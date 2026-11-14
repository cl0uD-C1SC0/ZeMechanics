# os-service

Microsserviço de **Ordens de Serviço** da Ze Mechanics: clientes, veículos, abertura e acompanhamento da OS e o **orquestrador da Saga**.

## Responsabilidades

* Cadastro de clientes e veículos.
* Abertura da OS, inclusão e remoção de peças e serviços.
* Atualização de status da OS e consulta de status e **histórico**.
* **Orquestração da Saga**: coordena billing-service e execution-service e dispara as compensações quando algo falha.

## Arquitetura

```
app/
├── api/v1/            rotas (FastAPI)
├── services/          regras de negócio
│   ├── OSService.py       OS: abrir, avançar, itens, histórico
│   └── saga_service.py    orquestrador da Saga (eventos de os.events)
├── repositories/      acesso ao MySQL (SQLAlchemy)
├── domain/            models e enums (StatusOS)
├── clients/
│   └── catalog_client.py  chamadas REST ao catalog-service
└── messaging/
    └── rabbitmq.py        publicar / consumir filas (pika)
```

### Comunicação

| Com quem | Como | O quê |
|---|---|---|
| catalog-service | **REST** (síncrono, timeout 5s) | Consultar peça e serviço, baixar e devolver estoque. Se o catálogo estiver fora, responde `503`. |
| billing-service | **RabbitMQ**: publica em `billing.commands` | `GERAR_ORCAMENTO`, `ESTORNAR_PAGAMENTO` |
| execution-service | **RabbitMQ**: publica em `execution.commands` | `EXECUTAR_OS` |
| billing + execution | **RabbitMQ**: consome `os.events` | `ORCAMENTO_GERADO`, `PAGAMENTO_APROVADO`, `PAGAMENTO_RECUSADO`, `ORCAMENTO_REPROVADO`, `PAGAMENTO_ESTORNADO`, `EXECUCAO_INICIADA`, `EXECUCAO_FINALIZADA`, `EXECUCAO_FALHOU` |

As peças e serviços pertencem ao catalog-service. A OS guarda apenas o ID e uma "foto" (nome e preço) do momento em que o item entrou, então consultar uma OS não depende do catálogo estar no ar.

## Saga (orquestrada)

O os-service é o **maestro** do fluxo da OS. Ele pede (comandos) e escuta as respostas (eventos). Para cada resposta, decide o próximo passo ou dispara as compensações.

```
Recebida → Em Diagnóstico → Aguardando Aprovação ──(GERAR_ORCAMENTO)──> billing
                                   │
             PAGAMENTO_APROVADO ───┤──(EXECUTAR_OS)──> execution
             EXECUCAO_INICIADA ────┤→ Em Execução
             EXECUCAO_FINALIZADA ──┤→ Finalizada → Entregue
                                   │
   compensações:                   │
             ORCAMENTO_REPROVADO ──┤→ devolve peças → Reprovada
             PAGAMENTO_RECUSADO ───┤→ devolve peças → Cancelada
             EXECUCAO_FALHOU ──────┤──(ESTORNAR_PAGAMENTO)──> billing
             PAGAMENTO_ESTORNADO ──┘→ devolve peças → Cancelada
```

**Por que orquestração (e não coreografia):**

* O fluxo tem um dono claro, a OS, então faz sentido um único serviço conhecer a sequência inteira.
* As regras de avanço e de compensação ficam em um único arquivo ([`saga_service.py`](app/services/saga_service.py)), fácil de ler e testar (100% de cobertura).
* Cada passo fica gravado no histórico da OS, o que responde "onde a OS travou?" com uma chamada.
* O billing e o execution não se conhecem: só recebem comandos e respondem com eventos.
* O orquestrador mora no os-service, sem criar um serviço só para isso.

A contrapartida é que o os-service conhece o fluxo inteiro, e uma mudança no processo passa por ele. Com 3 participantes, isso é mais simples do que espalhar o fluxo em eventos (coreografia).

**Limitação conhecida:** gravar no banco e publicar na fila não é atômico. Onde possível, a mensagem é publicada antes de mudar o status (se o RabbitMQ estiver fora, a API responde `503` e nada muda). A solução completa seria o padrão *Transactional Outbox*.

**Idempotência:** cada passo confere o status atual da OS antes de agir. Uma mensagem repetida é ignorada.

## Banco de dados

**MySQL**, schema `os_db`, acessado apenas pelo usuário `os_user`.

| Tabela | Conteúdo |
|---|---|
| `clientes` | Dados do cliente |
| `veiculos` | Veículos do cliente |
| `ordens_de_servico` | OS e seu status |
| `os_pecas` / `os_servicos` | Itens da OS (ID do catálogo + nome e preço) |
| `historico_os` | Cada mudança de status, inclusive as feitas pela Saga |

## Endpoints

Prefixo: `/api/v1` · Swagger: `http://localhost:8000/docs`

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/cliente/novo_cliente` | Cadastrar novo cliente |
| `GET` | `/cliente/clientes` | Listar todos os clientes |
| `GET` | `/cliente/{cpf}` | Consultar um cliente |
| `GET` | `/cliente/{cpf}/veiculos` | Listar os veículos do cliente |
| `PATCH` | `/cliente/{cpf}/atualizar_informacoes` | Atualizar dados do cliente |
| `PATCH` | `/cliente/{novo_cpf}/transferir_veiculo/{placa}` | Transferir veículo para outro CPF |
| `DELETE` | `/cliente/{cpf}/remover_cliente` | Remover um cliente |
| `POST` | `/veiculo/cadastrar_veiculo` | Cadastrar novo veículo |
| `GET` | `/veiculo/consultar_placa/{placa}` | Consultar um veículo |
| `GET` | `/veiculo/veiculos` | Listar todos os veículos |
| `PATCH` | `/veiculo/atualizar_veiculo/{placa}` | Atualizar veículo |
| `DELETE` | `/veiculo/remover_veiculo/{veiculo_placa}` | Excluir um veículo |
| `POST` | `/ordem_servico/nova_os` | Cadastrar uma nova OS |
| `POST` | `/ordem_servico/nova_os_completa` | Cadastrar cliente, veículo e OS em uma chamada |
| `GET` | `/ordem_servico/consultar/{os_id}` | Consultar uma OS |
| `GET` | `/ordem_servico/ordens` | Listar todas as OS |
| `GET` | `/ordem_servico/historico/{os_id}` | Consultar o histórico da OS (inclui a Saga) |
| `POST` | `/ordem_servico/{os_id}/adicionar_peca/{peca_id}` | Adicionar peça (baixa estoque no catálogo) |
| `POST` | `/ordem_servico/{os_id}/adicionar_servico/{servico_id}` | Adicionar serviço |
| `DELETE` | `/ordem_servico/{os_id}/remover_peca/{peca_id}` | Remover peça (devolve estoque no catálogo) |
| `DELETE` | `/ordem_servico/{os_id}/remover_servico/{servico_id}` | Remover serviço |
| `PATCH` | `/ordem_servico/avancar/{os_id}` | Avançar status (ao chegar em *Aguardando Aprovação*, inicia a Saga) |
| `PATCH` | `/ordem_servico/atualizar/{os_id}` | Atualizar CPF ou veículo da OS |
| `DELETE` | `/ordem_servico/excluir/{os_id}` | Excluir uma OS |
| `GET` | `/health/live` | Liveness probe |
| `GET` | `/health/ready` | Readiness probe (testa o MySQL) |

## Variáveis de ambiente

| Variável | Exemplo | Descrição |
|---|---|---|
| `DATABASE_URL` | `mysql+pymysql://os_user:os_pass@mysql:3306/os_db` | Conexão com o MySQL |
| `CATALOG_SERVICE_URL` | `http://catalog-service:8000` | Endereço do catalog-service |
| `RABBITMQ_URL` | `amqp://guest:guest@rabbitmq:5672/%2F` | Sem ela, o consumidor da Saga não é iniciado |

## Como rodar

Com o restante do ambiente, a partir da raiz do projeto: `docker compose up --build -d`.

Só este serviço:

```bash
docker build -t os-service .
docker run -p 8000:8000 -e DATABASE_URL=... -e CATALOG_SERVICE_URL=... -e RABBITMQ_URL=... os-service
```

## Testes

```bash
pip install -r requirements.txt
DATABASE_URL="sqlite:///./test.db" pytest --cov=app --cov-report=term
```

* **Unitários:** services, repositories, schemas, catalog client, RabbitMQ e Saga (mockados).
* **Integração:** fluxo completo pela API com SQLite, simulando o catalog-service e o RabbitMQ.
* **BDD:** [tests/features/saga_ordem_servico.feature](tests/features/saga_ordem_servico.feature). Para ver passo a passo:
  ```bash
  DATABASE_URL="sqlite:///./test.db" pytest tests/test_saga_bdd.py --gherkin-terminal-reporter -v
  ```

### Cobertura

```
TOTAL    921 stmts    56 miss    94%
175 passed
```

| Módulo | Cobertura |
|---|---|
| `services/saga_service.py` | 100% |
| `repositories/OSRepository.py` | 100% |
| `clients/catalog_client.py` | 100% |
| `messaging/rabbitmq.py` | 98% |
| `services/OSService.py` | 93% |
