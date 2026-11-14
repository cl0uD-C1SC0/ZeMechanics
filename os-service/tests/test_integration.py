import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.services import saga_service

from app.domain.models.Cliente_model import Cliente
from app.domain.models.Veiculo_model import Veiculo
from app.domain.models.OrdemServico_model import OrdemDeServico, OSPeca, OSServico

# ── BANCO DE DADOS DE TESTE (SQLite) ───────────────────────────────────────────
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── CATALOG-SERVICE SIMULADO (o os-service só fala com ele via HTTP) ──────────
class FakeCatalog:
    def __init__(self):
        self.pecas = {1: {"id": 1, "nome": "Filtro de Óleo", "preco": 45.90, "quantidade": 20}}
        self.servicos = {1: {"id": 1, "nome": "Troca de Óleo", "preco": 120.00}}

    def consultar_peca(self, peca_id):
        return self.pecas[peca_id]

    def baixar_estoque(self, peca_id, quantidade):
        self.pecas[peca_id]["quantidade"] -= quantidade

    def devolver_estoque(self, peca_id, quantidade):
        self.pecas[peca_id]["quantidade"] += quantidade

    def consultar_servico(self, servico_id):
        return self.servicos[servico_id]


# ── RABBITMQ SIMULADO (guarda o que foi publicado) ─────────────────────────────
class FakeRabbit:
    def __init__(self):
        self.publicadas = []

    def publicar(self, fila, mensagem):
        self.publicadas.append((fila, mensagem))

    def ultima(self):
        return self.publicadas[-1]


CATALOGO = FakeCatalog()
RABBIT = FakeRabbit()


def evento(tipo, os_id, **extra):
    """Simula uma resposta chegando na fila os.events (vinda do billing/execution)."""
    saga_service.processar_evento({"tipo": tipo, "os_id": int(os_id), **extra})


# ── FIXTURE PRINCIPAL ──────────────────────────────────────────────────────────
# Autenticação fica no AWS API Gateway + Lambda (Fase 3), não nos serviços.
@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)

    with patch("app.services.OSService.catalog_client", CATALOGO),          patch("app.services.OSService.rabbitmq", RABBIT),          patch("app.services.saga_service.catalog_client", CATALOGO),          patch("app.services.saga_service.rabbitmq", RABBIT),          patch("app.services.saga_service.SessionLocal", TestingSessionLocal):
        with TestClient(app) as c:
            yield c

    Base.metadata.drop_all(bind=engine)


# ── DADOS DO TESTE ─────────────────────────────────────────────────────────────
CLIENTE_DATA = {
    "nome": "João Silva",
    "cpf": "52998224725",
    "endereco": "Rua X, 123",
    "telefone": "11999999999",
    "email": "joao@zemechanics.com",
}

VEICULO_DATA = {
    "modelo": "Fit",
    "marca": "Honda",
    "placa": "FGV1412",
    "ano": "2014",
    "cliente_id": None,  # preenchido dinamicamente
}

# ── TESTE DE INTEGRAÇÃO: FLUXO PRINCIPAL ──────────────────────────────────────
class TestFluxoPrincipal:

    cliente_id = None
    veiculo_id = None
    peca_id    = 1   # existe no FakeCatalog
    servico_id = 1   # existe no FakeCatalog
    os_id      = None

    def test_01_cadastrar_cliente(self, client):
        response = client.post("/api/v1/cliente/novo_cliente", json=CLIENTE_DATA)

        assert response.status_code == 201
        assert "cliente_id" in response.json()

        TestFluxoPrincipal.cliente_id = int(response.json()["cliente_id"])

    def test_02_cadastrar_veiculo(self, client):
        veiculo = {**VEICULO_DATA, "cliente_id": self.cliente_id}
        response = client.post("/api/v1/veiculo/cadastrar_veiculo", json=veiculo)

        assert response.status_code == 201
        assert "Veiculo cadastrado com sucesso" in response.json()["message"]

        veiculo_id = int(response.json()["message"].split("ID: ")[-1])
        TestFluxoPrincipal.veiculo_id = veiculo_id

    def test_05_criar_os(self, client):
        response = client.post(
            "/api/v1/ordem_servico/nova_os",
            json={
                "cliente_cpf": int(CLIENTE_DATA["cpf"]),
                "veiculo_placa": VEICULO_DATA["placa"],
            },
        )

        assert response.status_code == 201
        assert "Nova Ordem de Serviço foi criada" in response.json()["message"]

        os_id = response.json()["message"].split("ID: ")[-1]
        TestFluxoPrincipal.os_id = os_id

    def test_06_adicionar_peca_na_os(self, client):
        response = client.post(
            f"/api/v1/ordem_servico/{self.os_id}/adicionar_peca/{self.peca_id}?quantidade=2"
        )

        assert response.status_code == 200
        assert "message" in response.json()

    def test_07_adicionar_servico_na_os(self, client):
        response = client.post(
            f"/api/v1/ordem_servico/{self.os_id}/adicionar_servico/{self.servico_id}"
        )

        assert response.status_code == 200
        assert "message" in response.json()

    def test_08_avancar_os_para_em_diagnostico(self, client):
        response = client.patch(f"/api/v1/ordem_servico/avancar/{self.os_id}")

        assert response.status_code == 200
        assert "Em Diagnóstico" in response.json()["message"]

    def test_09_avancar_para_aguardando_aprovacao_pede_orcamento(self, client):
        response = client.patch(f"/api/v1/ordem_servico/avancar/{self.os_id}")

        assert response.status_code == 200
        assert "Aguardando Aprovação" in response.json()["message"]

        fila, mensagem = RABBIT.ultima()
        assert fila == "billing.commands"
        assert mensagem["tipo"] == "GERAR_ORCAMENTO"
        assert mensagem["total"] == round(45.90 * 2 + 120.00, 2)

    def test_10_saga_pagamento_aprovado_envia_para_execucao(self, client):
        evento("ORCAMENTO_GERADO", self.os_id, orcamento_id=1)
        evento("PAGAMENTO_APROVADO", self.os_id)

        fila, mensagem = RABBIT.ultima()
        assert fila == "execution.commands"
        assert mensagem["tipo"] == "EXECUTAR_OS"

    def test_11_saga_execucao_iniciada_e_finalizada(self, client):
        evento("EXECUCAO_INICIADA", self.os_id)
        assert client.get(f"/api/v1/ordem_servico/consultar/{self.os_id}").json()["status"] == "Em Execução"

        evento("EXECUCAO_FINALIZADA", self.os_id)
        assert client.get(f"/api/v1/ordem_servico/consultar/{self.os_id}").json()["status"] == "Finalizada"

    def test_12_avancar_os_para_entregue(self, client):
        response = client.patch(f"/api/v1/ordem_servico/avancar/{self.os_id}")

        assert response.status_code == 200
        assert "Entregue" in response.json()["message"]

    def test_13_consultar_os_entregue(self, client):
        response = client.get(f"/api/v1/ordem_servico/consultar/{self.os_id}")

        assert response.status_code == 200
        dados = response.json()
        assert dados["status"] == "Entregue"
        assert len(dados["pecas"]) > 0
        assert len(dados["servicos"]) > 0
        assert dados["Total"] == round(45.90 * 2 + 120.00, 2)

    def test_14_historico_conta_a_saga(self, client):
        historico = client.get(f"/api/v1/ordem_servico/historico/{self.os_id}").json()

        assert [h["status"] for h in historico][-4:] == ["Aguardando Aprovação", "Em Execução", "Finalizada", "Entregue"]
        assert any("Orçamento #1" in h["evento"] for h in historico)


# ── TESTE DE INTEGRAÇÃO: SAGA COM FALHA NA EXECUÇÃO (COMPENSAÇÃO) ─────────────
class TestSagaCompensacao:

    os_id = None

    def test_01_prepara_os_aguardando_aprovacao(self, client):
        client.post("/api/v1/cliente/novo_cliente", json={**CLIENTE_DATA, "cpf": "11144477735", "email": "maria@zemechanics.com"})
        cliente_id = client.get("/api/v1/cliente/11144477735").json()["id"]
        client.post("/api/v1/veiculo/cadastrar_veiculo", json={**VEICULO_DATA, "placa": "SAG4A00", "cliente_id": cliente_id})
        response = client.post("/api/v1/ordem_servico/nova_os", json={"cliente_cpf": 11144477735, "veiculo_placa": "SAG4A00"})
        TestSagaCompensacao.os_id = response.json()["message"].split("ID: ")[-1].strip()

        estoque_antes = CATALOGO.pecas[1]["quantidade"]
        client.post(f"/api/v1/ordem_servico/{self.os_id}/adicionar_peca/1?quantidade=3")
        assert CATALOGO.pecas[1]["quantidade"] == estoque_antes - 3

        client.patch(f"/api/v1/ordem_servico/avancar/{self.os_id}")
        client.patch(f"/api/v1/ordem_servico/avancar/{self.os_id}")
        assert client.get(f"/api/v1/ordem_servico/consultar/{self.os_id}").json()["status"] == "Aguardando Aprovação"

    def test_02_execucao_falha_pede_estorno(self, client):
        evento("PAGAMENTO_APROVADO", self.os_id)
        evento("EXECUCAO_INICIADA", self.os_id)
        evento("EXECUCAO_FALHOU", self.os_id, motivo="peça incompatível")

        fila, mensagem = RABBIT.ultima()
        assert fila == "billing.commands"
        assert mensagem == {"tipo": "ESTORNAR_PAGAMENTO", "os_id": int(self.os_id)}

    def test_03_estorno_confirmado_devolve_estoque_e_cancela(self, client):
        estoque_antes = CATALOGO.pecas[1]["quantidade"]

        evento("PAGAMENTO_ESTORNADO", self.os_id)

        assert CATALOGO.pecas[1]["quantidade"] == estoque_antes + 3
        assert client.get(f"/api/v1/ordem_servico/consultar/{self.os_id}").json()["status"] == "Cancelada"

    def test_04_evento_repetido_nao_compensa_duas_vezes(self, client):
        estoque_antes = CATALOGO.pecas[1]["quantidade"]

        evento("PAGAMENTO_ESTORNADO", self.os_id)

        assert CATALOGO.pecas[1]["quantidade"] == estoque_antes
