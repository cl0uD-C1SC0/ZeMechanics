from pydantic import BaseModel
from typing import Optional

class ServicoSchema(BaseModel):
    nome: str
    preco: float
    descricao: str
class UpdateServiceSchema(BaseModel):
    nome: Optional[str] = None
    preco: Optional[str] = None
    descricao: Optional[str] = None

class ServicoResponse(BaseModel):
    id   : int
    nome : str
    preco: float
    class Config:
        from_attributes = True

class ConsultAllServicosSchema(BaseModel):
    id: int
    nome: str