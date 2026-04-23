from pydantic import BaseModel
from app.domain.enums.status_os import StatusOS

class OrdemDeServicoSchema(BaseModel):
    cliente_cpf: int
    veiculo_placa: str
    peca_ids     : list[int]
    servico_ids  : list[int]
    status_os: StatusOS = StatusOS.RECEBIDA


#     def calcular_total(self):
#         total_servicos = sum(s._preco for s in self._servicos)
#         total_pecas = sum(p._preco for p in self._pecas)

#         valor_total = float(total_servicos + total_pecas)

#         return f"{valor_total:.2f}"

#     def __str__(self):
#         servicos = [s._nome for s in self._servicos]
#         pecas = [p._nome for p in self._pecas]

#         return (
#             f"CLIENTE: {self._cliente}\n"
#             f"VEICULO: {self._veiculo}\n"
#             f"SERVIÇOS: {servicos}\n"
#             f"PEÇAS: {pecas}\n"
#             f"STATUS: {self._status_os}\n"
#             f"TOTAL: R${self.calcular_total()}"
#         )