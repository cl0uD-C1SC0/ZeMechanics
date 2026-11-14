import logging
from fastapi import HTTPException

from app.database import get_db
from app.repositories import ExecucaoRepository
from app.messaging import rabbitmq
from app.domain.enums.StatusExecucao import StatusExecucao, TRANSICAO_STATUS, STATUS_ABERTOS

# O execution-service é um PARTICIPANTE da Saga: recebe EXECUTAR_OS
# (fila execution.commands) e avisa o os-service (fila os.events) quando a OS
# entrou na fila, foi finalizada ou quando a execução falhou.

logger = logging.getLogger("execution")


# ── Comandos vindos do os-service (RabbitMQ) ─────────────────────────────────

def processar_comando(comando):
    if comando.get("tipo") != "EXECUTAR_OS":
        logger.warning(f"[execution] comando desconhecido ignorado: {comando}")
        return

    db = get_db()
    if not ExecucaoRepository.get_execucao(comando["os_id"], db):  # idempotência
        ExecucaoRepository.create_execucao(comando, db)

    rabbitmq.publicar("os.events", {"tipo": "EXECUCAO_INICIADA", "os_id": comando["os_id"]})


# ── Ações do mecânico (HTTP) ─────────────────────────────────────────────────

def _execucao_aberta(os_id, db):
    execucao = ExecucaoRepository.get_execucao(os_id, db)

    if not execucao:
        raise HTTPException(status_code=404, detail="OS não encontrada na fila de execução")

    if execucao["status"] not in [s.value for s in STATUS_ABERTOS]:
        raise HTTPException(status_code=400, detail=f"Execução já encerrada (status: {execucao['status']})")

    return execucao


def avancar_execucao(os_id, db):
    execucao = _execucao_aberta(os_id, db)
    proximo_status = TRANSICAO_STATUS[StatusExecucao(execucao["status"])]

    if proximo_status == StatusExecucao.FINALIZADA:
        # Publica ANTES de gravar: se o RabbitMQ estiver fora, nada muda (503)
        rabbitmq.publicar("os.events", {"tipo": "EXECUCAO_FINALIZADA", "os_id": os_id})

    ExecucaoRepository.update_status(os_id, proximo_status, "Avanço do mecânico", db)
    return {"message": f"Execução da OS {os_id} avançada para: {proximo_status.value}"}


def falhar_execucao(os_id, motivo, db):
    _execucao_aberta(os_id, db)

    # SAGA: avisa o os-service, que dispara as compensações (estorno + estoque)
    rabbitmq.publicar("os.events", {"tipo": "EXECUCAO_FALHOU", "os_id": os_id, "motivo": motivo})

    ExecucaoRepository.update_status(os_id, StatusExecucao.FALHOU, f"Falha: {motivo}", db)
    return {"message": f"Execução da OS {os_id} marcada como falha — o pagamento será estornado e a OS cancelada"}


def consultar_execucao(os_id, db):
    execucao = ExecucaoRepository.get_execucao(os_id, db)
    if not execucao:
        raise HTTPException(status_code=404, detail="OS não encontrada na fila de execução")
    return execucao


def listar_fila(db):
    return ExecucaoRepository.get_fila(db)
