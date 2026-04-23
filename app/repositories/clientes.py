from app.domain.models.Cliente_model import Cliente as ClienteModel
from app.domain.models.Veiculo_model import Veiculo as VeiculoModel
from fastapi import HTTPException

def add_client(cliente, db):
    novo_cliente = ClienteModel(
        nome     = cliente.nome,
        cpf      = cliente.cpf,
        contato  = cliente.contato,
        endereco = cliente.endereco
    )
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    print("NOVO CLIENTE:", novo_cliente.id, novo_cliente.nome)
    return novo_cliente

def update_client_infos(cliente, dados, db):    
    for campo, valor in dados.model_dump(exclude_none=True).items():
        setattr(cliente, campo, valor)
    
    db.commit()
    db.refresh(cliente)
    return cliente

def delete_client(cpf, db):
    client_to_delete = db.query(ClienteModel).filter(ClienteModel.cpf == cpf).first()

    if client_to_delete:
        db.delete(client_to_delete)
        db.commit()
        return {"message": "Cliente removido"}

def transfer_client_vehicle(veiculo, novo_cliente, db):
    veiculo.cliente_id = novo_cliente.id
    db.commit()
    return {"message": "Veículo transferido com sucesso"}

def get_all_clients(db):
    clientes = db.query(ClienteModel).all()
    return clientes

def get_specific_client(cpf, db):
    cliente = db.query(ClienteModel).filter(ClienteModel.cpf == cpf).first()
    return cliente

def get_client_veichles(cpf, db):
    client_veichles = db.query(ClienteModel).filter(ClienteModel.cpf == cpf).first()
    return client_veichles
