from pydantic import BaseModel
from typing import Optional
class PecaSchema(BaseModel):
    nome: str
    preco: float
    quantidade: int

class UpdatePecaSchema(BaseModel):
    nome: Optional[str] = None
    preco: Optional[str] = None
    

class PecaResponse(BaseModel):
    id   : int
    nome : str
    preco: float
    quantidade: int

    class Config:
        from_attributes = True

class ConsultAllPecasSchema(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True