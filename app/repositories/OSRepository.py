from fastapi import HTTPException
from app.domain.models.cliente_model import Cliente as ClienteModel
from app.domain.models.Veiculo_model import Veiculo as VeiculoModel
from app.domain.models.OrdemServico_model import OrdemDeServico as OSModel

from app.domain.enums.StatusOS import StatusOS
from datetime import datetime

from app.services.EmailService import enviar_email_aprovacao

def create_new_os(cliente, veiculo, db):
    nova_os = OSModel(
        cliente_id    = cliente.id,
        veiculo_id    = veiculo.id
    )
    db.add(nova_os)
    db.commit()
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

def advance_os(os, proximo_status, db):
    os.status = proximo_status

    if proximo_status == StatusOS.EM_EXECUCAO:
        os.iniciado_em = datetime.utcnow()
    elif proximo_status == StatusOS.FINALIZADA:
        os.finalizado_em = datetime.utcnow()
    elif proximo_status == StatusOS.ENTREGUE:
        os.entregue_em = datetime.utcnow()
    elif proximo_status == StatusOS.AGUARDANDO_APROVACAO:
        enviar_email_aprovacao(os)

    db.commit()
    db.refresh(os)
    return {"message": f"OS {os.id} avançada para: {proximo_status.value}"}

def approve_os(os, db):
    
    os.status = StatusOS.EM_EXECUCAO
    db.commit()
    db.refresh(os)

    return {"message": "OS Aprovada com sucesso, agora será executada"}