# Configurações do diretório: CORE

Nesta documentação você as características de cada arquivo localizado dentro do diretório **app/core**, veja mais abaixo:

## 📝config.py

O arquivo de **config.py** centraliza as configurações que o FastAPI vai utilizar, como por exemplo:

* URL do Banco de Dados
* Secret KEY do Banco de Dados
* Secret KEY da JWT
* Algoritmo utilizado
* Tempo para o token de acesso expirar

As configurações deste arquivo são utilizadas em: **app/database.py**

## 📝dependencies.py

Um dos arquivos utilizados pela configuração da JWT, ele instancia todas as dependencias necessárias para que o FastAPI utilize quando usar o JWT, neste caso, a configuração é de **get_current_user** que valida se o usuário atual contém o Token válido para acessar as rotas ou não.

## 📝init_db.py

É um arquivo que é **"chamado"** toda vez que a aplicação inicia, neste caso, ele cria automáticamente um usuário chamado **admin** e configura uma senha para ele.

Esse usuário ele é utilizado para gerar o token de acesso (Bearer Token) para que seja permitido o acesso as rotas da aplicação

## 📝security.py

É o arquivo principal da JWT, nele é feito: **criação de token**, **validação do token**, **validação do usuário**, **gerar hash da senha do usuário**

Ele é chamado quando um usuário admin é criado e/ou quando é necessário criar um token novo (Bearer) ou validar um token existente.