from enum import Enum

class StatusExecucao(str, Enum):
    NA_FILA        = "Na Fila"
    EM_DIAGNOSTICO = "Em Diagnóstico"
    EM_REPARO      = "Em Reparo"
    FINALIZADA     = "Finalizada"
    FALHOU         = "Falhou"

TRANSICAO_STATUS = {
    StatusExecucao.NA_FILA        : StatusExecucao.EM_DIAGNOSTICO,
    StatusExecucao.EM_DIAGNOSTICO : StatusExecucao.EM_REPARO,
    StatusExecucao.EM_REPARO      : StatusExecucao.FINALIZADA,
}

STATUS_ABERTOS = [StatusExecucao.NA_FILA, StatusExecucao.EM_DIAGNOSTICO, StatusExecucao.EM_REPARO]
