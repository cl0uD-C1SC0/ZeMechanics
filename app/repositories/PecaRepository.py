from app.domain.models.Peca_model import Peca as PecaModel
from fastapi import HTTPException

def add_peca(peca, db):
    nova_peca = PecaModel(
        nome = peca.nome,
        preco = peca.preco,
        quantidade = peca.quantidade
    )
    db.add(nova_peca)
    db.commit()
    db.refresh(nova_peca)

    return nova_peca

def get_all_pecas(db):
    pecas = db.query(PecaModel).all()

    if pecas:
        return pecas
    raise HTTPException(status_code=404, detail="Nenhma peça cadastrada")

def describe_peca(peca_id, db):
    peca = db.query(PecaModel).filter(PecaModel.id == peca_id).first()
    return peca

def update_peca(peca, dados, db):
    for campo, valor in dados.model_dump(exclude_none=True).items():
        setattr(peca, campo, valor)

    db.commit()
    db.refresh(peca)
    return {"message": f"Peça {peca.id} atualizada com sucesso"}

def delete_peca(peca_id, db):
    peca = db.query(PecaModel).filter(PecaModel.id == peca_id).first()

    if not peca:
        raise HTTPException(status_code=404, detail="Peça com esse ID não foi encontrada")

    db.delete(peca)
    db.commit()

    return {"message": "Peça removida com sucesso"}

def add_peca_amount(peca_id, qtd_adicionar, db):
    peca = db.query(PecaModel).filter(PecaModel.id == peca_id).first()

    if not peca:
        raise HTTPException(status_code=404, detail="Serviço com esse ID não foi encontrado")
    
    peca.quantidade += qtd_adicionar
    db.commit()
    db.refresh(peca)
    return {"message": f"Adicionado {qtd_adicionar} unidade(s) no serviço {peca.nome}"}

def remove_peca_amount(peca_id, qtd_remover, db):
    peca = db.query(PecaModel).filter(PecaModel.id == peca_id).first()

    if not peca:
        raise HTTPException(status_code=404, detail="Serviço com esse ID não foi encontrado")
    
    peca.quantidade -= qtd_remover
    db.commit()
    db.refresh(peca)
    return {"message": f"Removido {qtd_remover} unidade(s) do serviço {peca.nome}"}

