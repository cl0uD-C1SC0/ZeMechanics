import logging
from fastapi import HTTPException
from fastapi.responses import HTMLResponse

from app.database import SessionLocal
from app.repositories import OrcamentoRepository
from app.clients import payment_gateway
from app.messaging import rabbitmq
from app.services.EmailService import enviar_email_aprovacao
from app.domain.enums.StatusOrcamento import StatusOrcamento, StatusPagamento

# O billing é um PARTICIPANTE da Saga: recebe comandos do os-service
# (fila billing.commands) e responde com eventos (fila os.events).

logger = logging.getLogger("billing")


# ── Comandos vindos do os-service (RabbitMQ) ─────────────────────────────────

def processar_comando(comando):
    db = SessionLocal()
    try:
        if comando.get("tipo") == "GERAR_ORCAMENTO":
            gerar_orcamento(comando, db)
        elif comando.get("tipo") == "ESTORNAR_PAGAMENTO":
            estornar_pagamento(comando["os_id"], db)
        else:
            logger.warning(f"[billing] comando desconhecido ignorado: {comando}")
    finally:
        db.close()


def gerar_orcamento(comando, db):
    orcamento = OrcamentoRepository.get_orcamento_by_os(comando["os_id"], db)

    if not orcamento:  # idempotência: comando repetido não gera 2 orçamentos nem 2 e-mails
        orcamento = OrcamentoRepository.create_orcamento(comando, db)
        enviar_email_aprovacao(orcamento)

    rabbitmq.publicar("os.events", {"tipo": "ORCAMENTO_GERADO", "os_id": orcamento.os_id, "orcamento_id": orcamento.id})


def estornar_pagamento(os_id, db):
    orcamento = OrcamentoRepository.get_orcamento_by_os(os_id, db)

    if orcamento and orcamento.status == StatusOrcamento.APROVADO:
        pagamento = OrcamentoRepository.get_pagamento_aprovado(orcamento.id, db)
        estorno = payment_gateway.estornar_pagamento(pagamento.gateway_id)
        OrcamentoRepository.add_pagamento(orcamento, StatusPagamento.ESTORNADO, estorno["id"], db)
        OrcamentoRepository.update_status(orcamento, StatusOrcamento.ESTORNADO, db)

    if orcamento and orcamento.status == StatusOrcamento.ESTORNADO:
        rabbitmq.publicar("os.events", {"tipo": "PAGAMENTO_ESTORNADO", "os_id": os_id})
    else:
        logger.warning(f"[billing] estorno ignorado: OS {os_id} não tem pagamento aprovado")


# ── Ações do cliente (HTTP) ──────────────────────────────────────────────────

def _orcamento_aguardando(os_id, cliente_cpf, db):
    orcamento = OrcamentoRepository.get_orcamento_by_os(os_id, db)

    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado para esta OS")

    if orcamento.status != StatusOrcamento.AGUARDANDO_APROVACAO:
        raise HTTPException(status_code=400, detail=f"Orçamento não está aguardando aprovação (status: {orcamento.status})")

    if str(orcamento.cliente_cpf) != str(cliente_cpf):
        raise HTTPException(status_code=403, detail="CPF não autorizado")

    return orcamento


def aprovar_orcamento(os_id, cliente_cpf, db):
    orcamento = _orcamento_aguardando(os_id, cliente_cpf, db)

    pagamento = payment_gateway.processar_pagamento(orcamento.valor_total, f"Ze Mechanics - OS #{os_id}")

    if pagamento["status"] == "approved":
        OrcamentoRepository.add_pagamento(orcamento, StatusPagamento.APROVADO, pagamento["id"], db)
        OrcamentoRepository.update_status(orcamento, StatusOrcamento.APROVADO, db)
        rabbitmq.publicar("os.events", {"tipo": "PAGAMENTO_APROVADO", "os_id": os_id})
        return {"message": f"Orçamento aprovado e pagamento confirmado — OS {os_id} enviada para execução"}

    OrcamentoRepository.add_pagamento(orcamento, StatusPagamento.RECUSADO, pagamento["id"], db)
    OrcamentoRepository.update_status(orcamento, StatusOrcamento.PAGAMENTO_RECUSADO, db)
    rabbitmq.publicar("os.events", {"tipo": "PAGAMENTO_RECUSADO", "os_id": os_id, "motivo": pagamento["status_detail"]})
    return {"message": f"Pagamento recusado ({pagamento['status_detail']}) — OS {os_id} será cancelada"}


def reprovar_orcamento(os_id, cliente_cpf, db):
    orcamento = _orcamento_aguardando(os_id, cliente_cpf, db)

    OrcamentoRepository.update_status(orcamento, StatusOrcamento.REPROVADO, db)
    rabbitmq.publicar("os.events", {"tipo": "ORCAMENTO_REPROVADO", "os_id": os_id})
    return {"message": "Orçamento reprovado pelo cliente — Ordem de Serviço encerrada"}


def consultar_orcamento(os_id, db):
    orcamento = OrcamentoRepository.get_orcamento_by_os(os_id, db)
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado para esta OS")

    return {
        "orcamento_id": orcamento.id,
        "os_id": orcamento.os_id,
        "status": orcamento.status,
        "cliente": orcamento.cliente_nome,
        "itens": orcamento.itens,
        "valor_total": orcamento.valor_total,
        "pagamentos": [
            {"status": p.status, "valor": p.valor, "gateway_id": p.gateway_id, "data": p.criado_em}
            for p in orcamento.pagamentos
        ],
    }


def listar_orcamentos(db):
    orcamentos = OrcamentoRepository.get_all_orcamentos(db)
    if not orcamentos:
        raise HTTPException(status_code=404, detail="Nenhum orçamento foi gerado")
    return [{"os_id": o.os_id, "status": o.status, "valor_total": o.valor_total} for o in orcamentos]


def mostrar_aprovacao(os_id, cliente_cpf, db):
    orcamento = OrcamentoRepository.get_orcamento_by_os(os_id, db)
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado para esta OS")

    if orcamento.status != StatusOrcamento.AGUARDANDO_APROVACAO:
        return {"message": f"Este orçamento não está mais aguardando aprovação (status: {orcamento.status})"}

    pecas_html = "".join(
        f"<tr><td>{p['nome']}</td><td>{p['quantidade']}</td><td>R$ {p['valor']}</td></tr>"
        for p in orcamento.itens["pecas"]
    )
    servicos_html = "".join(
        f"<tr><td>{s['nome']}</td><td>R$ {s['valor']}</td></tr>"
        for s in orcamento.itens["servicos"]
    )

    return HTMLResponse(f"""
        <html>
        <body>
            <h2>OS #{os_id} — Aguardando Aprovação</h2>
            <p><b>Cliente:</b> {orcamento.cliente_nome}</p>

            <h3>Peças</h3>
            <table border="1">
                <tr><th>Nome</th><th>Quantidade</th><th>Valor</th></tr>
                {pecas_html}
            </table>

            <h3>Serviços</h3>
            <table border="1">
                <tr><th>Nome</th><th>Valor</th></tr>
                {servicos_html}
            </table>

            <h3>Total: R$ {orcamento.valor_total}</h3>

            <form method="post" action="/api/v1/orcamento/{os_id}/confirmar_aprovacao?cliente_cpf={cliente_cpf}">
                <button type="submit">✅ Aprovar e Pagar</button>
            </form>

            <form method="post" action="/api/v1/orcamento/{os_id}/reprovar?cliente_cpf={cliente_cpf}">
                <button type="submit">❌ Recusar Orçamento</button>
            </form>
        </body>
        </html>
    """)
