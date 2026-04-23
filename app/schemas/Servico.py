from pydantic import BaseModel

class ServicoSchema(BaseModel):
    nome: str
    preco: float
    descricao: str

class ServicoResponse(BaseModel):
    id   : int
    nome : str
    preco: float

    class Config:
        from_attributes = True

# Posso adicionar outro Response detalhado
# EX: Calculo total dentro do Schema do OS