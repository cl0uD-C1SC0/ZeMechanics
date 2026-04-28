from app.repositories import OSRepository
from fastapi import HTTPException

from app.services import cliente_service as cliente_service
from app.services import PecaService as peca_service
from app.services import ServicosService as servico_service
from app.services import VeiculoService as veiculo_service

from app.domain.enums.StatusOS import StatusOS
from app.domain.enums.StatusOS import TRANSICAO_STATUS

def criar_nova_os(os, db):

    cliente = cliente_service.consultar_cliente(os.cliente_cpf, db)
    veiculo = veiculo_service.consultar_veiculo(os.veiculo_placa, db) 

    if not cliente:
        raise HTTPException(404, detail="Cliente não encontrado!")

    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado!")

    for peca_id in os.peca_ids:

        if not peca_service.consultar_peca_especifica(peca_id, db):
            raise HTTPException(404, f"A peça com ID: {peca_id} não foi encontrada no sistema")
        
    for servico_id in os.servico_ids:
        if not servico_service.consultar_servico_especifico(servico_id, db):
            raise HTTPException(404, f"O Serviço com ID: {servico_id} não foi encontrada no sistema")

    nova_os = OSRepository.create_new_os(cliente, veiculo, db)

    if nova_os:
        return {"message": f"Nova Ordem de Serviço foi criada, ID: {nova_os.id} "} 

def listar_todas_os(db):
    todas_os = OSRepository.get_all_os(db)
    if not todas_os:
        raise HTTPException(status_code=404, detail="Nenhuma Ordem de Serviço foi criada")
    return todas_os

def atualizar_os(os_id, dados, db):
    dados_dict = dados.model_dump(exclude_none=True)

    if "veiculo_placa" in dados_dict:
        veiculo = veiculo_service.consultar_veiculo(dados_dict.pop("veiculo_placa"), db)
        if not veiculo:
            raise HTTPException(status_code=404, detail="Veículo não encontrado")
        dados_dict["veiculo_id"] = veiculo.id  

    if "cliente_cpf" in dados_dict:
        cliente = cliente_service.consultar_cliente(dados_dict.pop("cliente_cpf"), db)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        dados_dict["cliente_id"] = cliente.id  

    os_atualizada = OSRepository.update_os(os_id, dados_dict, db)
    return {"message": f"OS {os_atualizada.id} atualizada com sucesso"}

def remover_os(os_id, db):
    os_consultada = OSRepository.get_specific_os(os_id, db)

    if not os_consultada:
        raise HTTPException(status_code=404, detail="OS não encontrada")

    if OSRepository.remove_os(os_id, db):
        return {"message": "OS Removida com sucesso"}
    raise HTTPException(status_code=500, detail="Não foi possível remover a OS, tente novamente.")

def consultar_os(os_id, db):
    os_consultada = OSRepository.get_specific_os(os_id, db)

    if not os_consultada:
        raise HTTPException(status_code=404, detail="OS não encontrada")
    
    return {"OS ID": os_consultada.id, "Status atual": os_consultada.status, "CPF": os_consultada.cliente.cpf} 

def avancar_os(os_id, db):
    os = consultar_os(os_id, db)
    
    if not os:
        raise HTTPException(status_code=404, detail="OS não encontrada")
    
    if os.status == StatusOS.AGUARDANDO_APROVACAO:
        raise HTTPException(status_code=400, detail="OS aguardando aprovação do cliente — use a rota /aprovar")
    
    proximo_status = TRANSICAO_STATUS.get(os.status)
    
    if not proximo_status:
        raise HTTPException(status_code=400, detail="OS já está no status final")
    
    return OSRepository.advance_os(os, proximo_status, db)

def aprovar_os(os_id, cliente_cpf, db):
    os = consultar_os(os_id, db)
    
    if not os:
        raise HTTPException(status_code=404, detail="OS não encontrada")
    
    if os.status != StatusOS.AGUARDANDO_APROVACAO:
        raise HTTPException(status_code=400, detail="OS não está aguardando aprovação")
    
    if str(os.cliente.cpf) != cliente_cpf:
        raise HTTPException(status_code=403, detail="CPF não autorizado")

    return OSRepository.approve_os(os, db)