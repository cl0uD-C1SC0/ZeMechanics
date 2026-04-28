from fastapi import HTTPException
from app.repositories import ServicosRepository

def adicionar_servico(servico, db):
    return ServicosRepository.add_mechanic_service(servico, db)

def listar_todos_servicos(db):
    return ServicosRepository.get_all_services(db)

def consultar_servico_especifico(servico_id, db):
    servico = ServicosRepository.describe_service(servico_id, db)
    if not servico:
        raise HTTPException(status_code=404, detail=f"Serviço com o ID: {servico_id} não foi encontrado no sistema")
    return servico 

def atualizar_servico_especifico(servico_id, dados, db):
    servico = consultar_servico_especifico(servico_id, db)

    if not servico:
        raise HTTPException(status_code=404, detail=f"Serviço com o ID: {servico_id} não foi encontrado no sistema")
    
    servico_atualizado = ServicosRepository.update_service(servico, dados, db)
    return servico_atualizado

def remover_servico(servico_id, db):
    if not consultar_servico_especifico(servico_id, db):
        raise HTTPException(status_code=404, detail="Serviço com esse ID não encontrado")
    
    return ServicosRepository.delete_service(servico_id, db)