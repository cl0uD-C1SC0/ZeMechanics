from app.domain.models.Servico_model import Servicos as ServicoModel
from fastapi import HTTPException



def add_mechanic_service(service, db):
    novo_servico = ServicoModel(
        nome = service.nome,
        preco = service.preco,
        descricao = service.descricao
    )
    db.add(novo_servico)
    db.commit()
    db.refresh(novo_servico)

    return novo_servico

def get_all_services(db):
    servicos = db.query(ServicoModel).all()
    
    if servicos:
        return servicos
    raise HTTPException(status_code=404, detail="Nenhum serviço cadastrado")

def describe_service(servico_id, db):
    servico = db.query(ServicoModel).filter(ServicoModel.id == servico_id).first()
    return servico

def update_service(servico, dados, db):
    for campo, valor in dados.model_dump(exclude_none=True).items():
        setattr(servico, campo, valor)

    db.commit()
    db.refresh(servico)
    return {"message": f"Serviço {servico.id} atualizado com sucesso"}

def delete_service(servico_id, db):
    servico = db.query(ServicoModel).filter(ServicoModel.id == servico_id).first()

    if not servico:
        raise HTTPException(status_code=404, detail="Serviço com esse ID não foi encontrado")
    
    db.delete(servico)
    db.commit()

    return {"message": "Serviço removido com sucesso"}

