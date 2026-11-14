from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pymongo.database import Database
from typing import Annotated

from app.database import get_db
from app.services import health_service

router = APIRouter(prefix="/health", tags=["Health"])
DB = Annotated[Database, Depends(get_db)]

@router.get("/live", summary="LIVENESS PROBE", description="Verifica se a aplicação está no ar")
def liveness():
    return health_service.verificar_liveness()

@router.get("/ready", summary="READINESS PROBE", description="Verifica se a aplicação está pronta para receber tráfego, testando a conexão com o MongoDB")
def readiness(db: DB):
    if not health_service.verificar_readiness(db):
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "detail": "Banco de dados indisponível"},
        )
    return {"status": "ok"}
