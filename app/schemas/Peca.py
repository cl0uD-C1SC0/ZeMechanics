from pydantic import BaseModel

class PecaSchema(BaseModel):
    nome: str
    preco: float
    quantidade: int

class PecaResponse(BaseModel):
    id   : int
    nome : str
    preco: float
    quantidade: int

    class Config:
        from_attributes = True