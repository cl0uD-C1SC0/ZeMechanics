# Cenários de teste da Saga

Teste ponta a ponta da Saga com o `docker compose` no ar, usando o script [`scripts/testar-saga.sh`](../../scripts/testar-saga.sh).

## Como rodar

Na raiz do repositório:

```bash
bash scripts/testar-saga.sh              # cenários principais: feliz, falha, reprova
bash scripts/testar-saga.sh todos        # todos os seis
bash scripts/testar-saga.sh falha        # só um cenário
```

## Cenários

| Cenário | O que testa | Derruba algum container? |
|---|---|---|
| `feliz` | Orçamento → aprovação → execução → entrega | não |
| `falha` | Execução falha → estorno, peças devolvidas, OS cancelada | não |
| `reprova` | Cliente reprova → peças devolvidas, OS reprovada | não |
| `recusado` | Pagamento recusado (mock) → OS cancelada | reinicia o billing |
| `async` | Billing fora → mensagem espera na fila → é processada quando ele volta | para o billing |
| `rabbit` | RabbitMQ fora → 503, nada muda pela metade, e a Saga volta ao normal depois | para o RabbitMQ |
