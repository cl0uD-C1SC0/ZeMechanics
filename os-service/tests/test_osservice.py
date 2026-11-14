import pytest
from unittest.mock import patch, Mock
from fastapi import HTTPException

from app.services.OSService import (
    criar_nova_os,
    criar_os_completa,
    consultar_os,
    avancar_os,
    consultar_historico,
    montar_pedido_orcamento,
    listar_todas_os,
    atualizar_os,
    remover_os,
    adicionar_peca_os,
    remover_peca_os,
    adicionar_servico_os,
    remover_servico_os
)
from app.schemas.OrdemServicoSchema import OSCompletaSchema, VeiculoOSCompletaSchema, PecaOSCompletaSchema
from app.schemas.cliente_schema import ClienteSchema


def _dados_os_completa(pecas=None, servicos=None):
    return OSCompletaSchema(
        cliente=ClienteSchema(
            nome="Jose Silva",
            cpf="12345678901",
            endereco="Rua X, 123",
            telefone="11999999999",
            email="jose@mail.com",
        ),
        veiculo=VeiculoOSCompletaSchema(
            modelo="Civic", marca="Honda", placa="ABC1D23", ano="2020"
        ),
        pecas=pecas or [],
        servicos=servicos or [],
    )

@patch("app.services.OSService.OSRepository")
@patch("app.services.OSService.veiculo_service")
@patch("app.services.OSService.cliente_service")
def test_criar_os_sucesso(mock_cliente, mock_veiculo, mock_repo):
    db = Mock()

    os = Mock()
    os.cliente_cpf = "123"
    os.veiculo_placa = "ABC1234"

    cliente = Mock()
    cliente.cpf = "123"

    veiculo = Mock()
    veiculo.id = 1
    veiculo.placa = "ABC1234"

    mock_cliente.consultar_cliente.return_value = cliente
    mock_cliente.listar_veiculos_cliente.return_value = [veiculo]
    mock_veiculo.consultar_veiculo.return_value = veiculo

    mock_repo.validate_is_os_open.return_value = None

    nova_os = Mock()
    nova_os.id = 10
    mock_repo.create_new_os.return_value = nova_os

    result = criar_nova_os(os, db)

    assert "Nova Ordem de Serviço" in result["message"]

@patch("app.services.OSService.OSRepository")
@patch("app.services.OSService.veiculo_service")
@patch("app.services.OSService.cliente_service")
def test_criar_os_ja_existe_aberta(mock_cliente, mock_veiculo, mock_repo):
    db = Mock()

    os = Mock()
    os.cliente_cpf = "123"
    os.veiculo_placa = "ABC1234"

    cliente = Mock()
    cliente.cpf = "123"

    veiculo = Mock()
    veiculo.id = 1

    mock_cliente.consultar_cliente.return_value = cliente
    mock_cliente.listar_veiculos_cliente.return_value = [veiculo]
    mock_veiculo.consultar_veiculo.return_value = veiculo

    os_existente = Mock()
    os_existente.id = 99
    mock_repo.validate_is_os_open.return_value = os_existente

    with pytest.raises(HTTPException) as exc:
        criar_nova_os(os, db)

    assert exc.value.status_code == 409

@patch("app.services.OSService.OSRepository")
@patch("app.services.OSService.veiculo_service")
@patch("app.services.OSService.cliente_service")
def test_criar_os_veiculo_nao_pertence(mock_cliente, mock_veiculo, mock_repo):
    db = Mock()

    os = Mock()
    os.cliente_cpf = "123"
    os.veiculo_placa = "XYZ9999"

    cliente = Mock()
    cliente.cpf = "123"

    veiculo = Mock()
    veiculo.placa = "ABC1234"
    veiculo.id = 1

    mock_cliente.consultar_cliente.return_value = cliente
    mock_cliente.listar_veiculos_cliente.return_value = [veiculo]
    mock_veiculo.consultar_veiculo.return_value = veiculo

    mock_repo.validate_is_os_open.return_value = None

    with pytest.raises(HTTPException) as exc:
        criar_nova_os(os, db)

    assert exc.value.status_code == 400


@patch("app.services.OSService.catalog_client")
def test_criar_os_completa_peca_nao_encontrada(mock_catalog):
    db = Mock()
    dados = _dados_os_completa(pecas=[PecaOSCompletaSchema(peca_id=1, quantidade=2)])

    mock_catalog.consultar_peca.side_effect = HTTPException(status_code=404, detail="Peça não encontrada")

    with pytest.raises(HTTPException) as exc:
        criar_os_completa(dados, db)

    assert exc.value.status_code == 404


@patch("app.services.OSService.catalog_client")
def test_criar_os_completa_estoque_insuficiente(mock_catalog):
    db = Mock()
    dados = _dados_os_completa(pecas=[PecaOSCompletaSchema(peca_id=1, quantidade=5)])

    mock_catalog.consultar_peca.return_value = {"id": 1, "nome": "Filtro de óleo", "preco": 30.0, "quantidade": 2}

    with pytest.raises(HTTPException) as exc:
        criar_os_completa(dados, db)

    assert exc.value.status_code == 400


@patch("app.services.OSService.catalog_client")
def test_criar_os_completa_servico_nao_encontrado(mock_catalog):
    db = Mock()
    dados = _dados_os_completa(servicos=[1])

    mock_catalog.consultar_servico.side_effect = HTTPException(status_code=404, detail="Serviço não encontrado")

    with pytest.raises(HTTPException) as exc:
        criar_os_completa(dados, db)

    assert exc.value.status_code == 404


@patch("app.services.OSService.VeiculoRepository")
@patch("app.services.OSService.cliente_repository")
@patch("app.services.OSService.cliente_service")
def test_criar_os_completa_veiculo_de_outro_cliente(mock_cliente_service, mock_cliente_repo, mock_veiculo_repo):
    db = Mock()
    dados = _dados_os_completa()

    cliente_existente = Mock()
    cliente_existente.id = 1
    mock_cliente_repo.get_specific_client.return_value = cliente_existente

    veiculo_existente = Mock()
    veiculo_existente.cliente_id = 999
    mock_veiculo_repo.get_vehicle.return_value = veiculo_existente

    with pytest.raises(HTTPException) as exc:
        criar_os_completa(dados, db)

    assert exc.value.status_code == 409


@patch("app.services.OSService.OSRepository")
@patch("app.services.OSService.VeiculoRepository")
@patch("app.services.OSService.cliente_repository")
@patch("app.services.OSService.cliente_service")
def test_criar_os_completa_veiculo_com_os_aberta(mock_cliente_service, mock_cliente_repo, mock_veiculo_repo, mock_os_repo):
    db = Mock()
    dados = _dados_os_completa()

    cliente_existente = Mock()
    cliente_existente.id = 1
    mock_cliente_repo.get_specific_client.return_value = cliente_existente

    veiculo_existente = Mock()
    veiculo_existente.id = 10
    veiculo_existente.cliente_id = 1
    mock_veiculo_repo.get_vehicle.return_value = veiculo_existente

    os_aberta = Mock()
    os_aberta.id = 77
    mock_os_repo.validate_is_os_open.return_value = os_aberta

    with pytest.raises(HTTPException) as exc:
        criar_os_completa(dados, db)

    assert exc.value.status_code == 409


@patch("app.services.OSService.OSRepository")
@patch("app.services.OSService.veiculo_service")
@patch("app.services.OSService.VeiculoRepository")
@patch("app.services.OSService.cliente_service")
@patch("app.services.OSService.cliente_repository")
def test_criar_os_completa_cliente_e_veiculo_novos(
    mock_cliente_repo, mock_cliente_service, mock_veiculo_repo, mock_veiculo_service, mock_os_repo
):
    db = Mock()
    dados = _dados_os_completa()

    mock_cliente_repo.get_specific_client.side_effect = [None, Mock(id=1, cpf=dados.cliente.cpf)]
    mock_veiculo_repo.get_vehicle.side_effect = [None, Mock(id=10, placa=dados.veiculo.placa)]

    nova_os = Mock()
    nova_os.id = 50
    mock_os_repo.create_new_os.return_value = nova_os

    result = criar_os_completa(dados, db)

    mock_cliente_service.cadastrar_cliente.assert_called_once()
    mock_veiculo_service.cadastrar_veiculo.assert_called_once()
    assert "Nova Ordem de Serviço Completa" in result["message"]
    assert "50" in result["message"]


@patch("app.services.OSService.OSRepository")
@patch("app.services.OSService.veiculo_service")
@patch("app.services.OSService.VeiculoRepository")
@patch("app.services.OSService.cliente_service")
@patch("app.services.OSService.cliente_repository")
def test_criar_os_completa_cliente_existente_atualiza(
    mock_cliente_repo, mock_cliente_service, mock_veiculo_repo, mock_veiculo_service, mock_os_repo
):
    db = Mock()
    dados = _dados_os_completa()

    cliente_existente = Mock()
    cliente_existente.id = 1
    mock_cliente_repo.get_specific_client.return_value = cliente_existente
    mock_cliente_repo.update_client_infos.return_value = cliente_existente

    mock_veiculo_repo.get_vehicle.side_effect = [None, Mock(id=10, placa=dados.veiculo.placa)]

    nova_os = Mock()
    nova_os.id = 60
    mock_os_repo.create_new_os.return_value = nova_os

    result = criar_os_completa(dados, db)

    mock_cliente_repo.update_client_infos.assert_called_once()
    mock_cliente_service.cadastrar_cliente.assert_not_called()
    assert "60" in result["message"]


@patch("app.services.OSService.OSRepository")
@patch("app.services.OSService.VeiculoRepository")
@patch("app.services.OSService.cliente_service")
@patch("app.services.OSService.cliente_repository")
def test_criar_os_completa_veiculo_existente_atualiza(
    mock_cliente_repo, mock_cliente_service, mock_veiculo_repo, mock_os_repo
):
    db = Mock()
    dados = _dados_os_completa()

    cliente_existente = Mock()
    cliente_existente.id = 1
    mock_cliente_repo.get_specific_client.return_value = cliente_existente
    mock_cliente_repo.update_client_infos.return_value = cliente_existente

    veiculo_existente = Mock()
    veiculo_existente.id = 10
    veiculo_existente.cliente_id = 1
    mock_veiculo_repo.get_vehicle.return_value = veiculo_existente
    mock_veiculo_repo.update_vehicle_info.return_value = veiculo_existente

    mock_os_repo.validate_is_os_open.return_value = None

    nova_os = Mock()
    nova_os.id = 70
    mock_os_repo.create_new_os.return_value = nova_os

    result = criar_os_completa(dados, db)

    mock_veiculo_repo.update_vehicle_info.assert_called_once()
    assert "70" in result["message"]


@patch("app.services.OSService.OSRepository")
@patch("app.services.OSService.veiculo_service")
@patch("app.services.OSService.VeiculoRepository")
@patch("app.services.OSService.cliente_service")
@patch("app.services.OSService.cliente_repository")
@patch("app.services.OSService.catalog_client")
def test_criar_os_completa_com_pecas_e_servicos(
    mock_catalog,
    mock_cliente_repo,
    mock_cliente_service,
    mock_veiculo_repo,
    mock_veiculo_service,
    mock_os_repo,
):
    db = Mock()
    dados = _dados_os_completa(
        pecas=[PecaOSCompletaSchema(peca_id=1, quantidade=2)],
        servicos=[1],
    )

    peca = {"id": 1, "nome": "Pastilha de freio", "preco": 80.0, "quantidade": 5}
    mock_catalog.consultar_peca.return_value = peca

    servico = {"id": 1, "nome": "Alinhamento", "preco": 100.0}
    mock_catalog.consultar_servico.return_value = servico

    mock_cliente_repo.get_specific_client.side_effect = [None, Mock(id=1, cpf=dados.cliente.cpf)]
    mock_veiculo_repo.get_vehicle.side_effect = [None, Mock(id=10, placa=dados.veiculo.placa)]

    nova_os = Mock()
    nova_os.id = 80
    mock_os_repo.create_new_os.return_value = nova_os

    result = criar_os_completa(dados, db)

    mock_catalog.baixar_estoque.assert_called_once_with(1, 2)
    mock_os_repo.add_os_peca.assert_called_once_with(80, peca, 2, db)
    mock_os_repo.add_service_os.assert_called_once_with(80, servico, db)
    assert "80" in result["message"]


@patch("app.services.OSService.OSRepository")
def test_consultar_os_calculo_total(mock_repo):
    db = Mock()

    peca = Mock(nome="Motor", preco=100, quantidade=2)
    servico = Mock(nome="Troca", preco=50)

    os_mock = Mock()
    os_mock.id = 1
    os_mock.status = "ABERTA"

    os_mock.cliente.cpf = "123"
    os_mock.veiculo.placa = "ABC"

    os_mock.os_pecas = [peca]
    os_mock.os_servicos = [servico]

    mock_repo.get_specific_os.return_value = os_mock

    result = consultar_os(1, db)

    assert result["Total"] == 250

from app.domain.enums.StatusOS import StatusOS

def _os_com_itens():
    os = Mock()
    os.id = 7
    os.cliente.nome = "João"
    os.cliente.email = "joao@mail.com"
    os.cliente.cpf = "52998224725"
    os.os_pecas = [Mock(nome="Filtro", quantidade=2, preco=45.9)]
    os.os_servicos = [Mock(nome="Troca de Óleo", preco=120.0)]
    return os


@patch("app.services.OSService.rabbitmq")
@patch("app.services.OSService.OSRepository")
def test_avancar_os_sucesso(mock_repo, mock_rabbit):
    db = Mock()

    os = Mock()
    os.status = StatusOS.RECEBIDA

    mock_repo.get_specific_os.return_value = os
    mock_repo.advance_os.return_value = {"ok": True}

    result = avancar_os(1, db)

    assert result is not None
    mock_repo.advance_os.assert_called_once_with(os, StatusOS.EM_DIAGNOSTICO, db)
    mock_rabbit.publicar.assert_not_called()


@patch("app.services.OSService.rabbitmq")
@patch("app.services.OSService.OSRepository")
def test_avancar_para_aguardando_aprovacao_inicia_saga(mock_repo, mock_rabbit):
    db = Mock()

    os = _os_com_itens()
    os.status = StatusOS.EM_DIAGNOSTICO
    mock_repo.get_specific_os.return_value = os

    avancar_os(7, db)

    fila, mensagem = mock_rabbit.publicar.call_args.args
    assert fila == "billing.commands"
    assert mensagem["tipo"] == "GERAR_ORCAMENTO"
    assert mensagem["total"] == 211.8
    mock_repo.advance_os.assert_called_once_with(os, StatusOS.AGUARDANDO_APROVACAO, db)


@patch("app.services.OSService.rabbitmq")
@patch("app.services.OSService.OSRepository")
def test_avancar_rabbitmq_fora_nao_muda_status(mock_repo, mock_rabbit):
    db = Mock()

    os = _os_com_itens()
    os.status = StatusOS.EM_DIAGNOSTICO
    mock_repo.get_specific_os.return_value = os
    mock_rabbit.publicar.side_effect = HTTPException(status_code=503, detail="RabbitMQ indisponível")

    with pytest.raises(HTTPException) as exc:
        avancar_os(7, db)

    assert exc.value.status_code == 503
    mock_repo.advance_os.assert_not_called()


@patch("app.services.OSService.OSRepository")
def test_avancar_os_em_execucao_bloqueado(mock_repo):
    db = Mock()

    os = Mock()
    os.status = StatusOS.EM_EXECUCAO
    mock_repo.get_specific_os.return_value = os

    with pytest.raises(HTTPException) as exc:
        avancar_os(1, db)

    assert exc.value.status_code == 400
    assert "execution-service" in exc.value.detail


@patch("app.services.OSService.OSRepository")
def test_avancar_os_status_final(mock_repo):
    db = Mock()

    os = Mock()
    os.status = StatusOS.ENTREGUE
    mock_repo.get_specific_os.return_value = os

    with pytest.raises(HTTPException) as exc:
        avancar_os(1, db)

    assert exc.value.status_code == 400


@patch("app.services.OSService.OSRepository")
def test_avancar_os_nao_encontrada(mock_repo):
    mock_repo.get_specific_os.return_value = None

    with pytest.raises(HTTPException) as exc:
        avancar_os(1, Mock())

    assert exc.value.status_code == 404


def test_montar_pedido_orcamento():
    pedido = montar_pedido_orcamento(_os_com_itens())

    assert pedido["os_id"] == 7
    assert pedido["cliente"]["email"] == "joao@mail.com"
    assert pedido["pecas"] == [{"nome": "Filtro", "quantidade": 2, "valor": 45.9}]
    assert pedido["servicos"] == [{"nome": "Troca de Óleo", "valor": 120.0}]
    assert pedido["total"] == 211.8


@patch("app.services.OSService.OSRepository")
def test_consultar_historico(mock_repo):
    mock_repo.get_specific_os.return_value = Mock()
    mock_repo.get_historico.return_value = [Mock(status="Recebida", evento="OS aberta", criado_em="2026-11-14")]

    result = consultar_historico(1, Mock())

    assert result == [{"status": "Recebida", "evento": "OS aberta", "data": "2026-11-14"}]


@patch("app.services.OSService.OSRepository")
def test_consultar_historico_os_nao_encontrada(mock_repo):
    mock_repo.get_specific_os.return_value = None

    with pytest.raises(HTTPException) as exc:
        consultar_historico(1, Mock())

    assert exc.value.status_code == 404

from app.domain.enums.StatusOS import StatusOS

@patch("app.services.OSService.OSRepository")
def test_avancar_os_bloqueado(mock_repo):
    db = Mock()

    os = Mock()
    os.status = StatusOS.AGUARDANDO_APROVACAO

    mock_repo.get_specific_os.return_value = os

    with pytest.raises(HTTPException) as exc:
        avancar_os(1, db)

    assert exc.value.status_code == 400

@patch("app.services.OSService.OSRepository")
def test_listar_os_sucesso(mock_repo):
    db = Mock()

    mock_repo.get_all_os.return_value = [1, 2]

    result = listar_todas_os(db)

    assert len(result) == 2

@patch("app.services.OSService.OSRepository")
def test_listar_os_vazio(mock_repo):
    db = Mock()

    mock_repo.get_all_os.return_value = []

    with pytest.raises(HTTPException) as exc:
        listar_todas_os(db)

    assert exc.value.status_code == 404

@patch("app.services.OSService.OSRepository")
@patch("app.services.OSService.veiculo_service")
@patch("app.services.OSService.cliente_service")
def test_atualizar_os_sucesso(mock_cliente, mock_veiculo, mock_repo):
    db = Mock()

    dados = Mock()
    dados.model_dump.return_value = {
        "veiculo_placa": "ABC123",
        "cliente_cpf": "123"
    }

    os = Mock()
    os.id = 1

    veiculo = Mock()
    veiculo.id = 10

    cliente = Mock()
    cliente.id = 20

    mock_repo.get_specific_os.return_value = os
    mock_veiculo.consultar_veiculo.return_value = veiculo
    mock_cliente.consultar_cliente.return_value = cliente

    mock_repo.update_os.return_value = os

    result = atualizar_os(1, dados, db)

    assert "atualizada com sucesso" in result["message"]

@patch("app.services.OSService.OSRepository")
def test_atualizar_os_nao_encontrada(mock_repo):
    db = Mock()

    dados = Mock()
    dados.model_dump.return_value = {}

    mock_repo.get_specific_os.return_value = None

    with pytest.raises(HTTPException):
        atualizar_os(1, dados, db)

@patch("app.services.OSService.OSRepository")
def test_remover_os_sucesso(mock_repo):
    db = Mock()

    mock_repo.get_specific_os.return_value = True
    mock_repo.remove_os.return_value = True

    result = remover_os(1, db)

    assert "sucesso" in result["message"]

@patch("app.services.OSService.OSRepository")
def test_remover_os_erro(mock_repo):
    db = Mock()

    mock_repo.get_specific_os.return_value = True
    mock_repo.remove_os.return_value = None

    with pytest.raises(HTTPException) as exc:
        remover_os(1, db)

    assert exc.value.status_code == 500

@patch("app.services.OSService.OSRepository")
def test_consultar_os_nao_encontrada(mock_repo):
    db = Mock()

    mock_repo.get_specific_os.return_value = None

    with pytest.raises(HTTPException) as exc:
        consultar_os(1, db)

    assert exc.value.status_code == 404

@patch("app.services.OSService.OSRepository")
@patch("app.services.OSService.catalog_client")
def test_adicionar_peca_os_sucesso(mock_catalog, mock_repo):
    db = Mock()

    peca = {"id": 1, "nome": "Motor", "preco": 500.0, "quantidade": 10}
    mock_repo.get_specific_os.return_value = Mock()
    mock_catalog.consultar_peca.return_value = peca

    result = adicionar_peca_os(1, 1, 2, db)

    mock_catalog.baixar_estoque.assert_called_once_with(1, 2)
    mock_repo.add_os_peca.assert_called_once_with(1, peca, 2, db)
    assert "adicionada" in result["message"]


@patch("app.services.OSService.OSRepository")
@patch("app.services.OSService.catalog_client")
def test_adicionar_peca_os_catalogo_indisponivel(mock_catalog, mock_repo):
    db = Mock()

    mock_repo.get_specific_os.return_value = Mock()
    mock_catalog.consultar_peca.side_effect = HTTPException(status_code=503, detail="Catalog Service indisponível")

    with pytest.raises(HTTPException) as exc:
        adicionar_peca_os(1, 1, 2, db)

    assert exc.value.status_code == 503
    mock_repo.add_os_peca.assert_not_called()

@patch("app.services.OSService.OSRepository")
@patch("app.services.OSService.catalog_client")
def test_remover_peca_os_sucesso(mock_catalog, mock_repo):
    db = Mock()

    os = Mock()
    os_peca = Mock()
    os_peca.quantidade = 2

    mock_repo.get_specific_os.return_value = os
    mock_repo.get_peca_da_os.return_value = os_peca

    result = remover_peca_os(1, 1, db)

    mock_catalog.devolver_estoque.assert_called_once_with(1, 2)
    assert "removida" in result["message"]

@patch("app.services.OSService.catalog_client")
@patch("app.services.OSService.OSRepository")
def test_adicionar_servico_os_sucesso(mock_repo, mock_catalog):
    db = Mock()

    mock_repo.get_specific_os.return_value = Mock()
    mock_catalog.consultar_servico.return_value = {"id": 1, "nome": "Troca de óleo", "preco": 120.0}

    result = adicionar_servico_os(1, 1, db)

    assert "adicionado" in result["message"]

@patch("app.services.OSService.OSRepository")
def test_remover_servico_os_sucesso(mock_repo):
    db = Mock()

    os = Mock()
    mock_repo.get_specific_os.return_value = os
    mock_repo.get_os_service.return_value = True

    result = remover_servico_os(1, 1, db)

    assert "removido" in result["message"]

