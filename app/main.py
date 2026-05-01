from fastapi import FastAPI
from app.api.router import router
from app.database import Base, engine
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from app.domain.models.cliente_model import Cliente
from app.domain.models.Veiculo_model import Veiculo
from app.domain.models.Peca_model import Peca
from app.domain.models.Servico_model import Servicos
from app.domain.models.OrdemServico_model import OrdemDeServico, OSPeca, OSServico

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ze Mechanics LTDA",
    description="Swagger UI - FIAP",
    version="1.0",
    docs_url=None,
    contact={"RM": "rm371895", "Nome": "Jose Silva"},
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger():
    html = get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Ze Mechanics LTDA",
        swagger_favicon_url="/static/images/Logo-ZeMechanicsLTDA.ico",
        swagger_ui_parameters={
            "syntaxHighlight.theme": "agate",
            "docExpansion": "none",
            "filter": True,
            "displayRequestDuration": True,
            "persistAuthorization": True,
        },
    )
    return html


app.include_router(router, prefix="/api/v1")
