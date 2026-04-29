from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from app.services import veiculo_service
from app.database import get_db
from app.schemas.VeiculoSchema import VeiculoSchema, UpdateVehicleSchema

router = APIRouter(prefix="/veiculo", tags=["Veiculos v1"])
DB = Annotated[Session, Depends(get_db)]

@router.post("/cadastrar_veiculo", status_code=status.HTTP_201_CREATED, summary="CADASTRAR NOVO VEÍCULO", description="Adiciona um novo veículo ao sistema e o atribuí em um cliente")
def cadastrar_veiculo(veiculo: VeiculoSchema, db: DB):
    veiculo = veiculo_service.cadastrar_veiculo(veiculo, db)
    return veiculo

@router.get("/consultar_placa/{placa}", summary="CONSULTAR UM VEÍCULO ESPECÍFICO", description="Consulta um veículo específico e suas informações com base na Placa")
def consultar_placa(placa: str, db: DB):
    veiculo_consultado = veiculo_service.consultar_veiculo(placa, db)
    return veiculo_consultado

@router.get("/veiculos", summary="LISTAR TODOS OS VEÍCULOS", description="Lista todos os veículos e seus respectivos donos (cliente_id)")
def listar_veiculos(db: DB):
    veiculos = veiculo_service.listar_todos_veiculos(db)
    return veiculos

@router.patch("/atualizar_veiculo/{placa}", summary="ATUALIZAR VEÍCULO", description="Atualiza um veículo específico: MODELO, MARCA & ANO")
def atualizar_veiculo(placa: str, dados: UpdateVehicleSchema, db: DB):
    veiculo_atualizado = veiculo_service.atualizar_dados_veiculo(placa, dados, db)
    return veiculo_atualizado

@router.delete("/remover_veiculo/{veiculo_placa}", summary="EXCLUIR UM VEÍCULO", description="Excluí do sistema um veículo cadastrado")
def remover_veiculo_cliente(veiculo_placa: str, db: DB):
    veiculo_removido = veiculo_service.remover_veiculo(veiculo_placa, db)
    return veiculo_removido