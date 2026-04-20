

"""
Antes a minha classe ficava assim
"""

# class Cliente:
#     def __init__(self, nome, contato, endereco, cpf):
#         self._nome     = nome
#         self._contato  = contato
#         self._endereco = endereco
#         self._cpf      = cpf


#     def __str__(self):
#         return f"Cliente: {self._nome}, {self._cpf}, {self._endereco}"

"""
Com o uso do pydantic, ele valida a entrada e retorna o JSON:
"""
from pydantic import BaseModel

class ClienteSchema(BaseModel):
    nome: str
    cpf: str
    endereco: str
    contato: str