
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.services import svc_Cliente as cliente_service
from app.domain.models.Cliente import Cliente as ClienteModel
from app.domain.models.Veiculo import Veiculo
from app.database import get_db
from app.schemas import ClienteSchema

router = APIRouter(prefix="/cliente", tags=["Clientes"])

@router.post("/cadastrar_cliente")
def cadastrar_cliente(cliente: ClienteSchema, db: Session = Depends(get_db)):
    if cliente_service.validar_cpf(cliente.cpf):
        novo_cliente = ClienteModel(
            nome     = cliente.nome,
            cpf      = cliente.cpf,
            contato  = cliente.contato,
            endereco = cliente.endereco
        )
        db.add(novo_cliente) 
        db.commit()
        return "> Cliente adicionado"
    return "> Erro ao adicionar o Cliente, tente novamente!"

@router.get("/listar_clientes")
def listar_clientes(db: Session = Depends(get_db)):
    clientes = db.query(ClienteModel).all()
    return clientes

@router.get("/{cpf}")
def consultar_cliente(cpf: int, db: Session = Depends(get_db)):
    cliente = db.query(ClienteModel).filter(ClienteModel.cpf == cpf).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return cliente

@router.get("/{cpf}/veiculos")
def listar_veiculos_do_cliente(cpf: int, db: Session = Depends(get_db)):
    cliente = db.query(ClienteModel).filter(ClienteModel.cpf == cpf).first()

    if not cliente.veiculos:
        raise HTTPException(status_code=404, detail="Cliente não tem veículos cadastrados")

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return cliente.veiculos    
