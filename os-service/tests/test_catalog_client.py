import pytest
import httpx
from unittest.mock import patch, Mock
from fastapi import HTTPException

from app.clients import catalog_client


def _response(status_code, json_data):
    response = Mock()
    response.status_code = status_code
    response.json.return_value = json_data
    return response


@patch("app.clients.catalog_client.httpx.request")
def test_consultar_peca_sucesso(mock_request):
    mock_request.return_value = _response(200, {"id": 1, "nome": "Motor"})

    result = catalog_client.consultar_peca(1)

    assert result["nome"] == "Motor"
    assert mock_request.call_args.args[0] == "GET"
    assert mock_request.call_args.args[1].endswith("/api/v1/peca/consultar_peca/1")


@patch("app.clients.catalog_client.httpx.request")
def test_baixar_estoque_envia_quantidade(mock_request):
    mock_request.return_value = _response(200, {"message": "ok"})

    catalog_client.baixar_estoque(1, 3)

    assert mock_request.call_args.args[0] == "PATCH"
    assert mock_request.call_args.kwargs["params"] == {"quantidade": 3}


@patch("app.clients.catalog_client.httpx.request")
def test_devolver_estoque(mock_request):
    mock_request.return_value = _response(200, {"message": "ok"})

    catalog_client.devolver_estoque(1, 2)

    assert mock_request.call_args.args[1].endswith("/api/v1/peca/adicionar_quantidade/1")


@patch("app.clients.catalog_client.httpx.request")
def test_consultar_servico(mock_request):
    mock_request.return_value = _response(200, {"id": 1, "nome": "Alinhamento"})

    result = catalog_client.consultar_servico(1)

    assert result["nome"] == "Alinhamento"


@patch("app.clients.catalog_client.httpx.request")
def test_erro_do_catalogo_repassa_status(mock_request):
    mock_request.return_value = _response(400, {"detail": "Estoque insuficiente"})

    with pytest.raises(HTTPException) as exc:
        catalog_client.baixar_estoque(1, 99)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Estoque insuficiente"


@patch("app.clients.catalog_client.httpx.request")
def test_catalogo_fora_do_ar_retorna_503(mock_request):
    mock_request.side_effect = httpx.ConnectError("connection refused")

    with pytest.raises(HTTPException) as exc:
        catalog_client.consultar_peca(1)

    assert exc.value.status_code == 503
