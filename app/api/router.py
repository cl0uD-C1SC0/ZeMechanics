from fastapi import APIRouter
from app.api.v1 import api_Cliente, api_OrdemServico, api_Peca, api_Servico, api_Veiculo

router = APIRouter()

router.include_router(api_Cliente.router)
router.include_router(api_Veiculo.router)
router.include_router(api_OrdemServico.router)
router.include_router(api_Peca.router)
router.include_router(api_Servico.router)