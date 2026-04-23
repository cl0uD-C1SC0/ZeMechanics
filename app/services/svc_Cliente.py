from app.repositories import clientes
from fastapi import HTTPException
from app.repositories import veiculos

def validar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        print("> CPF Inválido, tente novamente..")
        return False
    
    if cpf == cpf[0] * 11:
        print("> CPF Inválido, tente novamente..")
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    digito1 = 0 if resto == 10 else resto

    if digito1 != int(cpf[9]):
        print("> CPF Inválido, tente novamente..")
        return False

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    digito2 = 0 if resto == 10 else resto

    if digito2 != int(cpf[10]):
        print("> CPF Inválido, tente novamente..")
        return False
    
    print("> CPF Válido!")
    return True

def cliente_existe(cpf, db):
    return clientes.get_specific_client(cpf, db) is not None

def cadastrar_cliente(cliente, db):
    if cliente_existe(cliente.cpf, db):
        raise HTTPException(status_code=409, detail="CPF Encontrado no sistema, tente novamente.")
    
    if not validar_cpf(cliente.cpf):
        raise HTTPException(status_code=422, detail="CPF inválido")
    
    result = clientes.add_client(cliente, db)
    return result

def listar_clientes(db):
    return clientes.get_all_clients(db)

def listar_veiculos_cliente(cpf, db):
    cliente_veiculos = clientes.get_client_veichles(cpf, db) or None

    if not cliente_existe(cpf, db):
        raise HTTPException(status_code=404, detail="Cliente com esse CPF não encontrado")
    
    if not cliente_veiculos:
        raise HTTPException(status_code=404, detail="Cliente não tem veículos cadastrados")
    
    return cliente_veiculos

def remover_cliente(cpf, db):
    if not cliente_existe(cpf, db):
        raise HTTPException(status_code=404, detail="Cliente com esse CPF não encontrado")
    
    return clientes.delete_client(cpf, db)

def transferir_veiculo_cliente(placa, novo_cpf, db):
    if not cliente_existe(novo_cpf, db):
        raise HTTPException(status_code=404, detail="Cliente com esse CPF não encontrado")

    novo_cliente = clientes.get_specific_client(novo_cpf, db)
    veiculo      = veiculos.get_vehicle(placa, db)

    veiculo_transferido = clientes.transfer_client_vehicle(veiculo, novo_cliente, db)
    return veiculo_transferido

def atualizar_informacao_cliente(cpf, dados, db):
    if not cliente_existe(cpf, db):
        raise HTTPException(status_code=404, detail="Cliente com esse CPF não encontrado")

    cliente = clientes.get_specific_client(cpf, db)
    dados_atualizados = clientes.update_client_infos(cliente, dados, db)
    return dados_atualizados

def consultar_cliente(cpf, db):
    if not cliente_existe(cpf, db):
        raise HTTPException(status_code=404, detail="Cliente com esse CPF não encontrado")
    
    return clientes.get_specific_client(cpf, db)