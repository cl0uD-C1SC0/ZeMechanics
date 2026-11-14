from app.domain.models.Orcamento_model import Orcamento as OrcamentoModel
from app.domain.models.Orcamento_model import Pagamento as PagamentoModel
from app.domain.enums.StatusOrcamento import StatusPagamento


def create_orcamento(comando, db):
    orcamento = OrcamentoModel(
        os_id=comando["os_id"],
        cliente_nome=comando["cliente"]["nome"],
        cliente_email=comando["cliente"]["email"],
        cliente_cpf=comando["cliente"]["cpf"],
        itens={"pecas": comando["pecas"], "servicos": comando["servicos"]},
        valor_total=comando["total"],
    )
    db.add(orcamento)
    db.commit()
    db.refresh(orcamento)
    return orcamento


def get_orcamento_by_os(os_id, db):
    return db.query(OrcamentoModel).filter(OrcamentoModel.os_id == os_id).first()


def get_all_orcamentos(db):
    return db.query(OrcamentoModel).all()


def update_status(orcamento, status, db):
    orcamento.status = status
    db.commit()
    db.refresh(orcamento)
    return orcamento


def add_pagamento(orcamento, status, gateway_id, db):
    pagamento = PagamentoModel(
        orcamento_id=orcamento.id,
        valor=orcamento.valor_total,
        status=status,
        gateway_id=gateway_id,
    )
    db.add(pagamento)
    db.commit()
    db.refresh(pagamento)
    return pagamento


def get_pagamento_aprovado(orcamento_id, db):
    return (
        db.query(PagamentoModel)
        .filter(PagamentoModel.orcamento_id == orcamento_id, PagamentoModel.status == StatusPagamento.APROVADO)
        .first()
    )
