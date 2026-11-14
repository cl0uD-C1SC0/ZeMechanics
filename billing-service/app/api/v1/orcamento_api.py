from fastapi import APIRouter, Depends, Query
from typing import Annotated
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import orcamento_service

router = APIRouter(prefix="/orcamento", tags=["Orçamento e Pagamento"])
DB = Annotated[Session, Depends(get_db)]

@router.get("/orcamentos", summary="LISTAR TODOS OS ORÇAMENTOS", description="Lista todos os orçamentos gerados, com OS, status e valor")
def listar_orcamentos(db: DB):
    return orcamento_service.listar_orcamentos(db)

@router.get("/{os_id}", summary="CONSULTAR ORÇAMENTO DA OS", description="Consulta o orçamento de uma OS, seus itens e os pagamentos (aprovado, recusado, estornado)")
def consultar_orcamento(os_id: int, db: DB):
    return orcamento_service.consultar_orcamento(os_id, db)

@router.get("/{os_id}/aprovar", summary="PÁGINA DE APROVAÇÃO DO ORÇAMENTO", description="Página enviada por e-mail ao cliente para aprovar ou recusar o orçamento")
def pagina_aprovacao(os_id: int, db: DB, cliente_cpf: str = Query(...)):
    return orcamento_service.mostrar_aprovacao(os_id, cliente_cpf, db)

@router.post("/{os_id}/confirmar_aprovacao", summary="APROVAR E PAGAR O ORÇAMENTO", description="Cliente aprova o orçamento, o pagamento é processado (Mercado Pago - mock) e a OS segue para execução")
def aprovar_orcamento(os_id: int, db: DB, cliente_cpf: str = Query(...)):
    return orcamento_service.aprovar_orcamento(os_id, cliente_cpf, db)

@router.post("/{os_id}/reprovar", summary="REPROVAR O ORÇAMENTO", description="Cliente recusa o orçamento; a OS é encerrada como Reprovada e as peças voltam ao estoque")
def reprovar_orcamento(os_id: int, db: DB, cliente_cpf: str = Query(...)):
    return orcamento_service.reprovar_orcamento(os_id, cliente_cpf, db)
