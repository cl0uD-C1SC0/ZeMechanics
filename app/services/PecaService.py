from fastapi import HTTPException
from app.repositories import PecaRepository

def adicionar_peca(peca, db):
    return PecaRepository.add_peca(peca, db)

def listar_todas_pecas(db):
    return PecaRepository.get_all_pecas(db)

def consultar_peca_especifica(peca_id, db):
    peca = PecaRepository.describe_peca(peca_id, db)
    if not peca:
        raise HTTPException(status_code=404, detail=f"Peça com o ID: {peca_id} não foi encontrada no sistema")
    return peca 

def atualizar_peca_especifica(peca_id, dados, db):
    peca = consultar_peca_especifica(peca_id, db)

    if not peca:
        raise HTTPException(status_code=404, detail="Peça com esse ID não encontradoo")
    
    peca_atualizada = PecaRepository.update_peca(peca, dados, db)
    return peca_atualizada

def remover_peca(peca_id, db):
    if not consultar_peca_especifica(peca_id, db):
        raise HTTPException(status_code=404, detail="Peça com esse ID não encontradoo")
    
    return PecaRepository.delete_peca(peca_id, db)

def adicionar_ao_estoque(peca_id, qtd_adicionar, db):
    if not consultar_peca_especifica(peca_id, db):
        raise HTTPException(status_code=404, detail="Peça com esse ID não encontrado")
    
    add_qtd = PecaRepository.add_peca_amount(peca_id, qtd_adicionar, db)

    return add_qtd

def remover_do_estoque(peca_id, qtd_remover, db):
    if not consultar_peca_especifica(peca_id, db):
        raise HTTPException(status_code=404, detail="Peça com esse ID não encontradoo")
    
    remove_qtd = PecaRepository.remove_peca_amount(peca_id, qtd_remover, db)

    return remove_qtd