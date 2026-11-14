from enum import Enum

class StatusOrcamento(str, Enum):
    AGUARDANDO_APROVACAO = "Aguardando Aprovação"
    APROVADO             = "Aprovado"
    REPROVADO            = "Reprovado"
    PAGAMENTO_RECUSADO   = "Pagamento Recusado"
    ESTORNADO            = "Estornado"

class StatusPagamento(str, Enum):
    APROVADO  = "Aprovado"
    RECUSADO  = "Recusado"
    ESTORNADO = "Estornado"
