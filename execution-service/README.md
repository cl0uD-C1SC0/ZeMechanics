# execution-service

Microsserviço de **Execução e Produção** da Ze Mechanics: a fila da oficina, o diagnóstico e o reparo. É um **participante da Saga**: recebe comandos do os-service e responde com eventos.

## Responsabilidades

* Gerenciar a fila de execução das OS.
* Atualizar o status durante o diagnóstico e o reparo.
* Comunicar a finalização ao os-service.
* Comunicar falhas na execução, o que dispara a compensação da Saga (estorno e devolução de peças).

## Arquitetura

```
app/
├── api/v1/          rotas (FastAPI): execução, health
├── services/        execucao_service (comandos da Saga + ações do mecânico)
├── repositories/    acesso ao MongoDB (pymongo)
├── domain/enums/    StatusExecucao
└── messaging/
    └── rabbitmq.py  publicar / consumir filas (pika)
```

### Comunicação

| Fila | Direção | Mensagens |
|---|---|---|
| `execution.commands` | **consome** (comandos do os-service) | `EXECUTAR_OS` |
| `os.events` | **publica** (respostas para o os-service) | `EXECUCAO_INICIADA`, `EXECUCAO_FINALIZADA`, `EXECUCAO_FALHOU` |

**Idempotência:** um `EXECUTAR_OS` repetido não coloca a mesma OS na fila duas vezes.

### Status da execução

```
Na Fila → Em Diagnóstico → Em Reparo → Finalizada   (avisa o os-service)
   └──────────┴───────────────┴──────→ Falhou       (dispara a compensação)
```

## Banco de dados

**MongoDB** (NoSQL), banco `execution_db`, coleção `execucoes`.

Uma execução é naturalmente um documento: a OS, os serviços a fazer e o histórico ficam juntos, sem JOIN.

```json
{
  "os_id": 1,
  "veiculo_placa": "FGV1412",
  "servicos": ["Troca de Óleo"],
  "status": "Em Reparo",
  "criado_em": "2026-11-14T10:00:00Z",
  "historico": [
    { "status": "Na Fila",        "evento": "Entrou na fila",     "data": "..." },
    { "status": "Em Diagnóstico", "evento": "Avanço do mecânico", "data": "..." },
    { "status": "Em Reparo",      "evento": "Avanço do mecânico", "data": "..." }
  ]
}
```

## Endpoints

Prefixo: `/api/v1` · Swagger: `http://localhost:8003/docs`

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/execucao/fila` | Listar a fila (na fila, em diagnóstico, em reparo), da mais antiga para a mais nova |
| `GET` | `/execucao/{os_id}` | Consultar a execução da OS e seu histórico |
| `PATCH` | `/execucao/{os_id}/avancar` | Avançar a execução (ao finalizar, avisa o os-service) |
| `PATCH` | `/execucao/{os_id}/falhar?motivo=` | Marcar falha (dispara a compensação da Saga) |
| `GET` | `/health/live` | Liveness probe |
| `GET` | `/health/ready` | Readiness probe (testa o MongoDB) |

## Variáveis de ambiente

| Variável | Exemplo | Descrição |
|---|---|---|
| `MONGO_URL` | `mongodb://mongo:27017` | Conexão com o MongoDB |
| `MONGO_DB` | `execution_db` | Nome do banco |
| `RABBITMQ_URL` | `amqp://guest:guest@rabbitmq:5672/%2F` | Sem ela, o consumidor não é iniciado |

## Como rodar

Com o restante do ambiente, a partir da raiz do projeto: `docker compose up --build -d`.

Só este serviço:

```bash
docker build -t execution-service .
docker run -p 8003:8000 -e MONGO_URL=... -e RABBITMQ_URL=... execution-service
```

## Testes

Os testes usam `mongomock` (MongoDB em memória), então não precisam de um Mongo rodando.

```bash
pip install -r requirements.txt
pytest --cov=app --cov-report=term
```

### Cobertura

```
TOTAL    197 stmts    7 miss    96%
24 passed
```

| Módulo | Cobertura |
|---|---|
| `services/execucao_service.py` | 100% |
| `repositories/ExecucaoRepository.py` | 100% |
| `api/v1/execucao_api.py` | 100% |
| `messaging/rabbitmq.py` | 98% |
