# billing-service

Microsserviço de **Orçamento e Pagamento** da Ze Mechanics. É um **participante da Saga**: recebe comandos do os-service e responde com eventos.

## Responsabilidades

* Gerar o orçamento da OS e enviar o e-mail de aprovação ao cliente.
* Página de aprovação: o cliente aprova e paga, ou recusa.
* Processar o pagamento (**Mercado Pago, mock por enquanto**) e registrar cada lançamento.
* Estornar o pagamento quando a Saga pede (compensação).

## Arquitetura

```
app/
├── api/v1/            rotas (FastAPI): orçamento, health
├── services/
│   ├── orcamento_service.py   comandos da Saga + ações do cliente
│   └── EmailService.py        e-mail de aprovação (SMTP)
├── repositories/      acesso ao MySQL (SQLAlchemy)
├── domain/            models (Orcamento, Pagamento) e enums
├── clients/
│   └── payment_gateway.py     gateway de pagamento (mock do Mercado Pago)
└── messaging/
    └── rabbitmq.py            publicar / consumir filas (pika)
```

### Comunicação

| Fila | Direção | Mensagens |
|---|---|---|
| `billing.commands` | **consome** (comandos do os-service) | `GERAR_ORCAMENTO`, `ESTORNAR_PAGAMENTO` |
| `os.events` | **publica** (respostas para o os-service) | `ORCAMENTO_GERADO`, `PAGAMENTO_APROVADO`, `PAGAMENTO_RECUSADO`, `ORCAMENTO_REPROVADO`, `PAGAMENTO_ESTORNADO` |

O billing **não acessa o banco do os-service**: tudo o que ele precisa da OS (cliente, itens, total) chega na mensagem `GERAR_ORCAMENTO` e é guardado no próprio banco.

**Idempotência:** um `GERAR_ORCAMENTO` repetido não cria um segundo orçamento nem reenvia o e-mail; um `ESTORNAR_PAGAMENTO` repetido só reenvia a confirmação.

### Pagamento (mock)

[`payment_gateway.py`](app/clients/payment_gateway.py) imita as respostas do Mercado Pago (`approved`, `rejected`, `refunded`). Na integração real, só esse arquivo muda.

```bash
# simular cartão recusado
MOCK_PAGAMENTO_STATUS=rejected docker compose up -d billing-service
```

## Banco de dados

**MySQL**, schema `billing_db`, acessado apenas pelo usuário `billing_user`.

| Tabela | Conteúdo |
|---|---|
| `orcamentos` | OS, cliente, itens (JSON), valor total e status |
| `pagamentos` | Cada lançamento: aprovado, recusado ou estornado. O estorno é um **novo lançamento**, nunca apaga o anterior. |

## Endpoints

Prefixo: `/api/v1` · Swagger: `http://localhost:8002/docs`

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/orcamento/orcamentos` | Listar todos os orçamentos |
| `GET` | `/orcamento/{os_id}` | Consultar o orçamento da OS e seus pagamentos |
| `GET` | `/orcamento/{os_id}/aprovar?cliente_cpf=` | Página de aprovação (link enviado por e-mail) |
| `POST` | `/orcamento/{os_id}/confirmar_aprovacao?cliente_cpf=` | Aprovar e pagar |
| `POST` | `/orcamento/{os_id}/reprovar?cliente_cpf=` | Reprovar o orçamento |
| `GET` | `/health/live` | Liveness probe |
| `GET` | `/health/ready` | Readiness probe (testa o MySQL) |

## Variáveis de ambiente

| Variável | Exemplo | Descrição |
|---|---|---|
| `DATABASE_URL` | `mysql+pymysql://billing_user:billing_pass@mysql:3306/billing_db` | Conexão com o MySQL |
| `RABBITMQ_URL` | `amqp://guest:guest@rabbitmq:5672/%2F` | Sem ela, o consumidor não é iniciado |
| `MAIL_SERVER_ADDRESS` | `maildev` | Servidor SMTP (porta 1025) |
| `BILLING_PUBLIC_URL` | `http://localhost:8002` | Endereço usado no link do e-mail |
| `MOCK_PAGAMENTO_STATUS` | `approved` ou `rejected` | Resultado do pagamento simulado |

## Como rodar

Com o restante do ambiente, a partir da raiz do projeto: `docker compose up --build -d`.

Só este serviço:

```bash
docker build -t billing-service .
docker run -p 8002:8000 -e DATABASE_URL=... -e RABBITMQ_URL=... -e MAIL_SERVER_ADDRESS=... billing-service
```

## Testes

```bash
pip install -r requirements.txt
DATABASE_URL="sqlite:///./test.db" pytest --cov=app --cov-report=term
```

### Cobertura

```
TOTAL    310 stmts    13 miss    96%
42 passed
```

| Módulo | Cobertura |
|---|---|
| `services/orcamento_service.py` | 100% |
| `repositories/OrcamentoRepository.py` | 100% |
| `clients/payment_gateway.py` | 100% |
| `api/v1/orcamento_api.py` | 100% |
