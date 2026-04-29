from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated
from app.database import get_db
from app.schemas.Servico import ServicoSchema, UpdateServiceSchema, ServicoResponse
from app.services import servico_service as servico_service

router = APIRouter(prefix="/servico", tags=["Serviços v1"])
DB = Annotated[Session, Depends(get_db)]

@router.post("/adicionar_servico")                                   
def cadastrar_servico(servico: ServicoSchema, db: DB):  
    novo_servico = servico_service.adicionar_servico(servico, db)
    return novo_servico

@router.get("/servicos", summary="Listar todos os serviços cadastrados")
def listar_servicos(db: DB):
    servicos = servico_service.listar_todos_servicos(db)
    return servicos

@router.get("/consultar_servico/{servico_id}")
def consultar_servico(servico_id: int, db: DB):
    servico = servico_service.consultar_servico_especifico(servico_id, db)
    return servico

@router.patch("/atualizar_servico/{servico_id}")
def atualizar_servico(servico_id: int, dados: UpdateServiceSchema, db: DB):
    servico_atualizado = servico_service.atualizar_servico_especifico(servico_id, dados, db)
    return servico_atualizado

@router.delete("/remover_servico/{servico_id}")
def remover_servico(servico_id: int, db: DB):
    servico_removido = servico_service.remover_servico(servico_id, db)
    return servico_removido