## Como implementar - Primeira etapa do projeto

### 01 - Requisitos mínimos:
* Docker & Docker Compose
* Python 3.x
* Git CLI

> É extremamente recomendado o uso de ambiente virtual (venv): [Como criar um Venv (windows)](docs/como-criar-venv.md)

### 02 - Clone o repositório
```bash
git clone https://github.com/cl0uD-C1SC0/ZeMechanics.git
```

### 03 - Acesse o repositório & Branch correta
```bash
cd ZeMechanics
git checkout feat/init_project
```

### 04 - Inicie a stack compose:
```bash
docker-compose up -d
```

> A Stack do docker-compose está subindo junto um serviço localmente chamado **SonarQube**, caso não precise, necessário comentar os services: db_sonarqube & sonarqube.

### 05 - Aguarde todos os containers subirem

### 06 - Geração de Token JWT
* Acesse as rotas de: **AUTH**
* Acesse a rota: **login**
* Faça o login com as credenciais já geradas:
    * Usuário: admin
    * Senha: admin123

> As credenciais são simples e estão sendo colocadas aqui por motivo didáticos apenas, em um ambiente real isso seria gerado de forma dinâmica e não seria compartilhada de uma maneira simples assim.

### 07 - Teste o fluxo **completo**:
* Cadastre um usuário
* Cadastre um veículo ao usuário
* Cadastre um serviço
* Cadastre uma peça
* Crie uma OS
* Avance o status da OS até: **Aguardando Aprovação**
* Ao chegar em **Aguardando Aprovação** acesse: http://localhost:1080/#/
* Abra o e-mail e aprove a OS
* Avance novamente a OS até ser finalizada

### Relatório SonarQube

<div align="center">
    <img src="app/static/images/SonarQube-Report.png">
</div>
