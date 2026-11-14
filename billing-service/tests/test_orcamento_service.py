import pytest
from unittest.mock import patch, Mock
from fastapi import HTTPException

from app.services import orcamento_service
from app.domain.enums.StatusOrcamento import StatusOrcamento, StatusPagamento

COMANDO = {
    "tipo": "GERAR_ORCAMENTO",
    "os_id": 1,
    "cliente": {"nome": "João", "email": "joao@mail.com", "cpf": "52998224725"},
    "pecas": [{"nome": "Filtro", "quantidade": 2, "valor": 45.9}],
    "servicos": [{"nome": "Troca de Óleo", "valor": 120.0}],
    "total": 211.8,
}


def _orcamento(status=StatusOrcamento.AGUARDANDO_APROVACAO, cpf="52998224725"):
    return Mock(
        id=3, os_id=1, status=status, cliente_cpf=cpf, cliente_nome="João", valor_total=211.8,
        itens={"pecas": COMANDO["pecas"], "servicos": COMANDO["servicos"]}, pagamentos=[],
    )


@pytest.fixture
def mocks():
    with patch.object(orcamento_service, "OrcamentoRepository") as repo, \
         patch.object(orcamento_service, "rabbitmq") as rabbit, \
         patch.object(orcamento_service, "payment_gateway") as gateway, \
         patch.object(orcamento_service, "enviar_email_aprovacao") as email, \
         patch.object(orcamento_service, "SessionLocal") as session:
        yield Mock(repo=repo, rabbit=rabbit, gateway=gateway, email=email, session=session)


# ── Comandos (RabbitMQ) ──────────────────────────────────────────────────────

def test_gerar_orcamento_cria_envia_email_e_responde(mocks):
    mocks.repo.get_orcamento_by_os.return_value = None
    mocks.repo.create_orcamento.return_value = _orcamento()

    orcamento_service.processar_comando(COMANDO)

    mocks.repo.create_orcamento.assert_called_once()
    mocks.email.assert_called_once()
    mocks.rabbit.publicar.assert_called_once_with("os.events", {"tipo": "ORCAMENTO_GERADO", "os_id": 1, "orcamento_id": 3})
    mocks.session.return_value.close.assert_called_once()


def test_gerar_orcamento_repetido_nao_duplica(mocks):
    mocks.repo.get_orcamento_by_os.return_value = _orcamento()

    orcamento_service.processar_comando(COMANDO)

    mocks.repo.create_orcamento.assert_not_called()
    mocks.email.assert_not_called()
    mocks.rabbit.publicar.assert_called_once()


def test_comando_desconhecido_e_ignorado(mocks):
    orcamento_service.processar_comando({"tipo": "QUALQUER", "os_id": 1})

    mocks.rabbit.publicar.assert_not_called()


def test_estornar_pagamento_aprovado(mocks):
    orcamento = _orcamento(StatusOrcamento.APROVADO)
    mocks.repo.get_orcamento_by_os.return_value = orcamento
    mocks.repo.get_pagamento_aprovado.return_value = Mock(gateway_id="mock-1")
    mocks.gateway.estornar_pagamento.return_value = {"id": "mock-1", "status": "refunded"}
    mocks.repo.update_status.side_effect = lambda o, status, db: setattr(o, "status", status)

    orcamento_service.processar_comando({"tipo": "ESTORNAR_PAGAMENTO", "os_id": 1})

    mocks.gateway.estornar_pagamento.assert_called_once_with("mock-1")
    mocks.repo.add_pagamento.assert_called_once_with(orcamento, StatusPagamento.ESTORNADO, "mock-1", mocks.session.return_value)
    mocks.rabbit.publicar.assert_called_once_with("os.events", {"tipo": "PAGAMENTO_ESTORNADO", "os_id": 1})


def test_estorno_repetido_so_responde_de_novo(mocks):
    mocks.repo.get_orcamento_by_os.return_value = _orcamento(StatusOrcamento.ESTORNADO)

    orcamento_service.processar_comando({"tipo": "ESTORNAR_PAGAMENTO", "os_id": 1})

    mocks.gateway.estornar_pagamento.assert_not_called()
    mocks.rabbit.publicar.assert_called_once_with("os.events", {"tipo": "PAGAMENTO_ESTORNADO", "os_id": 1})


def test_estorno_sem_pagamento_aprovado_e_ignorado(mocks):
    mocks.repo.get_orcamento_by_os.return_value = _orcamento(StatusOrcamento.AGUARDANDO_APROVACAO)

    orcamento_service.processar_comando({"tipo": "ESTORNAR_PAGAMENTO", "os_id": 1})

    mocks.gateway.estornar_pagamento.assert_not_called()
    mocks.rabbit.publicar.assert_not_called()


# ── Ações do cliente (HTTP) ──────────────────────────────────────────────────

def test_aprovar_com_pagamento_aprovado(mocks):
    orcamento = _orcamento()
    mocks.repo.get_orcamento_by_os.return_value = orcamento
    mocks.gateway.processar_pagamento.return_value = {"id": "mock-1", "status": "approved", "status_detail": "accredited"}

    result = orcamento_service.aprovar_orcamento(1, "52998224725", Mock())

    assert "pagamento confirmado" in result["message"]
    assert mocks.repo.add_pagamento.call_args.args[1] == StatusPagamento.APROVADO
    assert mocks.repo.update_status.call_args.args[1] == StatusOrcamento.APROVADO
    mocks.rabbit.publicar.assert_called_once_with("os.events", {"tipo": "PAGAMENTO_APROVADO", "os_id": 1})


def test_aprovar_com_pagamento_recusado(mocks):
    mocks.repo.get_orcamento_by_os.return_value = _orcamento()
    mocks.gateway.processar_pagamento.return_value = {"id": "mock-2", "status": "rejected", "status_detail": "cc_rejected_other_reason"}

    result = orcamento_service.aprovar_orcamento(1, "52998224725", Mock())

    assert "recusado" in result["message"]
    assert mocks.repo.add_pagamento.call_args.args[1] == StatusPagamento.RECUSADO
    assert mocks.repo.update_status.call_args.args[1] == StatusOrcamento.PAGAMENTO_RECUSADO
    mocks.rabbit.publicar.assert_called_once_with(
        "os.events", {"tipo": "PAGAMENTO_RECUSADO", "os_id": 1, "motivo": "cc_rejected_other_reason"}
    )


def test_reprovar_orcamento(mocks):
    mocks.repo.get_orcamento_by_os.return_value = _orcamento()

    result = orcamento_service.reprovar_orcamento(1, "52998224725", Mock())

    assert "reprovado" in result["message"]
    assert mocks.repo.update_status.call_args.args[1] == StatusOrcamento.REPROVADO
    mocks.rabbit.publicar.assert_called_once_with("os.events", {"tipo": "ORCAMENTO_REPROVADO", "os_id": 1})


def test_aprovar_orcamento_inexistente(mocks):
    mocks.repo.get_orcamento_by_os.return_value = None

    with pytest.raises(HTTPException) as exc:
        orcamento_service.aprovar_orcamento(1, "52998224725", Mock())

    assert exc.value.status_code == 404


def test_aprovar_orcamento_ja_aprovado(mocks):
    mocks.repo.get_orcamento_by_os.return_value = _orcamento(StatusOrcamento.APROVADO)

    with pytest.raises(HTTPException) as exc:
        orcamento_service.aprovar_orcamento(1, "52998224725", Mock())

    assert exc.value.status_code == 400
    mocks.gateway.processar_pagamento.assert_not_called()


def test_aprovar_com_cpf_errado(mocks):
    mocks.repo.get_orcamento_by_os.return_value = _orcamento()

    with pytest.raises(HTTPException) as exc:
        orcamento_service.reprovar_orcamento(1, "00000000000", Mock())

    assert exc.value.status_code == 403
    mocks.rabbit.publicar.assert_not_called()


def test_consultar_orcamento(mocks):
    orcamento = _orcamento(StatusOrcamento.APROVADO)
    orcamento.pagamentos = [Mock(status="Aprovado", valor=211.8, gateway_id="mock-1", criado_em="2026-11-14")]
    mocks.repo.get_orcamento_by_os.return_value = orcamento

    result = orcamento_service.consultar_orcamento(1, Mock())

    assert result["status"] == StatusOrcamento.APROVADO
    assert result["pagamentos"][0]["gateway_id"] == "mock-1"


def test_consultar_orcamento_inexistente(mocks):
    mocks.repo.get_orcamento_by_os.return_value = None

    with pytest.raises(HTTPException) as exc:
        orcamento_service.consultar_orcamento(1, Mock())

    assert exc.value.status_code == 404


def test_listar_orcamentos(mocks):
    mocks.repo.get_all_orcamentos.return_value = [_orcamento()]

    assert orcamento_service.listar_orcamentos(Mock()) == [
        {"os_id": 1, "status": StatusOrcamento.AGUARDANDO_APROVACAO, "valor_total": 211.8}
    ]


def test_listar_orcamentos_vazio(mocks):
    mocks.repo.get_all_orcamentos.return_value = []

    with pytest.raises(HTTPException) as exc:
        orcamento_service.listar_orcamentos(Mock())

    assert exc.value.status_code == 404


def test_mostrar_aprovacao_html(mocks):
    mocks.repo.get_orcamento_by_os.return_value = _orcamento()

    response = orcamento_service.mostrar_aprovacao(1, "52998224725", Mock())

    corpo = response.body.decode()
    assert "OS #1 —" in corpo
    assert "Filtro" in corpo
    assert "/api/v1/orcamento/1/confirmar_aprovacao?cliente_cpf=52998224725" in corpo
    assert "/api/v1/orcamento/1/reprovar?cliente_cpf=52998224725" in corpo


def test_mostrar_aprovacao_ja_respondida(mocks):
    mocks.repo.get_orcamento_by_os.return_value = _orcamento(StatusOrcamento.REPROVADO)

    result = orcamento_service.mostrar_aprovacao(1, "52998224725", Mock())

    assert "não está mais aguardando" in result["message"]


def test_mostrar_aprovacao_inexistente(mocks):
    mocks.repo.get_orcamento_by_os.return_value = None

    with pytest.raises(HTTPException) as exc:
        orcamento_service.mostrar_aprovacao(1, "52998224725", Mock())

    assert exc.value.status_code == 404
