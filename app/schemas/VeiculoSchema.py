from pydantic import BaseModel, Field
from typing import Optional
class VeiculoSchema(BaseModel):
    modelo: str
    marca: str
    placa: str
    ano: str
    cliente_id: int

class AddVehicleReponse(BaseModel):
    id: int
    cliente_id: int
    marca: str
    modelo: str
    placa: str
    ano: str
    class Config:
        from_attributes = True

class UpdateVehicleSchema(BaseModel):
    modelo: Optional[str] = None
    marca: Optional[str] = None
    ano: Optional[str] = None

class ConsultClientVeiculoResponse(BaseModel):
    veiculo_id: Optional[int] = Field(default=None, alias="id")
    marca: Optional[str] = None
    modelo: Optional[str] = None
    placa: Optional[str] = None
    ano: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True