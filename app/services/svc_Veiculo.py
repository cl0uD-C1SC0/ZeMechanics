from app.repositories.veiculos import consultar_veiculo, add_veiculo

def consultar_placa(placa: str, db):
    consultar_veiculo(placa, db) # renomear essa funcao depois, ta esquisito