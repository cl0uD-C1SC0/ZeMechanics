from fastapi import APIRouter
from app.api.v1 import execucao_api, health_api


router = APIRouter()

router.include_router(execucao_api.router)
router.include_router(health_api.router)
