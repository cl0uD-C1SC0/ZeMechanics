
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.services import svc_Cliente as cliente_service
from app.database import get_db
from app.schemas.ClienteSchema import ClienteSchema, AddClientResponse, ConsultClientResponse, ClienteUpdateSchema

router = APIRouter(prefix="/cliente", tags=["Clientes v1"])

@router.post("/cadastrar_cliente", status_code=status.HTTP_201_CREATED, response_model=AddClientResponse,summary="Cadastrar novo cliente", description="Cadastra um novo cliente com CPF, Nome, Endereco & Contato")
def cadastrar_cliente(cliente: ClienteSchema, db: Session = Depends(get_db)):
    novo_cliente = cliente_service.cadastrar_cliente(cliente, db)
    return {"id": novo_cliente.id, "nome": novo_cliente.nome, "message": "Cliente adicionado"}

@router.get("/clientes", summary="Listar todos os clientes cadastrados", description="Lista todas as informações, incluindo o ID dos clientes")
def listar_clientes(db: Session = Depends(get_db)):
    clientes = cliente_service.listar_clientes(db)
    if clientes:
        return clientes
    raise HTTPException(status_code=404, detail="> Não foi possível listar os clientes")

@router.get("/consultar_cliente/{cpf}", response_model=ConsultClientResponse, summary="Consultar um cliente específico", description="Consultar todos os dados de um cliente com base em um CPF")
def consultar_cliente(cpf: int, db: Session = Depends(get_db)):
    cliente = cliente_service.consultar_cliente(cpf, db)    
    return cliente

@router.get("/{cpf}/veiculos", summary="Listar somente veículos de um Cliente", description="Consulta todos os veículos do cliente que foram cadastrados")
def listar_veiculos_do_cliente(cpf: int, db: Session = Depends(get_db)):
    cliente_veiculos = cliente_service.listar_veiculos_cliente(cpf, db)
    return cliente_veiculos.veiculos 

@router.patch("/atualizar_informacoes/{cpf}", summary="Atualizar dados cadastrais", description="Atualizar dados como NOME, CONTATO, ENDERECO")
def atualizar_cliente(cpf: int, dados: ClienteUpdateSchema, db: Session = Depends(get_db)):
    dados_atualizados = cliente_service.atualizar_informacao_cliente(cpf, dados, db)
    return dados_atualizados

@router.delete("/remover_cliente/{cpf}", summary="Remover um cliente cadastrado", description="Remover um cliente que foi cadastrado")
def remover_cliente(cpf: int, db: Session = Depends(get_db)):
    cliente_removido = cliente_service.remover_cliente(cpf, db)
    return cliente_removido

@router.patch("/transferir_veiculo/{placa}/{novo_cpf}")
def transferir_veiculo(novo_cpf: str, placa: str, db: Session = Depends(get_db)):
    veiculo_transferido = cliente_service.transferir_veiculo_cliente(placa, novo_cpf, db)
    return veiculo_transferido