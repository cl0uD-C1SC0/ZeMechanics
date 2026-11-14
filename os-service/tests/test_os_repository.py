from unittest.mock import Mock, patch
from app.repositories.OSRepository import *
from app.domain.enums.StatusOS import StatusOS

PECA = {"id": 1, "nome": "Filtro de Óleo", "preco": 45.9}
SERVICO = {"id": 1, "nome": "Troca de Óleo", "preco": 120.0}

def test_create_new_os(db):
    cliente = Mock()
    cliente.id = 1

    veiculo = Mock()
    veiculo.id = 10

    os = create_new_os(cliente, veiculo, db)

    assert os.id is not None
    assert os.cliente_id == 1
    assert os.veiculo_id == 10

def test_get_all_os(db):
    cliente = Mock(id=1)
    veiculo = Mock(id=1)

    create_new_os(cliente, veiculo, db)
    create_new_os(cliente, veiculo, db)

    result = get_all_os(db)

    assert len(result) == 2

def test_get_all_os(db):
    cliente = Mock(id=1)
    veiculo = Mock(id=1)

    create_new_os(cliente, veiculo, db)
    create_new_os(cliente, veiculo, db)

    result = get_all_os(db)

    assert len(result) == 2

def test_get_specific_os(db):
    cliente = Mock(id=1)
    veiculo = Mock(id=1)

    created = create_new_os(cliente, veiculo, db)

    result = get_specific_os(created.id, db)

    assert result.id == created.id

def test_get_specific_os(db):
    cliente = Mock(id=1)
    veiculo = Mock(id=1)

    created = create_new_os(cliente, veiculo, db)

    result = get_specific_os(created.id, db)

    assert result.id == created.id

def test_update_os(db):
    cliente = Mock(id=1)
    veiculo = Mock(id=1)

    os = create_new_os(cliente, veiculo, db)

    updated = update_os(os.id, {"status": StatusOS.EM_EXECUCAO}, db)                

    assert updated.status == StatusOS.EM_EXECUCAO                   

def test_remove_os(db):
    cliente = Mock(id=1)
    veiculo = Mock(id=1)

    os = create_new_os(cliente, veiculo, db)

    result = remove_os(os.id, db)

    assert "removida" in result["message"]

    assert get_specific_os(os.id, db) is None

def test_advance_os_execucao(db):
    cliente = Mock(id=1)
    veiculo = Mock(id=1)

    os = create_new_os(cliente, veiculo, db)

    result = advance_os(os, StatusOS.EM_EXECUCAO, db)

    assert os.status == StatusOS.EM_EXECUCAO
    assert os.iniciado_em is not None

def test_advance_os_finalizada(db):
    cliente = Mock(id=1)
    veiculo = Mock(id=1)

    os = create_new_os(cliente, veiculo, db)

    advance_os(os, StatusOS.FINALIZADA, db)

    assert os.finalizado_em is not None

def test_advance_os_entregue(db):
    cliente = Mock(id=1)
    veiculo = Mock(id=1)

    os = create_new_os(cliente, veiculo, db)

    advance_os(os, StatusOS.ENTREGUE, db)

    assert os.entregue_em is not None

def test_add_os_peca(db):
    os_peca = add_os_peca(1, PECA, 2, db)

    assert os_peca.id is not None
    assert os_peca.quantidade == 2

def test_get_peca_da_os(db):
    add_os_peca(1, PECA, 2, db)

    result = get_peca_da_os(1, 1, db)

    assert result is not None

def test_remove_os_peca(db):
    add_os_peca(1, PECA, 2, db)

    remove_os_peca(1, 1, db)

    result = get_peca_da_os(1, 1, db)

    assert result is None

def test_add_service_os(db):
    os_servico = add_service_os(1, SERVICO, db)

    assert os_servico.id is not None

def test_get_os_service(db):
    add_service_os(1, SERVICO, db)

    result = get_os_service(1, 1, db)

    assert result is not None

def test_remove_service_os(db):
    add_service_os(1, SERVICO, db)

    remove_service_os(1, 1, db)

    result = get_os_service(1, 1, db)

    assert result is None

def test_validate_is_os_open(db):
    cliente = Mock(id=1)
    veiculo = Mock(id=99)

    os = create_new_os(cliente, veiculo, db)

    result = validate_is_os_open(99, db)

    assert result is not None


def test_validate_is_os_open_ignora_reprovada(db):
    cliente = Mock(id=1)
    veiculo = Mock(id=98)

    os = create_new_os(cliente, veiculo, db)
    advance_os(os, StatusOS.REPROVADA, db)

    result = validate_is_os_open(98, db)

    assert result is None


def test_validate_is_os_open_ignora_entregue(db):
    cliente = Mock(id=1)
    veiculo = Mock(id=97)

    os = create_new_os(cliente, veiculo, db)
    advance_os(os, StatusOS.ENTREGUE, db)

    result = validate_is_os_open(97, db)

    assert result is None

def test_validate_is_os_open_ignora_cancelada(db):
    os = create_new_os(Mock(id=1), Mock(id=96), db)
    advance_os(os, StatusOS.CANCELADA, db, "Pagamento recusado")

    assert validate_is_os_open(96, db) is None


def test_historico_registra_abertura_e_mudancas(db):
    os = create_new_os(Mock(id=1), Mock(id=1), db)
    advance_os(os, StatusOS.EM_DIAGNOSTICO, db)
    add_historico(os.id, os.status, "Orçamento #1 gerado", db)

    historico = get_historico(os.id, db)

    assert [h.status for h in historico] == [StatusOS.RECEBIDA, StatusOS.EM_DIAGNOSTICO, StatusOS.EM_DIAGNOSTICO]
    assert historico[0].evento == "OS aberta"
    assert historico[1].evento == "Avanço manual"
    assert historico[2].evento == "Orçamento #1 gerado"
