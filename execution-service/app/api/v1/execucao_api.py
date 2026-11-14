from fastapi import APIRouter, Depends, Query
from pymongo.database import Database
from typing import Annotated

from app.database import get_db
from app.services import execucao_service

router = APIRouter(prefix="/execucao", tags=["Execução"])
DB = Annotated[Database, Depends(get_db)]

@router.get("/fila", summary="LISTAR FILA DE EXECUÇÃO", description="Lista as OS que estão na fila, em diagnóstico ou em reparo, da mais antiga para a mais nova")
def listar_fila(db: DB):
    return execucao_service.listar_fila(db)

@router.get("/{os_id}", summary="CONSULTAR EXECUÇÃO DA OS", description="Consulta o status da execução de uma OS e o seu histórico")
def consultar_execucao(os_id: int, db: DB):
    return execucao_service.consultar_execucao(os_id, db)

@router.patch("/{os_id}/avancar", summary="AVANÇAR EXECUÇÃO", description="Na Fila → Em Diagnóstico → Em Reparo → Finalizada (ao finalizar, avisa o os-service)")
def avancar_execucao(os_id: int, db: DB):
    return execucao_service.avancar_execucao(os_id, db)

@router.patch("/{os_id}/falhar", summary="MARCAR FALHA NA EXECUÇÃO", description="Não foi possível executar o serviço. Dispara a compensação da Saga: estorno do pagamento, devolução das peças e cancelamento da OS")
def falhar_execucao(os_id: int, db: DB, motivo: str = Query(..., min_length=3)):
    return execucao_service.falhar_execucao(os_id, motivo, db)
