from app.domain.models.Veiculo import Veiculo as VeiculoModel

def consultar_veiculo(placa, db):
    placa_consultada = db.query(VeiculoModel).filter(VeiculoModel.placa == placa).first()

    if placa_consultada:
        return False
    
    return True

def add_veiculo():
    ...
#     novo_veiculo = VeiculoModel(
#         modelo      = veiculo.modelo,
#         placa       = veiculo.placa,
#         ano         = veiculo.ano,
#         cliente_id  = veiculo.cliente_id 
#     )

#     db.add(novo_veiculo)
#     db.commit()