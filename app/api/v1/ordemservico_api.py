from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from typing import Annotated
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.OrdemServicoSchema import OrdemDeServicoSchema, OSUpdateSchema, OSResponse
from app.services import OSService as os_service

router = APIRouter(prefix="/ordem_servico", tags=["OrdemDeServico"])
DB = Annotated[Session, Depends(get_db)]

@router.post("/nova_os", description="Cria uma nova OS com apenas um veículo atribuído por vez")
def criar_os(os: OrdemDeServicoSchema, db: DB):
    nova_os = os_service.criar_nova_os(os, db)
    return nova_os

@router.get("/ordens", response_model=list[OSResponse])
def listar_todas_as_os(db: DB):
    ordens = os_service.listar_todas_os(db)
    return ordens

@router.get("/consultar/{os_id}", summary="Consultar o status da OS", description="Consultar o STATUS da OS e seu respectivo dono")
def consultar_ordemservico(os_id: int, db: DB):
    os_consultada = os_service.consultar_os(os_id, db)
    return os_consultada

@router.patch("/atualizar/{os_id}", description="Atualiza o CPF ou o veiculo da OS")
def atualizar_os(os_id: int, dados: OSUpdateSchema, db: DB):
    os_atualizada = os_service.atualizar_os(os_id, dados, db)
    return os_atualizada

@router.delete("/excluir/{os_id}")
def excluir_os(os_id: int, db: DB):
    os_removida = os_service.remover_os(os_id, db)
    return os_removida

@router.post("/{os_id}/adicionar_peca/{peca_id}")
def adicionar_peca_os(os_id: int, peca_id: int, db: DB, quantidade: int = Query(..., ge=1)):
    resultado = os_service.adicionar_peca_os(os_id, peca_id, quantidade, db)
    return resultado

@router.delete("/{os_id}/remover_peca/{peca_id}")
def remover_peca_os(os_id: int, peca_id: int, db: DB):
    resultado = os_service.remover_peca_os(os_id, peca_id, db)
    return resultado

@router.post("/{os_id}/adicionar_servico/{servico_id}")
def adicionar_servico_os(os_id: int, servico_id: int, db: DB):
    resultado = os_service.adicionar_servico_os(os_id, servico_id, db)
    return resultado

@router.delete("/{os_id}/remover_servico/{servico_id}")
def remover_servico_os(os_id: int, servico_id: int, db: DB):
    resultado = os_service.remover_servico_os(os_id, servico_id, db)
    return resultado

@router.patch("/avancar/{os_id}")
def avancar_ordem(os_id: int, db: DB):
    os_avancada = os_service.avancar_os(os_id, db)
    return os_avancada

@router.get("/aprovar/{os_id}")
def pagina_aprovacao(os_id: int, db: DB, cliente_cpf: str = Query(...)):
    dados_os = os_service.consultar_os(os_id, db)
    
    pecas_html = "".join([
        f"<tr><td>{p['nome']}</td><td>{p['quantidade']}</td><td>R$ {p['valor']}</td></tr>"
        for p in dados_os["Peças"]
    ])

    servicos_html = "".join([
        f"<tr><td>{s['nome']}</td><td>R$ {s['valor']}</td></tr>"
        for s in dados_os["Serviços"]
    ])

    return HTMLResponse(f"""
        <html>
        <body>
            <h2>OS #{os_id} — Aguardando Aprovação</h2>
            <p><b>Status:</b> {dados_os["Status atual"]}</p>
            <p><b>Veículo:</b> {dados_os["Veículo"]}</p>

            <h3>Peças</h3>
            <table border="1">
                <tr><th>Nome</th><th>Quantidade</th><th>Valor</th></tr>
                {pecas_html}
            </table>

            <h3>Serviços</h3>
            <table border="1">
                <tr><th>Nome</th><th>Valor</th></tr>
                {servicos_html}
            </table>

            <h3>Total: R$ {dados_os["Total"]}</h3>

            <form method="post" action="/api/v1/ordem_servico/confirmar_aprovacao/{os_id}?cliente_cpf={cliente_cpf}">
                <button type="submit">✅ Aprovar OS</button>
            </form>
        </body>
        </html>
    """)

@router.post("/confirmar_aprovacao/{os_id}")
def aprovar_os(os_id: int, db: DB, cliente_cpf: str = Query(...)):
    return os_service.aprovar_os(os_id, cliente_cpf, db)