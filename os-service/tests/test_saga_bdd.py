"""
BDD da Saga da Ordem de Serviço (pytest-bdd).

O cenário está escrito em português em tests/features/saga_ordem_servico.feature.
Aqui ficam os "passos": o que cada frase do cenário faz no sistema.

O os-service roda de verdade (API + banco SQLite + orquestrador da Saga).
Os outros serviços são simulados nas bordas:
  - catalog-service -> FakeCatalog (o os-service só fala com ele via HTTP)
  - RabbitMQ        -> FakeRabbit  (guarda o que o os-service publicou)
  - billing/execution respondendo -> saga_service.processar_evento(...)
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pytest_bdd import scenarios, given, when, then, parsers

from app.main import app
from app.database import Base, get_db
from app.services import saga_service

scenarios("features/saga_ordem_servico.feature")

engine = create_engine("sqlite:///./test_bdd.db", connect_args={"check_same_thread": False})
SessionBDD = sessionmaker(autocommit=False, autoflush=False, bind=engine)

CPF = "52998224725"
PLACA = "BDD1A23"


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


class FakeRabbit:
    def __init__(self):
        self.publicadas = []

    def publicar(self, fila, mensagem):
        self.publicadas.append((fila, mensagem))


def _override_get_db():
    db = SessionBDD()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def oficina():
    """Um ambiente novo e limpo para cada cenário."""
    catalogo, rabbit = FakeCatalog(), FakeRabbit()
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = _override_get_db

    with patch("app.services.OSService.catalog_client", catalogo), \
         patch("app.services.OSService.rabbitmq", rabbit), \
         patch("app.services.saga_service.catalog_client", catalogo), \
         patch("app.services.saga_service.rabbitmq", rabbit), \
         patch("app.services.saga_service.SessionLocal", SessionBDD):
        with TestClient(app) as client:
            yield {"client": client, "catalogo": catalogo, "rabbit": rabbit, "os_id": None}

    Base.metadata.drop_all(bind=engine)


# ── Contexto ─────────────────────────────────────────────────────────────────

@given("um cliente com um veículo cadastrado")
def cliente_com_veiculo(oficina):
    client = oficina["client"]
    resposta = client.post("/api/v1/cliente/novo_cliente", json={
        "nome": "João Silva", "cpf": CPF, "endereco": "Rua X, 123",
        "telefone": "11999999999", "email": "joao@zemechanics.com",
    })
    assert resposta.status_code == 201
    cliente_id = int(resposta.json()["cliente_id"])

    resposta = client.post("/api/v1/veiculo/cadastrar_veiculo", json={
        "modelo": "Fit", "marca": "Honda", "placa": PLACA, "ano": "2014", "cliente_id": cliente_id,
    })
    assert resposta.status_code == 201


@given("uma OS com 2 filtros de óleo e uma troca de óleo")
def os_com_itens(oficina):
    client = oficina["client"]
    resposta = client.post("/api/v1/ordem_servico/nova_os", json={"cliente_cpf": int(CPF), "veiculo_placa": PLACA})
    assert resposta.status_code == 201
    oficina["os_id"] = int(resposta.json()["message"].split("ID: ")[-1])

    assert client.post(f"/api/v1/ordem_servico/{oficina['os_id']}/adicionar_peca/1?quantidade=2").status_code == 200
    assert client.post(f"/api/v1/ordem_servico/{oficina['os_id']}/adicionar_servico/1").status_code == 200


# ── Ações ────────────────────────────────────────────────────────────────────

@given("que a OS está aguardando aprovação")
@when("o atendente avança a OS até aguardar aprovação")
def avancar_ate_aprovacao(oficina):
    for _ in range(2):  # Recebida → Em Diagnóstico → Aguardando Aprovação
        assert oficina["client"].patch(f"/api/v1/ordem_servico/avancar/{oficina['os_id']}").status_code == 200


@when(parsers.parse('o {servico} informa "{evento}"'))
def servico_informa(oficina, servico, evento):
    # simula a resposta chegando na fila os.events
    extras = {"orcamento_id": 1} if evento == "ORCAMENTO_GERADO" else {"motivo": "teste BDD"}
    saga_service.processar_evento({"tipo": evento, "os_id": oficina["os_id"], **extras})


@when("o atendente entrega a OS")
def entregar(oficina):
    assert oficina["client"].patch(f"/api/v1/ordem_servico/avancar/{oficina['os_id']}").status_code == 200


# ── Verificações ─────────────────────────────────────────────────────────────

@given(parsers.parse("o estoque de filtros no catálogo é {quantidade:d}"))
@then(parsers.parse("o estoque de filtros no catálogo é {quantidade:d}"))
def estoque_do_catalogo(oficina, quantidade):
    assert oficina["catalogo"].pecas[1]["quantidade"] == quantidade


@then(parsers.parse('o billing-service recebe o comando "{comando}" com total de {total:f}'))
def billing_recebe_com_total(oficina, comando, total):
    fila, mensagem = oficina["rabbit"].publicadas[-1]
    assert fila == "billing.commands"
    assert mensagem["tipo"] == comando
    assert mensagem["total"] == pytest.approx(total)


@then(parsers.parse('o {servico} recebe o comando "{comando}"'))
def servico_recebe(oficina, servico, comando):
    fila_esperada = {"billing-service": "billing.commands", "execution-service": "execution.commands"}[servico]
    fila, mensagem = oficina["rabbit"].publicadas[-1]
    assert fila == fila_esperada
    assert mensagem["tipo"] == comando


@then(parsers.parse('a OS fica "{status}"'))
def os_fica(oficina, status):
    resposta = oficina["client"].get(f"/api/v1/ordem_servico/consultar/{oficina['os_id']}")
    assert resposta.json()["status"] == status
