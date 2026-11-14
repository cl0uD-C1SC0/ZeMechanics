from fastapi import APIRouter
from app.api.v1 import peca_api, servico_api, health_api


router = APIRouter()

router.include_router(peca_api.router)
router.include_router(servico_api.router)
router.include_router(health_api.router)
