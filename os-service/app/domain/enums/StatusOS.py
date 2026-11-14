from enum import Enum

class StatusOS(str, Enum):
    RECEBIDA                = "Recebida"
    EM_DIAGNOSTICO          = "Em Diagnóstico"
    AGUARDANDO_APROVACAO    = "Aguardando Aprovação"
    REPROVADA               = "Reprovada"
    EM_EXECUCAO             = "Em Execução"
    FINALIZADA              = "Finalizada"
    ENTREGUE                = "Entregue"
    CANCELADA               = "Cancelada"

# Transições feitas MANUALMENTE pela rota /avancar do os-service.
# As demais (aprovação, execução, finalização, cancelamento) chegam
# por eventos dos outros serviços e são tratadas pela Saga (saga_service.py).
TRANSICAO_STATUS = {
    StatusOS.RECEBIDA        : StatusOS.EM_DIAGNOSTICO,
    StatusOS.EM_DIAGNOSTICO  : StatusOS.AGUARDANDO_APROVACAO,
    StatusOS.FINALIZADA      : StatusOS.ENTREGUE,
}

STATUS_ENCERRADOS = [StatusOS.ENTREGUE, StatusOS.REPROVADA, StatusOS.CANCELADA]
