import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from app.api.router import router
from app.database import Base, engine

from app.domain.models.Cliente_model import Cliente
from app.domain.models.Veiculo_model import Veiculo
from app.domain.models.OrdemServico_model import OrdemDeServico, OSPeca, OSServico, HistoricoOS
from app.messaging import rabbitmq
from app.services import saga_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app):
    # Escuta as respostas do billing/execution (orquestrador da Saga)
    if os.getenv("RABBITMQ_URL"):
        rabbitmq.iniciar_consumidor("os.events", saga_service.processar_evento)
    yield


app = FastAPI(
    title="Ze Mechanics LTDA - OS Service",
    description="Swagger UI - FIAP | Clientes, Veículos e Ordens de Serviço",
    version="1.0",
    docs_url=None,
    contact={"RM": "rm371895", "Nome": "Jose Silva"},
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger():
    return get_swagger_ui_html(
        openapi_url="openapi.json",
        title="Ze Mechanics LTDA - OS Service",
        swagger_favicon_url="static/images/Logo-ZeMechanicsLTDA.ico",
        swagger_ui_parameters={
            "syntaxHighlight.theme": "agate",
            "docExpansion": "none",
            "filter": True,
            "displayRequestDuration": True
        },
    )

app.include_router(router, prefix="/api/v1")
