from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrdemDeServicoSchema(BaseModel):
    cliente_cpf: int
    veiculo_placa: str

class OSUpdateSchema(BaseModel):
    cliente_cpf: Optional[int] = None
    veiculo_placa: Optional[str] = None

class ClienteResumo(BaseModel):
    id: int
    nome: str
    cpf: str
    class Config:
        from_attributes = True
class VeiculoResumo(BaseModel):
    id: int
    marca: str
    modelo: str
    placa: str
    
    class Config:
        from_attributes = True
class OSResponse(BaseModel):
    id: int
    status: str
    criado_em: datetime
    cliente: ClienteResumo
    veiculo: VeiculoResumo

    class Config:
        from_attributes = True