import pytest
from unittest.mock import patch, Mock

from app.services import saga_service
from app.domain.enums.StatusOS import StatusOS


def _os(status):
    os = Mock()
    os.id = 1
    os.status = status
    os.veiculo.placa = "ABC1D23"
    os.os_servicos = [Mock(nome="Troca de Óleo")]
    os.os_pecas = [Mock(peca_id=10, quantidade=2), Mock(peca_id=11, quantidade=1)]
    return os


@pytest.fixture
def mocks():
    with patch.object(saga_service, "OSRepository") as repo, \
         patch.object(saga_service, "rabbitmq") as rabbit, \
         patch.object(saga_service, "catalog_client") as catalog, \
         patch.object(saga_service, "SessionLocal") as session:
        yield Mock(repo=repo, rabbit=rabbit, catalog=catalog, session=session)


def test_evento_desconhecido_e_ignorado(mocks):
    saga_service.processar_evento({"tipo": "QUALQUER", "os_id": 1})
    mocks.session.assert_not_called()


def test_os_inexistente_e_ignorada(mocks):
    mocks.repo.get_specific_os.return_value = None

    saga_service.processar_evento({"tipo": "PAGAMENTO_APROVADO", "os_id": 99})

    mocks.rabbit.publicar.assert_not_called()
    mocks.session.return_value.close.assert_called_once()


def test_orcamento_gerado_registra_historico(mocks):
    mocks.repo.get_specific_os.return_value = _os(StatusOS.AGUARDANDO_APROVACAO)

    saga_service.processar_evento({"tipo": "ORCAMENTO_GERADO", "os_id": 1, "orcamento_id": 5})

    assert "Orçamento #5" in mocks.repo.add_historico.call_args.args[2]


def test_pagamento_aprovado_envia_para_execucao(mocks):
    mocks.repo.get_specific_os.return_value = _os(StatusOS.AGUARDANDO_APROVACAO)

    saga_service.processar_evento({"tipo": "PAGAMENTO_APROVADO", "os_id": 1})

    fila, mensagem = mocks.rabbit.publicar.call_args.args
    assert fila == "execution.commands"
    assert mensagem == {"tipo": "EXECUTAR_OS", "os_id": 1, "veiculo_placa": "ABC1D23", "servicos": ["Troca de Óleo"]}


def test_pagamento_aprovado_repetido_e_ignorado(mocks):
    mocks.repo.get_specific_os.return_value = _os(StatusOS.EM_EXECUCAO)

    saga_service.processar_evento({"tipo": "PAGAMENTO_APROVADO", "os_id": 1})

    mocks.rabbit.publicar.assert_not_called()


def test_execucao_iniciada_muda_status(mocks):
    mocks.repo.get_specific_os.return_value = _os(StatusOS.AGUARDANDO_APROVACAO)

    saga_service.processar_evento({"tipo": "EXECUCAO_INICIADA", "os_id": 1})

    assert mocks.repo.advance_os.call_args.args[1] == StatusOS.EM_EXECUCAO


def test_execucao_iniciada_fora_de_ordem_e_ignorada(mocks):
    mocks.repo.get_specific_os.return_value = _os(StatusOS.CANCELADA)

    saga_service.processar_evento({"tipo": "EXECUCAO_INICIADA", "os_id": 1})

    mocks.repo.advance_os.assert_not_called()


def test_execucao_finalizada_muda_status(mocks):
    mocks.repo.get_specific_os.return_value = _os(StatusOS.EM_EXECUCAO)

    saga_service.processar_evento({"tipo": "EXECUCAO_FINALIZADA", "os_id": 1})

    assert mocks.repo.advance_os.call_args.args[1] == StatusOS.FINALIZADA


def test_execucao_finalizada_fora_de_ordem_e_ignorada(mocks):
    mocks.repo.get_specific_os.return_value = _os(StatusOS.ENTREGUE)

    saga_service.processar_evento({"tipo": "EXECUCAO_FINALIZADA", "os_id": 1})

    mocks.repo.advance_os.assert_not_called()


def test_orcamento_reprovado_compensa_e_reprova(mocks):
    mocks.repo.get_specific_os.return_value = _os(StatusOS.AGUARDANDO_APROVACAO)

    saga_service.processar_evento({"tipo": "ORCAMENTO_REPROVADO", "os_id": 1})

    assert mocks.catalog.devolver_estoque.call_count == 2
    mocks.catalog.devolver_estoque.assert_any_call(10, 2)
    mocks.catalog.devolver_estoque.assert_any_call(11, 1)
    assert mocks.repo.advance_os.call_args.args[1] == StatusOS.REPROVADA


def test_pagamento_recusado_compensa_e_cancela(mocks):
    mocks.repo.get_specific_os.return_value = _os(StatusOS.AGUARDANDO_APROVACAO)

    saga_service.processar_evento({"tipo": "PAGAMENTO_RECUSADO", "os_id": 1, "motivo": "cartão recusado"})

    assert mocks.catalog.devolver_estoque.call_count == 2
    assert mocks.repo.advance_os.call_args.args[1] == StatusOS.CANCELADA
    assert "cartão recusado" in mocks.repo.advance_os.call_args.args[3]


def test_execucao_falhou_pede_estorno(mocks):
    mocks.repo.get_specific_os.return_value = _os(StatusOS.EM_EXECUCAO)

    saga_service.processar_evento({"tipo": "EXECUCAO_FALHOU", "os_id": 1, "motivo": "sem peça"})

    mocks.rabbit.publicar.assert_called_once_with("billing.commands", {"tipo": "ESTORNAR_PAGAMENTO", "os_id": 1})
    mocks.catalog.devolver_estoque.assert_not_called()


def test_execucao_falhou_em_os_encerrada_e_ignorada(mocks):
    mocks.repo.get_specific_os.return_value = _os(StatusOS.CANCELADA)

    saga_service.processar_evento({"tipo": "EXECUCAO_FALHOU", "os_id": 1})

    mocks.rabbit.publicar.assert_not_called()


def test_pagamento_estornado_compensa_e_cancela(mocks):
    mocks.repo.get_specific_os.return_value = _os(StatusOS.EM_EXECUCAO)

    saga_service.processar_evento({"tipo": "PAGAMENTO_ESTORNADO", "os_id": 1})

    assert mocks.catalog.devolver_estoque.call_count == 2
    assert mocks.repo.advance_os.call_args.args[1] == StatusOS.CANCELADA


def test_compensacao_repetida_nao_devolve_estoque_de_novo(mocks):
    mocks.repo.get_specific_os.return_value = _os(StatusOS.CANCELADA)

    saga_service.processar_evento({"tipo": "PAGAMENTO_ESTORNADO", "os_id": 1})

    mocks.catalog.devolver_estoque.assert_not_called()
    mocks.repo.advance_os.assert_not_called()
