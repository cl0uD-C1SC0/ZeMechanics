from app.repositories.OrcamentoRepository import *
from app.domain.enums.StatusOrcamento import StatusOrcamento, StatusPagamento

COMANDO = {
    "tipo": "GERAR_ORCAMENTO",
    "os_id": 1,
    "cliente": {"nome": "João", "email": "joao@mail.com", "cpf": "52998224725"},
    "pecas": [{"nome": "Filtro", "quantidade": 2, "valor": 45.9}],
    "servicos": [{"nome": "Troca de Óleo", "valor": 120.0}],
    "total": 211.8,
}


def test_create_orcamento(db):
    orcamento = create_orcamento(COMANDO, db)

    assert orcamento.id is not None
    assert orcamento.os_id == 1
    assert orcamento.status == StatusOrcamento.AGUARDANDO_APROVACAO
    assert orcamento.itens["pecas"][0]["nome"] == "Filtro"
    assert orcamento.valor_total == 211.8


def test_get_orcamento_by_os(db):
    create_orcamento(COMANDO, db)

    assert get_orcamento_by_os(1, db) is not None
    assert get_orcamento_by_os(99, db) is None


def test_get_all_orcamentos(db):
    create_orcamento(COMANDO, db)
    create_orcamento({**COMANDO, "os_id": 2}, db)

    assert len(get_all_orcamentos(db)) == 2


def test_update_status(db):
    orcamento = create_orcamento(COMANDO, db)

    update_status(orcamento, StatusOrcamento.APROVADO, db)

    assert get_orcamento_by_os(1, db).status == StatusOrcamento.APROVADO


def test_pagamentos_sao_lancamentos_novos(db):
    orcamento = create_orcamento(COMANDO, db)

    add_pagamento(orcamento, StatusPagamento.APROVADO, "mock-1", db)
    add_pagamento(orcamento, StatusPagamento.ESTORNADO, "mock-1", db)

    assert [p.status for p in orcamento.pagamentos] == [StatusPagamento.APROVADO, StatusPagamento.ESTORNADO]
    assert get_pagamento_aprovado(orcamento.id, db).gateway_id == "mock-1"
    assert orcamento.pagamentos[0].valor == 211.8
