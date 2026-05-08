# Estrutura de Diretórios - explicação

A Documentação a seguir tem como viés reforçar o meu conhecimento na criação de APIs, models e etc, tudo a respeito do mundo de Desenvolvimento de Software, portanto, usarei essa documentação como base para criar outros futuros projetos.

# INDEX

[📁root](#-diretório-root-raiz)
 * [📁reports](#-reports)
 * [📁tests](#-tests)

[📁app/](#-diretório-principal-app)
 * [📁api/](#-diretório-api)
 * [📁core/](#-diretório-core)
 * [📁domain/](#-diretório-domain)
 * [📁repositories/](#-diretório-repositories)
 * [📁schemas/](#-diretório-schemas)
 * [📁services](#-diretório-services)
 * [📁static](#-diretório-static)

# 📁 Diretório root (raiz)

O diretório root (raiz), contém todos os arquivos necessários para que a aplicação funcione, veja mais detalhes abaixo:

### 📝 .gitignore
> O arquivo de .gitinore foi gerado pelo site: https://gitignore.io para incluir arquivos a serem ignorados que são gerados automáticamente pelo SonarQube, Venv, Pydantic, FastAPI, Python e outros (que foram adicionados manualmente)

### ⚙️ conftest.py
> O arquivo de conftest.py serve exclusivamente para passar uma referência de diretório para que seja possível rodar o comando **python -m pytest** no diretório raiz

### 📝 docker-compose.yml
> O arquivo de docker-compose.yml contém todos os **services** necessários para que toda a arquitetura funcione corretamente, services estes:
* **db**: Mysql
* **maildev**: Serviço de Email local
* **api**: FastAPI
* **db_sonarqube**: Banco de dados para o SonarQube
* **soanrqube**: Serviço do Sonarqube Community

> Além disso é criado alguns volumes de forma automática e que são utilizados pelos services:
* **mysql_data**: Disco da aplicação
* **sonarqube_data**: Disco do SonarQube
* **sonarqube_extensions**: Disco do SonarQube dedicado a extensões
* **sonarqube_logs**: Disco do SonarQube dedicado a logs
* **postgresql_data**: Disco do Banco de dados do SonarQube

### 📝 Dockerfile
> Dockerfile necessário para aplicação, construído com base nas boas práticas do Docker, inclusive de segurança.
### 📝 requirements.txt
> Todas as bibliotecas necessárias para que o app funcione
### ⚙️ sonar-project.properties
> Configurações do Sonarqube Project, que possuí informações de: **project ID & Key, coveragePath** etc..

## 📁 reports

Neste diretório contém todos os reports gerados pelo comando abaixo:

```powershell
python -m pytest --cov=app --cov-report=xml:reports/coverage.xml --junitxml=reports/test-results.xml
```

Esses arquivos são utilizados quando rodamos a análise do SonarQube pelo comando:
```powershell
pysonar --sonar-host-url=http://localhost:9000 --sonar-token=<SONARQUBE_TOKEN>--sonar-project-key=<SONARQUBE_PROJECT_KEY>
```

## 📁 tests

Estrutura de diretórios **tests**, com certeza é uma das mais importantes de todo o projeto, ela garante a qualidade do sistema via **testes unitários** e **testes de integração**, os itens que foram **cobertos** nos testes:
* Repository
* Service
* Schema
* database.py

Além disso, como mencionado anteriormente, foi criado um **teste de integração** que cobre:
* Fluxo principal:
    * Simula um banco de dados
    * Cadastra um cliente
    * Cadastra um veículo ao cliente
    * Cadastra uma peça
    * Cadastra um serviço
    * Cria uma nova OS
    * Adiciona uma peça na OS
    * Adiciona um serviço na OS
    * Avança o status da OS para em Diagnóstico
    * Avança o status da OS para Aguardando Aprovação (simulação)
        * O cliente recebe um e-mail e clica no link
        * Visualiza os detalhes do veículo, peças e serviços
        * Visualiza o total da OS
        * Aprova a OS
    * Avança o status da OS para Finalizada
    * Avança o status da OS para Entregue
    * Consulta uma OS entregue

# 📁 Diretório principal: app/

O diretório **app/** vai conter todas as configurações do nosso APP, sua estrutura e nomenclatura é muito importante para deixar um código mais organizado e limpo.

Os próximos itens a seguir conta quais **arquivos** devem ser criados neste diretório, mais a frente, quais subdiretórios devem ser criados e seus respectivos arquivos/objetivos

### 📝 database.py

O arquivo de **database.py** é o arquivo responsável por se *conectar* ao Banco de Dados da aplicação, veja mais detalhes de sua possível configuração:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

* SQL Alchemy: É uma biblioteca que traduz Python para SQL, basicamente um ORM.
* SessionMaker: É o responsável por criar a seção (conexão)
* declarative_base(): É o responsável por criar nossas bases de dados (tabelas)
* from app.core.config import settings: Esse import faz referencia as credenciais do banco de dados, veremos mais a frente. 
* bind: É o responsável por coletar as credenciais como o DATABASE_URL e fazer uma "conexão/bind"

### 📝 main.py

O arquivo **main.py** ele é simples, é o arquivo que o framework FastAPI vai olhar para mapear todas as rotas, mas temos um ponto importante:

* Base.metadata.ceate_all(bind=engine): Esse é o responsável por acessar /domain/models e criar nossas tabelas dentro do banco de dados quando o app for subir

> Para rodar o main.py execute (fora do app/):
```shell
uvicorn app.main:app --reload
```

## 📁 Diretório: api

O Diretório API, tecnicamente falando, é o "centro" da aplicação, todos os dados são recebidos pelas rotas configuradas em cada arquivo (API) e direcionadas aos **services** que veremos mais adiante.

As rotas/APIs ficam localizadas dentro do diretório **v1**, que corresponde a versão 1 das rotas. Veja mais detalhes em [Rotas & APis - Doc](apis-rotas.md)

## 📁 Diretório: core

O Diretório CORE centraliza tudo que é mais importante para aplicação ser **inicializada** como: Configurações de banco, JWT, init DBs e etc.. Veja mais detalhes em: [Entendendo o diretório CORE](core-configuracoes.md)

## 📁 Diretório: domain

Dentro do diretório de **domain**, seguindo o DDD, criamos nossos domínios. Além disso, criamos dentro dele os nossos *models* que são uma representação de uma tabela dentro do banco de dados porém em Python, veja um exemplo abaixo

> 📄 domain/models/Cliente.py
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id       = Column(Integer, primary_key=True, index=True)
    nome     = Column(String(100), nullable=False)
    cpf      = Column(String(14), unique=True, nullable=False)
    contato  = Column(String(20), nullable=False)
    endereco = Column(String(200), nullable=False)

    veiculos = relationship("Veiculo", back_populates="cliente") 
```


Ponto importante:

* relationship: É a forma que relaciona uma tabela com outra via SQL Achemy

## 📁 Diretório: repositories

Neste diretório é centralizado todos os "comandos SQL" (por assim dizer), cada API tem o seu próprio service & repository, quando uma API recebe uma requisição ela encaminha ao service que por sua vez chama o seu repository que executa uma query no banco de dados via Python utilizando **SQL Alchemy**

## 📁 Diretório: schemas

O Diretório schemas é um dos mais importantes, é nele que definimos nosass principais "classes" ou melhor "esquemas".

Porém um ponto interessante é que, quando vamos utilizar o FastAPI por exemplo, utilizamos em conjunto o Pydantic para validar a requisição, veja um exemplo

> 📄 schemas/ClienteSchema.py
```python
from pydantic import BaseModel

class ClienteSchema(BaseModel):
    nome: str
    cpf: str
    endereco: str
    contato: str
```

**Sem** o uso do Pydantic ficaria assim:
```python
class Cliente:
    def __init__(self, nome, contato, endereco, cpf):
        self._nome     = nome
        self._contato  = contato
        self._endereco = endereco
        self._cpf      = cpf


    def __str__(self):
        return f"Cliente: {self._nome}, {self._cpf}, {self._endereco}"
```

## 📁 Diretório: services

Toda API, como dito anteriormente, tem o seu próprio service. O Service é responsável pela regra de negócio, nele é centralizado todas as possíveis validações de cada chamada referente a rota que foi acionada, como por exemplo, cadastrar cliente que pode validar CPF, verificar se o usuário já existe no sistema e por sua vez cadastrar o cliente.

## 📁 Diretório static

O Diretório static, neste contexto, é utilizado apenas para colocar estilos ao Swagger criado pelo FastAPI de forma automática, ele é carregado dentro do arquivo **app/main.py**

