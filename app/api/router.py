from fastapi import APIRouter
from app.api.v1 import api_OrdemServico, api_Peca, api_Servico, api_Veiculo, cliente_api

router = APIRouter()

router.include_router(cliente_api.router)
router.include_router(api_Veiculo.router)
router.include_router(api_OrdemServico.router)
router.include_router(api_Peca.router)
router.include_router(api_Servico.router)