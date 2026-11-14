import os
import uuid

# MOCK do gateway de pagamento (Mercado Pago).
#
# As respostas imitam o formato do Mercado Pago (id + status "approved",
# "rejected", "refunded"). Quando a integração real for feita, só este arquivo
# muda — o resto do billing continua igual.
#
# Para demonstrar a Saga com pagamento recusado:
#   MOCK_PAGAMENTO_STATUS=rejected


def processar_pagamento(valor, descricao):
    status = os.getenv("MOCK_PAGAMENTO_STATUS", "approved")
    return {
        "id": f"mock-{uuid.uuid4()}",
        "status": status,
        "status_detail": "accredited" if status == "approved" else "cc_rejected_other_reason",
        "transaction_amount": valor,
        "description": descricao,
    }


def estornar_pagamento(pagamento_id):
    return {"id": pagamento_id, "status": "refunded"}
