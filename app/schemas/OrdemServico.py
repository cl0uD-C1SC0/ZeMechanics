

class OrdemServico:
    def __init__(self, cliente, veiculo):
        self._cliente        = cliente
        self._veiculo        = veiculo
        self._servicos       = []
        self._pecas          = []
        self._status_os      = 'Recebida'

    def adicionar_peca(self, peca):
        self._pecas.append(peca)

    def adicionar_servico(self, servico):
        self._servicos.append(servico)

    def calcular_total(self):
        total_servicos = sum(s._preco for s in self._servicos)
        total_pecas = sum(p._preco for p in self._pecas)

        valor_total = float(total_servicos + total_pecas)

        return f"{valor_total:.2f}"

    def __str__(self):
        servicos = [s._nome for s in self._servicos]
        pecas = [p._nome for p in self._pecas]

        return (
            f"CLIENTE: {self._cliente}\n"
            f"VEICULO: {self._veiculo}\n"
            f"SERVIÇOS: {servicos}\n"
            f"PEÇAS: {pecas}\n"
            f"STATUS: {self._status_os}\n"
            f"TOTAL: R${self.calcular_total()}"
        )