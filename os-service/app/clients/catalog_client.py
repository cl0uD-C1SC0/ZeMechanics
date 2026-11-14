import os
import httpx
from fastapi import HTTPException

# Chamadas REST síncronas do os-service para o catalog-service.
# O os-service NÃO acessa o banco do catálogo — só a API dele.

CATALOG_URL = os.getenv("CATALOG_SERVICE_URL", "http://catalog-service:8000")
TIMEOUT = 5


def _request(method, path, **kwargs):
    try:
        response = httpx.request(method, f"{CATALOG_URL}/api/v1{path}", timeout=TIMEOUT, **kwargs)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Catalog Service indisponível, tente novamente")

    if response.status_code >= 400:
        detail = response.json().get("detail", "Erro no Catalog Service")
        raise HTTPException(status_code=response.status_code, detail=detail)

    return response.json()


def consultar_peca(peca_id):
    return _request("GET", f"/peca/consultar_peca/{peca_id}")


def baixar_estoque(peca_id, quantidade):
    return _request("PATCH", f"/peca/remover_quantidade/{peca_id}", params={"quantidade": quantidade})


def devolver_estoque(peca_id, quantidade):
    return _request("PATCH", f"/peca/adicionar_quantidade/{peca_id}", params={"quantidade": quantidade})


def consultar_servico(servico_id):
    return _request("GET", f"/servico/consultar_servico/{servico_id}")
