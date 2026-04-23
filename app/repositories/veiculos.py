from app.domain.models.Veiculo_model import Veiculo as VeiculoModel
from fastapi import HTTPException

def get_vehicle(placa, db):
    placa_consultada = db.query(VeiculoModel).filter(VeiculoModel.placa == placa).first()
    return placa_consultada

def add_veiculo(veiculo, db):
    novo_veiculo = VeiculoModel(
        modelo      = veiculo.modelo,
        placa       = veiculo.placa,
        ano         = veiculo.ano,
        cliente_id  = veiculo.cliente_id 
    )

    db.add(novo_veiculo)
    db.commit()
    db.refresh(novo_veiculo)
    return novo_veiculo

def delete_vehicle(veiculo_placa, db):
    veiculo = db.query(VeiculoModel).filter(VeiculoModel.placa == veiculo_placa).first()

    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    db.delete(veiculo)
    db.commit()

    return {"message": "Veículo removido. Necessário cadastrar novamente"}

def update_vehicle_info(veiculo, dados, db):
    for campo, valor in dados.model_dump(exclude_none=True).items():
        setattr(veiculo, campo, valor)

    db.commit()
    db.refresh(veiculo)
    return veiculo

def get_all_vehicles(db):
    veiculos = db.query(VeiculoModel).all()

    if veiculos:
        return veiculos
    raise HTTPException(status_code=404, detail="Nenhum veículo foi cadastrado.")