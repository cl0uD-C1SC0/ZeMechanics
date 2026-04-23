# from app.repositories.veiculos import get_vehicle, add_veiculo
from app.repositories import veiculos
from app.repositories import clientes
from fastapi import HTTPException

def consultar_veiculo(placa, db):
    veiculo_consultado = veiculos.get_vehicle(placa, db) 
    if not veiculo_consultado:
        raise HTTPException(status_code=404, detail="O Veículo com a placa solicitada não foi encontrado no sistema")
    return veiculo_consultado

def cadastrar_veiculo(veiculo, db):
    novo_veiculo = veiculos.add_veiculo(veiculo, db)
    return novo_veiculo

def atualizar_dados_veiculo(placa, dados, db):
    veiculo = consultar_veiculo(placa, db)

    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo com essa placa não encontrado")
    
    veiculo_atualizado = veiculos.update_vehicle_info(veiculo, dados, db)
    return veiculo_atualizado

def listar_todos_veiculos(db):
    todos_veiculos = veiculos.get_all_vehicles(db)
    if not todos_veiculos:
        raise HTTPException(status_code=404, detail="Nenhum veículo foi cadastrado")
    return todos_veiculos

def remover_veiculo(veiculo_placa, db):
    if not veiculos.get_vehicle(veiculo_placa, db):
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    return veiculos.delete_vehicle(veiculo_placa, db)