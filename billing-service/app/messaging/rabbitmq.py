import json
import logging
import os
import threading
import time

import pika
from fastapi import HTTPException

# Mensageria assíncrona (RabbitMQ) - "caixa de correio" entre os serviços.
#
# Filas usadas no projeto:
#   billing.commands    -> o os-service pede algo ao billing  (consumida pelo billing)
#   execution.commands  -> o os-service pede algo à execução  (consumida pelo execution)
#   os.events           -> billing/execution respondem       (consumida pelo os-service)
#
# Toda fila tem uma DLQ (<fila>.dlq): mensagem que deu erro no processamento vai
# para lá em vez de se perder ou travar a fila.

logger = logging.getLogger("rabbitmq")

RABBITMQ_URL = os.getenv("RABBITMQ_URL")


def _conectar():
    return pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))


def _declarar_fila(channel, fila):
    channel.queue_declare(queue=f"{fila}.dlq", durable=True)
    channel.queue_declare(
        queue=fila,
        durable=True,
        arguments={
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": f"{fila}.dlq",
        },
    )


def publicar(fila, mensagem):
    try:
        conexao = _conectar()
        channel = conexao.channel()
        _declarar_fila(channel, fila)
        channel.basic_publish(
            exchange="",
            routing_key=fila,
            body=json.dumps(mensagem),
            properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
        )
        conexao.close()
    except pika.exceptions.AMQPError:
        raise HTTPException(status_code=503, detail="RabbitMQ indisponível, tente novamente")

    logger.info(f"[publicado] {fila} -> {mensagem}")


def _processar(handler, channel, method, body):
    mensagem = json.loads(body)
    try:
        logger.info(f"[recebido] {mensagem}")
        handler(mensagem)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception(f"[erro] mensagem enviada para a DLQ: {mensagem}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def consumir(fila, handler):
    while True:
        try:
            conexao = _conectar()
            channel = conexao.channel()
            _declarar_fila(channel, fila)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue=fila,
                on_message_callback=lambda ch, method, props, body: _processar(handler, ch, method, body),
            )
            logger.info(f"[consumidor] ouvindo a fila {fila}")
            channel.start_consuming()
        except pika.exceptions.AMQPError:
            logger.warning("[consumidor] RabbitMQ indisponível, tentando de novo em 5s")
            time.sleep(5)


def iniciar_consumidor(fila, handler):
    threading.Thread(target=consumir, args=(fila, handler), daemon=True).start()
