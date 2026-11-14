from fastapi import APIRouter
from app.api.v1 import orcamento_api, health_api


router = APIRouter()

router.include_router(orcamento_api.router)
router.include_router(health_api.router)
