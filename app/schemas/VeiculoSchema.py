from pydantic import BaseModel

class VeiculoSchema(BaseModel):
    modelo: str
    placa: str
    ano: str
    cliente_id: int

    # def __init__(self, modelo, placa, ano):
    #     self._modelo = modelo
    #     self._placa  = placa
    #     self._ano    = ano

    # def __str__(self):
    #     return f"Veiculo: {self._modelo}, {self._placa}, {self._ano}"