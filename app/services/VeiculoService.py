from app.repositories import VeiculoRepository
from fastapi import HTTPException

def consultar_veiculo(placa, db):
    veiculo_consultado = VeiculoRepository.get_vehicle(placa, db) 
    if not veiculo_consultado:
        raise HTTPException(status_code=404, detail="O Veículo com a placa solicitada não foi encontrado no sistema")
    return veiculo_consultado

def cadastrar_veiculo(veiculo, db):
    novo_veiculo = VeiculoRepository.add_veiculo(veiculo, db)
    return novo_veiculo

def atualizar_dados_veiculo(placa, dados, db):
    veiculo = consultar_veiculo(placa, db)

    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo com essa placa não encontrado")
    
    veiculo_atualizado = VeiculoRepository.update_vehicle_info(veiculo, dados, db)
    return veiculo_atualizado

def listar_todos_veiculos(db):
    todos_veiculos = VeiculoRepository.get_all_vehicles(db)
    if not todos_veiculos:
        raise HTTPException(status_code=404, detail="Nenhum veículo foi cadastrado")
    return todos_veiculos

def remover_veiculo(veiculo_placa, db):
    if not VeiculoRepository.get_vehicle(veiculo_placa, db):
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    return VeiculoRepository.delete_vehicle(veiculo_placa, db)