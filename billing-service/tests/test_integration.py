import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base
from app.services import orcamento_service
from tests.conftest import engine, TestingSessionLocal


class FakeRabbit:
    def __init__(self):
        self.publicadas = []

    def publicar(self, fila, mensagem):
        self.publicadas.append((fila, mensagem))


RABBIT = FakeRabbit()

def comando(os_id, cpf):
    return {
        "tipo": "GERAR_ORCAMENTO",
        "os_id": os_id,
        "cliente": {"nome": "João", "email": "joao@mail.com", "cpf": cpf},
        "pecas": [{"nome": "Filtro", "quantidade": 2, "valor": 45.9}],
        "servicos": [{"nome": "Troca de Óleo", "valor": 120.0}],
        "total": 211.8,
    }


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with patch.object(orcamento_service, "rabbitmq", RABBIT), \
         patch.object(orcamento_service, "SessionLocal", TestingSessionLocal), \
         patch.object(orcamento_service, "enviar_email_aprovacao"):
        with TestClient(app) as c:
            yield c
    Base.metadata.drop_all(bind=engine)


def test_fluxo_aprovacao_pagamento_e_estorno(client):
    # 1. os-service pede o orçamento (mensagem chega pela fila billing.commands)
    orcamento_service.processar_comando(comando(1, "52998224725"))
    assert RABBIT.publicadas[-1] == ("os.events", {"tipo": "ORCAMENTO_GERADO", "os_id": 1, "orcamento_id": 1})

    # 2. cliente abre a página do e-mail e aprova
    assert "Aprovar e Pagar" in client.get("/api/v1/orcamento/1/aprovar?cliente_cpf=52998224725").text
    response = client.post("/api/v1/orcamento/1/confirmar_aprovacao?cliente_cpf=52998224725")
    assert response.status_code == 200
    assert RABBIT.publicadas[-1] == ("os.events", {"tipo": "PAGAMENTO_APROVADO", "os_id": 1})

    # 3. execução falhou: os-service pede o estorno (compensação)
    orcamento_service.processar_comando({"tipo": "ESTORNAR_PAGAMENTO", "os_id": 1})
    assert RABBIT.publicadas[-1] == ("os.events", {"tipo": "PAGAMENTO_ESTORNADO", "os_id": 1})

    dados = client.get("/api/v1/orcamento/1").json()
    assert dados["status"] == "Estornado"
    assert [p["status"] for p in dados["pagamentos"]] == ["Aprovado", "Estornado"]


def test_fluxo_reprovacao(client):
    orcamento_service.processar_comando(comando(2, "11144477735"))

    assert client.post("/api/v1/orcamento/2/reprovar?cliente_cpf=00000000000").status_code == 403
    assert client.post("/api/v1/orcamento/2/reprovar?cliente_cpf=11144477735").status_code == 200
    assert RABBIT.publicadas[-1] == ("os.events", {"tipo": "ORCAMENTO_REPROVADO", "os_id": 2})
    assert client.post("/api/v1/orcamento/2/confirmar_aprovacao?cliente_cpf=11144477735").status_code == 400


@patch.dict("os.environ", {"MOCK_PAGAMENTO_STATUS": "rejected"})
def test_fluxo_pagamento_recusado(client):
    orcamento_service.processar_comando(comando(3, "52998224725"))

    response = client.post("/api/v1/orcamento/3/confirmar_aprovacao?cliente_cpf=52998224725")

    assert "recusado" in response.json()["message"]
    assert RABBIT.publicadas[-1][1]["tipo"] == "PAGAMENTO_RECUSADO"
    assert client.get("/api/v1/orcamento/3").json()["status"] == "Pagamento Recusado"


def test_listar_orcamentos(client):
    assert len(client.get("/api/v1/orcamento/orcamentos").json()) == 3
