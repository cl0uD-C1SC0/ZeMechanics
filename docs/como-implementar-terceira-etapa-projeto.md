# Como implementar - Terceira etapa do projeto (Depreciado)

> Instruções da Fase 3 (monólito na AWS com API Gateway + Lambda + EKS), mantidas para histórico.

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
