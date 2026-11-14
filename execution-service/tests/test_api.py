from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from pymongo.errors import PyMongoError

from app.main import app
from app.services import execucao_service, health_service

client = TestClient(app)

COMANDO = {"tipo": "EXECUTAR_OS", "os_id": 1, "veiculo_placa": "ABC1D23", "servicos": ["Troca de Óleo"]}


@patch.object(execucao_service, "rabbitmq")
def test_fluxo_execucao_pela_api(mock_rabbit, db):
    with patch.object(execucao_service, "get_db", return_value=db):
        execucao_service.processar_comando(COMANDO)

    assert [e["os_id"] for e in client.get("/api/v1/execucao/fila").json()] == [1]

    assert "Em Diagnóstico" in client.patch("/api/v1/execucao/1/avancar").json()["message"]
    assert "Em Reparo" in client.patch("/api/v1/execucao/1/avancar").json()["message"]
    assert "Finalizada" in client.patch("/api/v1/execucao/1/avancar").json()["message"]

    dados = client.get("/api/v1/execucao/1").json()
    assert dados["status"] == "Finalizada"
    assert len(dados["historico"]) == 4
    assert client.get("/api/v1/execucao/fila").json() == []


@patch.object(execucao_service, "rabbitmq")
def test_falhar_pela_api(mock_rabbit, db):
    with patch.object(execucao_service, "get_db", return_value=db):
        execucao_service.processar_comando(COMANDO)

    assert client.patch("/api/v1/execucao/1/falhar?motivo=ab").status_code == 422
    response = client.patch("/api/v1/execucao/1/falhar?motivo=peça incompatível")

    assert response.status_code == 200
    assert mock_rabbit.publicar.call_args.args[1]["tipo"] == "EXECUCAO_FALHOU"


def test_health_live():
    assert client.get("/api/v1/health/live").json() == {"status": "ok"}


def test_health_ready_ok(db):
    assert client.get("/api/v1/health/ready").json() == {"status": "ok"}


def test_health_ready_mongo_fora():
    banco = Mock()
    banco.command.side_effect = PyMongoError("fora")

    assert health_service.verificar_readiness(banco) is False
