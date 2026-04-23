from enum import Enum

class StatusOS(str, Enum):
    RECEBIDA                = "Recebida"
    EM_DIAGNOSTICO          = "Em Diagnóstico"
    AGUARDANDO_APROVACAO    = "Aguardando Aprovação"
    EM_EXECUCAO             = "Em Execução"
    FINALIZADA              = "Finalizada"
    ENTREGUE                = "Entregue"