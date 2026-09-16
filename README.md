<div align="center">
    <img src="app/static/images/Logo-ZeMechanicsLTDA.png" width=300px>
</div>

<br>
<br>
<br>

# ZeMechanics

Seja muito bem-vindo à ZeMechanics!

A melhor mecânica da região de Osasco, a única com especialidade em desmanche de carro, seja blindado ou não!

>Também reparamos os carros feitos *só para rodar*!! 

## Resumo

Todo o código foi desenvolvido utilizado **Python**, mais especificamente **FastAPI** por questões de conhecimento na linguagem e facilidade no aprendizado de desenvolvimento de APIs utilizando o *FastAPI*.

O Banco da aplicação é **MySQL**, o motivo: É eficiente, e para um sistema onde é necessário trabalhar com um conjunto de dados relacionais como **cliente = veículo**, um banco de dados relacional se encaixa perfeitamente, além disso, o conhecimento prévio em MySQL foi também levado em conta ao escolher o mesmo. 

A escolha da biblioteca **FastAPI** foi devido a sua curva de aprendizado ser menor, não significando que ela é ruim, e sim possuí uma série de facilidades na hora do desenvolvimento, uma deles é criar automaticamente um **Swagger UI** para a aplicação.

Para **análise de código** foi utilizado o SonarQube, uma das maiores ferramentas de análise de código.



## Índice

* ➡️ [Estrutura de diretórios](docs/estrutura_diretorios.md)
* ➡️ [Configurações do app/core](docs/core-configuracoes.md)
* ➡️ [Como criar um ambiente virtual - Windows](docs/como-criar-venv.md)
* ➡️ [Quais são as rotas existens](docs/apis-rotas.md)

## Stack

<p align="center">
          <img src="https://skillicons.dev/icons?i=,,github,docker,python,mysql,sonarqube,">
</p>

# Como implementar - Terceira etapa do projeto

## 01 - Configure AWS Credentials
```bash
aws configure
```

## 02 - Ajuste as variáveis do Terraform
```bash
cd terraform/
nano main.tf
``` 

## 03 - Deploy Terraform:
```bash
terraform init
terraform apply --auto-approve
```

## TEST COMMANDS:

### 01 - Gerar Token:
```bash
curl -X POST https://<API_GATEWAY_ID>.execute-api.us-east-1.amazonaws.com/prod/auth/login -H "Content-Type: application/json" -d "{\"cpf\": \"<CPF>\"}"

# OBS: Substitua os campos:
# ➡️ <API_GATEWAY_ID>: Pelo ID do AWS API Gateway criado
# ➡️ <CPF>: Pelo CPF cadastrado nas etapas anteriores
```

### 02 - APP Test Work around
Sempre coloque o **/prod** no inicio do PATH das rotas.

> 01 - Cadastrar cliente (LINUX)
```bash
curl -X 'POST' \
  'https://<API_GATEWAY_ID>.execute-api.us-east-1.amazonaws.com/prod/api/v1/cliente/novo_cliente' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "nome": "string",
  "cpf": "string",
  "endereco": "string",
  "telefone": "string",
  "email": "string"
}'

# OBS: Substitua os campos 'string' pelo seus respectivos valores
```

> 02 - Gerar JWT
```
curl -X POST https://<API_GATEWAY_ID>.execute-api.us-east-1.amazonaws.com/prod/auth/login -H "Content-Type: application/json" -d "{\"cpf\": \"<CPF\"}"
```

> 03 - Cria uma OS completa (sem peça/serviço)
```bash
curl -X 'POST' \
  'https://<API_GATEWAY_ID>.execute-api.us-east-1.amazonaws.com/prod/api/v1/ordem_servico/nova_os_completa' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <TOKEN>' \
  -d '{
  "cliente": {
    "nome": "string",
    "cpf": "string",
    "endereco": "string",
    "telefone": "string",
    "email": "string"
  },
  "veiculo": {
    "modelo": "string",
    "marca": "string",
    "placa": "string",
    "ano": "string"
  },
  "pecas": [],
  "servicos": []
}'
```

> 04 - Avance a OS ate o status de Aguardando Aprovacao
```bash
curl -X 'PATCH' \
  'https://<API_GATEWAY_ID>.execute-api.us-east-1.amazonaws.com/prod/api/v1/ordem_servico/avancar/{OS_ID}' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <TOKEN>'
```

> 05 - Aprove a:
```bash
curl -X POST "https://<API_GATEWAY_ID>.execute-api.us-east-1.amazonaws.com/prod/api/v1/ordem_servico/confir
mar_aprovacao/<OS_ID>?cliente_cpf=<CPF>"
```

> 06 - Execute a etapa 04 novamente para finalizar.

>> OBS: Consulte o Swagger, acesse:
```html
https://<API_GATEWAY_ID>.execute-api.us-east-1.amazonaws.com/prod/docs
```

# Como implementar - Segunda etapa do projeto (Depreciado)

* [Clique aqui para ver o tutorial antigo](docs/como-implementar-segunda-etapa-projeto.md)

## 📫 Vamos nos conectar?

<p align="center">
  <a href="https://www.linkedin.com/in/jgsiqueiraa/">
    <img src="https://img.shields.io/badge/-LinkedIn-0A66C2?logo=linkedin&logoColor=white&style=for-the-badge" />
  </a>
  <a href="https://github.com/cl0uD-C1SC0">
    <img src="https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white&style=for-the-badge" />
  </a>
</p>

<br><br>


<h4 align="center">
   © 2026 Ze Mechanics LTDA. O lugar perfeito para carro de leilão, feito apenas para rodar. 🚀
</h4>