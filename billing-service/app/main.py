import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from app.api.router import router
from app.database import Base, engine

from app.domain.models.Orcamento_model import Orcamento, Pagamento
from app.messaging import rabbitmq
from app.services import orcamento_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app):
    # Escuta os comandos do os-service (participante da Saga)
    if os.getenv("RABBITMQ_URL"):
        rabbitmq.iniciar_consumidor("billing.commands", orcamento_service.processar_comando)
    yield


app = FastAPI(
    title="Ze Mechanics LTDA - Billing Service",
    description="Swagger UI - FIAP | Orçamentos, Aprovação e Pagamentos",
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
        title="Ze Mechanics LTDA - Billing Service",
        swagger_favicon_url="static/images/Logo-ZeMechanicsLTDA.ico",
        swagger_ui_parameters={
            "syntaxHighlight.theme": "agate",
            "docExpansion": "none",
            "filter": True,
            "displayRequestDuration": True
        },
    )

app.include_router(router, prefix="/api/v1")
