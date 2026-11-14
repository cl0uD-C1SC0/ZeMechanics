import json
import pytest
import pika
from unittest.mock import patch, Mock
from fastapi import HTTPException

from app.messaging import rabbitmq


@patch("app.messaging.rabbitmq._conectar")
def test_publicar_declara_fila_com_dlq_e_envia(mock_conectar):
    channel = mock_conectar.return_value.channel.return_value

    rabbitmq.publicar("billing.commands", {"tipo": "GERAR_ORCAMENTO", "os_id": 1})

    filas = [c.kwargs["queue"] for c in channel.queue_declare.call_args_list]
    assert filas == ["billing.commands.dlq", "billing.commands"]
    kwargs = channel.basic_publish.call_args.kwargs
    assert kwargs["routing_key"] == "billing.commands"
    assert json.loads(kwargs["body"]) == {"tipo": "GERAR_ORCAMENTO", "os_id": 1}
    assert kwargs["properties"].delivery_mode == 2
    mock_conectar.return_value.close.assert_called_once()


@patch("app.messaging.rabbitmq._conectar")
def test_publicar_com_rabbitmq_fora_retorna_503(mock_conectar):
    mock_conectar.side_effect = pika.exceptions.AMQPConnectionError()

    with pytest.raises(HTTPException) as exc:
        rabbitmq.publicar("billing.commands", {"tipo": "X"})

    assert exc.value.status_code == 503


def test_processar_sucesso_faz_ack():
    handler, channel, method = Mock(), Mock(), Mock(delivery_tag=7)

    rabbitmq._processar(handler, channel, method, json.dumps({"tipo": "X", "os_id": 1}))

    handler.assert_called_once_with({"tipo": "X", "os_id": 1})
    channel.basic_ack.assert_called_once_with(delivery_tag=7)


def test_processar_erro_manda_para_dlq():
    handler, channel, method = Mock(side_effect=Exception("boom")), Mock(), Mock(delivery_tag=7)

    rabbitmq._processar(handler, channel, method, json.dumps({"tipo": "X"}))

    channel.basic_nack.assert_called_once_with(delivery_tag=7, requeue=False)
    channel.basic_ack.assert_not_called()


@patch("app.messaging.rabbitmq.time.sleep")
@patch("app.messaging.rabbitmq._conectar")
def test_consumir_reconecta_quando_rabbitmq_cai(mock_conectar, mock_sleep):
    channel = Mock()
    channel.start_consuming.side_effect = KeyboardInterrupt  # encerra o loop infinito no teste
    conexao = Mock()
    conexao.channel.return_value = channel
    mock_conectar.side_effect = [pika.exceptions.AMQPConnectionError(), conexao]

    with pytest.raises(KeyboardInterrupt):
        rabbitmq.consumir("os.events", Mock())

    mock_sleep.assert_called_once_with(5)
    assert channel.basic_consume.call_args.kwargs["queue"] == "os.events"


@patch("app.messaging.rabbitmq.threading.Thread")
def test_iniciar_consumidor_roda_em_thread(mock_thread):
    handler = Mock()

    rabbitmq.iniciar_consumidor("os.events", handler)

    assert mock_thread.call_args.kwargs["args"] == ("os.events", handler)
    assert mock_thread.call_args.kwargs["daemon"] is True
    mock_thread.return_value.start.assert_called_once()
