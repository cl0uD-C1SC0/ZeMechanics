# Estrutura de Diretórios - explicação

A Documentação a seguir tem como viés reforçar o meu conhecimento na criação de APIs, models e etc, tudo a respeito do mundo de Desenvolvimento de Software, portanto, usarei essa documentação como base para criar outros futuros projetos.

# INDEX

* [📁app/](#diretório-principal-app)
* [📁api/](#diretório-api)
* [📁core/](#diretório-core)
* [📁domain/](#diretório-domain)
* [📁repositories/](#diretório-repositories)
* [📁schemas/](#diretório-schemas)

## 📁 Diretório principal: app/

O diretório **app/** vai conter todas as configurações do nosso APP, sua estrutura e nomenclatura é muito importante para deixar um código mais organizado e limpo.

Os próximos itens a seguir conta quais **arquivos** devem ser criados neste diretório, mais a frente, quais subdiretórios devem ser criados e seus respectivos arquivos/objetivos

### Arquivo: database.py

O arquivo de **database.py** é o arquivo responsável por se *conectar* ao Banco de Dados da aplicação, veja mais detalhes de sua possível configuração:
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
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

### Arquivo: main.py

O arquivo **main.py** ele é simples, é o arquivo que o framework FastAPI vai olhar para mapear todas as rotas, mas temos um ponto importante:

* Base.metadata.ceate_all(bind=engine): Esse é o responsável por acessar /domain/models e criar nossas tabelas dentro do banco de dados quando o app for subir

> Para rodar o main.py execute (fora do app/):
```shell
uvicorn app.main:app --reload
```

## 📁 Diretório: api

Neste diretório fica **todas as nossas rotas** por padrão é interessante criarmos uma estrutura como api/v1, api/v2 pois define qual versão aquela rota é

No **📄main.py** faremos uma referência a esse diretório da seguinte maneira:
```python
app.include_router(router, prefix="/api/v1")
```

## 📁 Diretório: core

Neste diretório fica **todas as configurações principais** como string de conexão ao banco de dados, config do JWT e etc...

Um exemplo de string de conexão ao banco de dados:

```python
from  pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

BASE_DIR = os.getcwd()
dotenv = os.path.join(BASE_DIR, "../../env")
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = str(os.getenv('DATABASE_URL'))
    SECRET_KEY: str = str(os.getenv('SECRET_KEY'))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

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