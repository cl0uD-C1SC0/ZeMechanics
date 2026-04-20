class Servico:
    def __init__(self, nome, preco):
        self._nome  = nome
        self._preco = preco

    def __str__(self):
        return f"Peça: {self._nome}, Preço {self._preco}"