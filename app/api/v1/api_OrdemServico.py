from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.OrdemServicoSchema import OrdemDeServicoSchema, OSUpdateSchema, OSResponse
from app.services import OSService as os_service

router = APIRouter(prefix="/ordem_servico", tags=["OrdemDeServico"])

@router.post("/nova_os", description="Cria uma nova OS com apenas um veículo atribuído por vez")
def criar_os(os: OrdemDeServicoSchema, db: Session = Depends(get_db)):
    nova_os = os_service.criar_nova_os(os, db)
    return nova_os

@router.get("/ordens", response_model=list[OSResponse])
def listar_todas_as_os(db: Session = Depends(get_db)):
    ordens = os_service.listar_todas_os(db)
    return ordens

@router.get("/consultar/{os_id}", summary="Consultar o status da OS", description="Consultar o STATUS da OS e seu respectivo dono")
def consultar_ordemservico(os_id: int, db: Session = Depends(get_db)):
    os_consultada = os_service.consultar_os(os_id, db)
    return os_consultada

@router.patch("/atualizar/{os_id}", description="Atualiza o CPF ou o veiculo da OS")
def atualizar_os(os_id: int, dados: OSUpdateSchema, db: Session = Depends(get_db)):
    os_atualizada = os_service.atualizar_os(os_id, dados, db)
    return os_atualizada

@router.delete("/excluir/{os_id}")
def excluir_os(os_id: int, db: Session = Depends(get_db)):
    os_removida = os_service.remover_os(os_id, db)
    return os_removida

# OUTRAS

# PECAS
# adicionar peca

# remover peca

# SERVICOS
# adicionar servico

# remover servico
# ----
@router.patch("/avancar/{os_id}")
def avancar_ordem(os_id: int, db: Session = Depends(get_db)):
    os_avancada = os_service.avancar_os(os_id, db)
    return os_avancada

@router.get("/aprovar/{os_id}")
def pagina_aprovacao(os_id: int, cliente_cpf: str = Query(...), db: Session = Depends(get_db)):
    return HTMLResponse(f"""
        <html>
            <body>
                <h2>OS #{os_id} — Aguardando Aprovação</h2>
                <p>Clique no botão abaixo para aprovar sua OS:</p>
                <form method="post" action="/api/v1/ordem_servico/confirmar_aprovacao/{os_id}?cliente_cpf={cliente_cpf}">
                    <button type="submit">✅ Aprovar OS</button>
                </form>
            </body>
        </html>
    """)

@router.post("/confirmar_aprovacao/{os_id}")
def aprovar_os(os_id: int, cliente_cpf: str = Query(...), db: Session = Depends(get_db)):
    return os_service.aprovar_os(os_id, cliente_cpf, db)