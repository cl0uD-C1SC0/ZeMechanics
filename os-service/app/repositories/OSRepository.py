from app.domain.models.OrdemServico_model import OrdemDeServico as OSModel
from app.domain.models.OrdemServico_model import OSPeca as OSPecaModel
from app.domain.models.OrdemServico_model import OSServico as OSServicoModel
from app.domain.models.OrdemServico_model import HistoricoOS as HistoricoModel

from app.domain.enums.StatusOS import StatusOS, STATUS_ENCERRADOS
from datetime import datetime, timezone


def create_new_os(cliente, veiculo, db):
    nova_os = OSModel(cliente_id=cliente.id, veiculo_id=veiculo.id, status=StatusOS.RECEBIDA)
    db.add(nova_os)
    db.commit()
    add_historico(nova_os.id, StatusOS.RECEBIDA, "OS aberta", db)
    return nova_os


def get_all_os(db):
    ordens = db.query(OSModel).all()
    return ordens


def get_specific_os(os_id, db):
    os = db.query(OSModel).filter(OSModel.id == os_id).first()
    return os


def update_os(os_id, dados_dict, db):
    os = get_specific_os(os_id, db)

    for campo, valor in dados_dict.items():
        setattr(os, campo, valor)

    db.commit()
    db.refresh(os)
    return os


def remove_os(os_id, db):
    os = get_specific_os(os_id, db)

    db.delete(os)
    db.commit()
    return {"message": f"OS {os.id} foi removida"}


def advance_os(os, proximo_status, db, evento="Avanço manual"):
    os.status = proximo_status

    if proximo_status == StatusOS.EM_EXECUCAO:
        os.iniciado_em = datetime.now(timezone.utc)
    elif proximo_status == StatusOS.FINALIZADA:
        os.finalizado_em = datetime.now(timezone.utc)
    elif proximo_status == StatusOS.ENTREGUE:
        os.entregue_em = datetime.now(timezone.utc)

    db.commit()
    db.refresh(os)
    add_historico(os.id, proximo_status, evento, db)
    return {"message": f"OS {os.id} avançada para: {proximo_status.value}"}


def add_historico(os_id, status, evento, db):
    historico = HistoricoModel(ordem_id=os_id, status=status, evento=evento)
    db.add(historico)
    db.commit()
    return historico


def get_historico(os_id, db):
    return (
        db.query(HistoricoModel)
        .filter(HistoricoModel.ordem_id == os_id)
        .order_by(HistoricoModel.id)
        .all()
    )


def add_os_peca(os_id, peca, quantidade, db):
    os_peca = OSPecaModel(
        ordem_id=os_id,
        peca_id=peca["id"],
        nome=peca["nome"],
        preco=peca["preco"],
        quantidade=quantidade,
    )
    db.add(os_peca)
    db.commit()
    db.refresh(os_peca)
    return os_peca


def get_peca_da_os(os_id, peca_id, db):
    return (
        db.query(OSPecaModel)
        .filter(OSPecaModel.ordem_id == os_id, OSPecaModel.peca_id == peca_id)
        .first()
    )


def remove_os_peca(os_id, peca_id, db):
    os_peca = get_peca_da_os(os_id, peca_id, db)
    db.delete(os_peca)
    db.commit()


def add_service_os(os_id, servico, db):
    os_servico = OSServicoModel(
        ordem_id=os_id,
        servico_id=servico["id"],
        nome=servico["nome"],
        preco=servico["preco"],
    )
    db.add(os_servico)
    db.commit()
    db.refresh(os_servico)

    return os_servico


def get_os_service(os_id, servico_id, db):
    return (
        db.query(OSServicoModel)
        .filter(
            OSServicoModel.ordem_id == os_id, OSServicoModel.servico_id == servico_id
        )
        .first()
    )


def remove_service_os(os_id, servico_id, db):
    os_servico = get_os_service(os_id, servico_id, db)
    db.delete(os_servico)
    db.commit()

    return os_servico


def validate_is_os_open(veiculo_id, db):
    return (
        db.query(OSModel)
        .filter(
            OSModel.veiculo_id == veiculo_id,
            OSModel.status.notin_(STATUS_ENCERRADOS),
        )
        .first()
    )
