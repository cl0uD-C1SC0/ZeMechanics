# catalog-service

Microsserviço de **Catálogo** da Ze Mechanics: peças (com estoque) e serviços (mão de obra).

## Responsabilidades

* Cadastro, consulta, atualização e remoção de peças e serviços.
* Controle de estoque das peças: baixa e devolução.
* Garantir que o estoque nunca fique negativo: uma baixa maior que o disponível é recusada com `400`.

## Arquitetura

```
app/
├── api/v1/          rotas (FastAPI): peça, serviço, health
├── services/        regras de negócio (peca_service, servico_service)
├── repositories/    acesso ao MySQL (SQLAlchemy)
└── domain/models/   Peca, Servicos
```

### Comunicação

| Quem chama | Como | O quê |
|---|---|---|
| os-service | **REST** (síncrono) | Consultar peça e serviço, `remover_quantidade` (baixa de estoque) e `adicionar_quantidade` (devolução, inclusive como **compensação da Saga**) |

O catalog-service não participa das filas do RabbitMQ: ele só responde a chamadas REST. Ele não conhece as OS. Quem guarda quais peças estão em cada OS é o os-service.

## Banco de dados

**MySQL**, schema `catalog_db`, acessado apenas pelo usuário `catalog_user`.

| Tabela | Conteúdo |
|---|---|
| `pecas` | Nome, preço e quantidade em estoque |
| `servicos` | Nome, descrição e preço da mão de obra |

## Endpoints

Prefixo: `/api/v1` · Swagger: `http://localhost:8001/docs`

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/peca/adicionar_peca` | Cadastrar uma nova peça |
| `GET` | `/peca/pecas` | Listar todas as peças |
| `GET` | `/peca/consultar_peca/{peca_id}` | Consultar uma peça |
| `PATCH` | `/peca/atualizar_peca/{peca_id}` | Atualizar nome e preço |
| `PATCH` | `/peca/adicionar_quantidade/{peca_id}` | Adicionar quantidade ao estoque |
| `PATCH` | `/peca/remover_quantidade/{peca_id}` | Remover quantidade do estoque (`400` se insuficiente) |
| `DELETE` | `/peca/remover_peca/{peca_id}` | Remover peça |
| `POST` | `/servico/adicionar_servico` | Cadastrar um novo serviço |
| `GET` | `/servico/servicos` | Listar todos os serviços |
| `GET` | `/servico/consultar_servico/{servico_id}` | Consultar um serviço |
| `PATCH` | `/servico/atualizar_servico/{servico_id}` | Atualizar nome, preço e descrição |
| `DELETE` | `/servico/remover_servico/{servico_id}` | Remover um serviço |
| `GET` | `/health/live` | Liveness probe |
| `GET` | `/health/ready` | Readiness probe (testa o MySQL) |

## Variáveis de ambiente

| Variável | Exemplo | Descrição |
|---|---|---|
| `DATABASE_URL` | `mysql+pymysql://catalog_user:catalog_pass@mysql:3306/catalog_db` | Conexão com o MySQL |

## Como rodar

Com o restante do ambiente, a partir da raiz do projeto: `docker compose up --build -d`.

Só este serviço:

```bash
docker build -t catalog-service .
docker run -p 8001:8000 -e DATABASE_URL=... catalog-service
```

## Testes

```bash
pip install -r requirements.txt
DATABASE_URL="sqlite:///./test.db" pytest --cov=app --cov-report=term
```

### Cobertura

```
TOTAL    328 stmts    39 miss    88%
57 passed
```

| Módulo | Cobertura |
|---|---|
| `repositories/PecaRepository.py` | 100% |
| `repositories/ServicosRepository.py` | 100% |
| `services/servico_service.py` | 100% |
| `services/peca_service.py` | 92% |
