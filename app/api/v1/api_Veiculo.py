from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.services import svc_Veiculo as veiculo_service
from app.domain.models.Cliente import Cliente 
from app.domain.models.Veiculo import Veiculo as VeiculoModel
from app.database import get_db
from app.schemas import VeiculoSchema

router = APIRouter(prefix="/veiculo", tags=["Veiculos"])

@router.post("/consultar_placa")
def consultar_placa(placa: str, db: Session = Depends(get_db)):
    if veiculo_service.consultar_placa(placa, db):
        return "> A placa não foi cadastrada ainda.."
    return "> A placa do veículo já está cadastrada, tente novamente.."

@router.post("/cadastrar_veiculo")
def cadastrar_veiculo(veiculo: VeiculoSchema, db: Session = Depends(get_db)):
    ...