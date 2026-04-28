
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app.services import cliente_service as cliente_service
from app.schemas.cliente_schema import ClienteSchema, ConsultAllClientsResponse, ConsultClientResponse, ClienteUpdateSchema

router = APIRouter(prefix="/cliente", tags=["Clientes v1"])
DB = Annotated[Session, Depends(get_db)]

@router.post("/novo_cliente", status_code=status.HTTP_201_CREATED, summary="Cadastrar novo cliente", description="Cadastra um novo cliente com CPF, Nome, Endereco & Contato")
def cadastrar_cliente(cliente: ClienteSchema, db: DB):
    novo_cliente = cliente_service.cadastrar_cliente(cliente, db)
    return novo_cliente

@router.get("/clientes", response_model=list[ConsultAllClientsResponse], summary="Listar todos os clientes cadastrados", description="Lista todas as informações, incluindo o ID dos clientes")
def listar_clientes(db: DB):
    clientes = cliente_service.listar_clientes(db)
    return clientes
    
@router.get("/{cpf}", response_model=ConsultClientResponse, summary="Consultar um cliente específico", description="Consultar todos os dados de um cliente com base em um CPF")
def consultar_cliente(cpf: int, db: DB):
    cliente = cliente_service.consultar_cliente(cpf, db)    
    return cliente

@router.get("/{cpf}/veiculos", summary="Listar somente veículos de um Cliente", description="Consulta todos os veículos do cliente que foram cadastrados")
def listar_veiculos_do_cliente(cpf: int, db: DB):
    cliente_veiculos = cliente_service.listar_veiculos_cliente(cpf, db)
    return cliente_veiculos.veiculos 

@router.patch("/{cpf}/atualizar_informacoes", summary="Atualizar dados cadastrais", description="Atualizar dados como NOME, CONTATO, ENDERECO")
def atualizar_cliente(cpf: int, dados: ClienteUpdateSchema, db: DB):
    dados_atualizados = cliente_service.atualizar_informacao_cliente(cpf, dados, db)
    return dados_atualizados

@router.delete("/{cpf}/remover_cliente", summary="Remover um cliente cadastrado", description="Remover um cliente que foi cadastrado")
def remover_cliente(cpf: int, db: DB):
    cliente_removido = cliente_service.remover_cliente(cpf, db)
    return cliente_removido

@router.patch("/{novo_cpf}/transferir_veiculo/{placa}")
def transferir_veiculo(novo_cpf: int, placa: str, db: DB):
    veiculo_transferido = cliente_service.transferir_veiculo_cliente(placa, novo_cpf, db)
    return veiculo_transferido