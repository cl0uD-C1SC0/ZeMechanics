
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Annotated
from app.database import get_db
from app.schemas.Peca import PecaSchema, UpdatePecaSchema
from app.services import peca_service as peca_service

router = APIRouter(prefix="/peca", tags=["Peças v1"])
DB = Annotated[Session, Depends(get_db)]

@router.post("/adicionar_peca")                                   
def cadastrar_nova_peca(servico: PecaSchema, db: DB):  
    nova_peca = peca_service.adicionar_peca(servico, db)
    return nova_peca

@router.get("/pecas", summary="Listar todas as peças cadastrados")
def listar_pecas(db: DB):
    pecas = peca_service.listar_todas_pecas(db)
    return pecas

@router.get("/consultar_peca/{peca_id}")
def consultar_peca(peca_id: int, db: DB):
    peca = peca_service.consultar_peca_especifica(peca_id, db)
    return peca

@router.patch("/atualizar_peca/{peca_id}")
def atualizar_peca(peca_id: int, dados: UpdatePecaSchema, db: DB):
    peca_atualizada = peca_service.atualizar_peca_especifica(peca_id, dados, db)
    return peca_atualizada

@router.patch("/adicionar_quantidade/{peca_id}")
def adicionar_ao_estoque(peca_id: int, db: DB, quantidade: int = Query(..., gt=0)):
    estoque_adicionado = peca_service.adicionar_ao_estoque(peca_id, quantidade, db)
    return estoque_adicionado

@router.patch("/remover_quantidade/{peca_id}")
def remover_do_estoque(peca_id: int, db: DB, quantidade: int = Query(..., gt=0)):
    estoque_removido = peca_service.remover_do_estoque(peca_id, quantidade, db)
    return estoque_removido

@router.delete("/remover_peca/{peca_id}")
def remover_peca(peca_id: int, db: DB):
    peca_removida = peca_service.remover_peca(peca_id, db)
    return peca_removida

