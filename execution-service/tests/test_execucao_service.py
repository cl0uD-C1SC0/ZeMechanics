import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.services import execucao_service
from app.repositories import ExecucaoRepository
from app.domain.enums.StatusExecucao import StatusExecucao

COMANDO = {"tipo": "EXECUTAR_OS", "os_id": 1, "veiculo_placa": "ABC1D23", "servicos": ["Troca de Óleo"]}


@pytest.fixture
def rabbit():
    with patch.object(execucao_service, "rabbitmq") as mock:
        yield mock


@pytest.fixture
def fila(db, rabbit):
    with patch.object(execucao_service, "get_db", return_value=db):
        execucao_service.processar_comando(COMANDO)
    rabbit.reset_mock()
    return db


# ── Comandos (RabbitMQ) ──────────────────────────────────────────────────────

def test_executar_os_entra_na_fila_e_avisa(db, rabbit):
    with patch.object(execucao_service, "get_db", return_value=db):
        execucao_service.processar_comando(COMANDO)

    assert ExecucaoRepository.get_execucao(1, db)["status"] == "Na Fila"
    rabbit.publicar.assert_called_once_with("os.events", {"tipo": "EXECUCAO_INICIADA", "os_id": 1})


def test_executar_os_repetido_nao_duplica(fila, rabbit):
    with patch.object(execucao_service, "get_db", return_value=fila):
        execucao_service.processar_comando(COMANDO)

    assert fila["execucoes"].count_documents({"os_id": 1}) == 1
    rabbit.publicar.assert_called_once()


def test_comando_desconhecido_e_ignorado(rabbit):
    execucao_service.processar_comando({"tipo": "QUALQUER", "os_id": 1})

    rabbit.publicar.assert_not_called()


# ── Ações do mecânico (HTTP) ─────────────────────────────────────────────────

def test_avancar_ate_finalizar_avisa_os_service(fila, rabbit):
    execucao_service.avancar_execucao(1, fila)
    execucao_service.avancar_execucao(1, fila)
    rabbit.publicar.assert_not_called()

    result = execucao_service.avancar_execucao(1, fila)

    assert "Finalizada" in result["message"]
    rabbit.publicar.assert_called_once_with("os.events", {"tipo": "EXECUCAO_FINALIZADA", "os_id": 1})


def test_finalizar_com_rabbitmq_fora_nao_muda_status(fila, rabbit):
    ExecucaoRepository.update_status(1, StatusExecucao.EM_REPARO, "reparo", fila)
    rabbit.publicar.side_effect = HTTPException(status_code=503, detail="RabbitMQ indisponível")

    with pytest.raises(HTTPException):
        execucao_service.avancar_execucao(1, fila)

    assert ExecucaoRepository.get_execucao(1, fila)["status"] == "Em Reparo"


def test_falhar_execucao_dispara_compensacao(fila, rabbit):
    result = execucao_service.falhar_execucao(1, "peça incompatível", fila)

    assert "estornado" in result["message"]
    rabbit.publicar.assert_called_once_with(
        "os.events", {"tipo": "EXECUCAO_FALHOU", "os_id": 1, "motivo": "peça incompatível"}
    )
    assert ExecucaoRepository.get_execucao(1, fila)["status"] == "Falhou"


def test_nao_avanca_execucao_encerrada(fila, rabbit):
    execucao_service.falhar_execucao(1, "sem peça", fila)

    with pytest.raises(HTTPException) as exc:
        execucao_service.avancar_execucao(1, fila)

    assert exc.value.status_code == 400


def test_execucao_inexistente(db):
    with pytest.raises(HTTPException) as exc:
        execucao_service.avancar_execucao(99, db)
    assert exc.value.status_code == 404

    with pytest.raises(HTTPException) as exc:
        execucao_service.consultar_execucao(99, db)
    assert exc.value.status_code == 404


def test_consultar_e_listar_fila(fila):
    assert execucao_service.consultar_execucao(1, fila)["veiculo_placa"] == "ABC1D23"
    assert [e["os_id"] for e in execucao_service.listar_fila(fila)] == [1]
