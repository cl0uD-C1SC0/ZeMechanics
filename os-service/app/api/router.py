from fastapi import APIRouter
from app.api.v1 import cliente_api, ordemservico_api, veiculo_api, health_api


router = APIRouter()

router.include_router(cliente_api.router)
router.include_router(veiculo_api.router)
router.include_router(ordemservico_api.router)
router.include_router(health_api.router)
