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
    quantidade: Optional[str] = None

class ServicoResponse(BaseModel):
    id   : int
    nome : str
    preco: float
    class Config:
        from_attributes = True

# Posso adicionar outro Response detalhado
# EX: Calculo total dentro do Schema do OS