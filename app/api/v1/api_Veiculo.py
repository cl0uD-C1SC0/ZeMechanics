from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from app.services import svc_Veiculo as veiculo_service
from app.database import get_db
from app.schemas.VeiculoSchema import VeiculoSchema, UpdateVehicleSchema, AddVehicleReponse

router = APIRouter(prefix="/veiculo", tags=["Veiculos v1"])

@router.post("/cadastrar_veiculo", status_code=status.HTTP_201_CREATED, response_model=AddVehicleReponse)
def cadastrar_veiculo(veiculo: VeiculoSchema, db: Session = Depends(get_db)):
    veiculo = veiculo_service.cadastrar_veiculo(veiculo, db)
    return veiculo

@router.get("/consultar_placa")
def consultar_placa(placa: str, db: Session = Depends(get_db)):
    veiculo_consultado = veiculo_service.consultar_veiculo(placa, db)
    return veiculo_consultado

@router.get("/listar_veiculos", summary="Lista todos os veiculos cadastrados & seus donos")
def listar_veiculos(db: Session = Depends(get_db)):
    veiculos = veiculo_service.listar_todos_veiculos(db)
    return veiculos

@router.patch("/atualizar_veiculo/{placa}")
def atualizar_veiculo(placa: str, dados: UpdateVehicleSchema, db: Session = Depends(get_db)):
    veiculo_atualizado = veiculo_service.atualizar_dados_veiculo(placa, dados, db)
    return veiculo_atualizado

@router.delete("/remover_veiculo/{veiculo_placa}", summary="Excluir um veículo")
def remover_veiculo_cliente(veiculo_placa: str, db: Session = Depends(get_db)):
    veiculo_removido = veiculo_service.remover_veiculo(veiculo_placa, db)
    return veiculo_removido