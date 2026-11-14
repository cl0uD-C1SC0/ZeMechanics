import logging

from app.database import SessionLocal
from app.repositories import OSRepository
from app.clients import catalog_client
from app.messaging import rabbitmq
from app.domain.enums.StatusOS import StatusOS, STATUS_ENCERRADOS

# ─────────────────────────────────────────────────────────────────────────────
# SAGA ORQUESTRADA — o os-service é o "maestro" do fluxo da OS.
#
# Ele pede (fila billing.commands / execution.commands) e escuta as respostas
# (fila os.events). Para cada resposta decide o próximo passo — ou, se algo
# falhou, dispara as COMPENSAÇÕES (desfaz o que já foi feito).
#
#   Caminho feliz:
#     /avancar → GERAR_ORCAMENTO ──> billing
#                ORCAMENTO_GERADO <── billing   (e-mail enviado ao cliente)
#                PAGAMENTO_APROVADO <── billing (cliente aprovou + pagou)
#     EXECUTAR_OS ──> execution
#                EXECUCAO_INICIADA <── execution  → OS "Em Execução"
#                EXECUCAO_FINALIZADA <── execution → OS "Finalizada"
#
#   Falhas e compensações:
#     ORCAMENTO_REPROVADO → devolve peças ao estoque  → OS "Reprovada"
#     PAGAMENTO_RECUSADO  → devolve peças ao estoque  → OS "Cancelada"
#     EXECUCAO_FALHOU     → pede ESTORNAR_PAGAMENTO ao billing
#     PAGAMENTO_ESTORNADO → devolve peças ao estoque  → OS "Cancelada"
#
# Idempotência: cada passo confere o status atual da OS antes de agir, então
# uma mensagem repetida não faz nada duas vezes.
# ─────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger("saga")


def processar_evento(evento):
    handler = HANDLERS.get(evento.get("tipo"))
    if not handler:
        logger.warning(f"[saga] evento desconhecido ignorado: {evento}")
        return

    db = SessionLocal()
    try:
        os = OSRepository.get_specific_os(evento["os_id"], db)
        if not os:
            logger.warning(f"[saga] OS {evento['os_id']} não encontrada, evento ignorado")
            return
        handler(os, evento, db)
    finally:
        db.close()


# ── Caminho feliz ────────────────────────────────────────────────────────────

def orcamento_gerado(os, evento, db):
    OSRepository.add_historico(os.id, os.status, f"Orçamento #{evento['orcamento_id']} gerado e enviado ao cliente", db)


def pagamento_aprovado(os, evento, db):
    if os.status != StatusOS.AGUARDANDO_APROVACAO:
        return

    rabbitmq.publicar("execution.commands", {
        "tipo": "EXECUTAR_OS",
        "os_id": os.id,
        "veiculo_placa": os.veiculo.placa,
        "servicos": [s.nome for s in os.os_servicos],
    })
    OSRepository.add_historico(os.id, os.status, "Pagamento aprovado — OS enviada para a fila de execução", db)


def execucao_iniciada(os, evento, db):
    if os.status != StatusOS.AGUARDANDO_APROVACAO:
        return
    OSRepository.advance_os(os, StatusOS.EM_EXECUCAO, db, "Execução iniciada")


def execucao_finalizada(os, evento, db):
    if os.status != StatusOS.EM_EXECUCAO:
        return
    OSRepository.advance_os(os, StatusOS.FINALIZADA, db, "Execução finalizada")


# ── Falhas e compensações ────────────────────────────────────────────────────

def orcamento_reprovado(os, evento, db):
    compensar(os, StatusOS.REPROVADA, "Cliente reprovou o orçamento", db)


def pagamento_recusado(os, evento, db):
    compensar(os, StatusOS.CANCELADA, f"Pagamento recusado ({evento.get('motivo', 'sem motivo')})", db)


def execucao_falhou(os, evento, db):
    if os.status in STATUS_ENCERRADOS:
        return

    rabbitmq.publicar("billing.commands", {"tipo": "ESTORNAR_PAGAMENTO", "os_id": os.id})
    OSRepository.add_historico(
        os.id, os.status, f"Execução falhou ({evento.get('motivo', 'sem motivo')}) — estorno solicitado", db
    )


def pagamento_estornado(os, evento, db):
    compensar(os, StatusOS.CANCELADA, "Pagamento estornado", db)


def compensar(os, status_final, motivo, db):
    if os.status in STATUS_ENCERRADOS:
        return

    for peca in os.os_pecas:
        catalog_client.devolver_estoque(peca.peca_id, peca.quantidade)

    OSRepository.advance_os(
        os, status_final, db, f"{motivo} — {len(os.os_pecas)} peça(s) devolvida(s) ao estoque"
    )


HANDLERS = {
    "ORCAMENTO_GERADO": orcamento_gerado,
    "PAGAMENTO_APROVADO": pagamento_aprovado,
    "EXECUCAO_INICIADA": execucao_iniciada,
    "EXECUCAO_FINALIZADA": execucao_finalizada,
    "ORCAMENTO_REPROVADO": orcamento_reprovado,
    "PAGAMENTO_RECUSADO": pagamento_recusado,
    "EXECUCAO_FALHOU": execucao_falhou,
    "PAGAMENTO_ESTORNADO": pagamento_estornado,
}
