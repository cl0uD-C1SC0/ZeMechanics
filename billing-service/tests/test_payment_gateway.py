from unittest.mock import patch

from app.clients import payment_gateway


def test_pagamento_aprovado_por_padrao():
    pagamento = payment_gateway.processar_pagamento(211.8, "OS #1")

    assert pagamento["status"] == "approved"
    assert pagamento["status_detail"] == "accredited"
    assert pagamento["transaction_amount"] == 211.8
    assert pagamento["id"].startswith("mock-")


@patch.dict("os.environ", {"MOCK_PAGAMENTO_STATUS": "rejected"})
def test_pagamento_recusado_por_configuracao():
    pagamento = payment_gateway.processar_pagamento(211.8, "OS #1")

    assert pagamento["status"] == "rejected"
    assert pagamento["status_detail"] == "cc_rejected_other_reason"


def test_estorno():
    assert payment_gateway.estornar_pagamento("mock-1") == {"id": "mock-1", "status": "refunded"}
