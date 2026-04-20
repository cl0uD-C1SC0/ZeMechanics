from fastapi import FastAPI
from app.api.router import router
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ze Mechanics LTDA",
    description="Sistema para a mecânica - ZeMechanics LTDA",
    version="1.0"
)

app.include_router(router, prefix="/api/v1")

# @app.post("/cadastrar_veiculo")
# def cadastrar_veiculo(veiculo: VeiculoSchema, db: Session = Depends(get_db)):
#     novo_veiculo = VeiculoModel(
#         modelo      = veiculo.modelo,
#         placa       = veiculo.placa,
#         ano         = veiculo.ano,
#         cliente_id  = veiculo.cliente_id 
#     )

#     db.add(novo_veiculo)
#     db.commit()

#     return "Veiculo added"

