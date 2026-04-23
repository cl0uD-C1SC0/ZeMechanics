from pydantic import BaseModel
from app.schemas.VeiculoSchema import ConsultClientVeiculoResponse
from typing import Optional

class ClienteSchema(BaseModel):
    nome: str
    cpf: str
    endereco: str
    contato: str

class ClienteUpdateSchema(BaseModel):
    nome: Optional[str] = None
    endereco: Optional[str] = None
    contato: Optional[str] = None


class AddClientResponse(BaseModel):
    id: int
    nome: str
    message: str
    
    class Config:
        from_attributes = True
class ConsultClientResponse(BaseModel):
    id: int
    nome: str
    cpf: str
    contato: str
    endereco: str
    veiculos: list[ConsultClientVeiculoResponse]

    class Config:
        from_attributes = True