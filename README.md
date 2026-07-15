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

## Como implementar - Segunda etapa do projeto

Nessa etapa, a aplicação sai do `docker-compose` local e passa a rodar dentro de um cluster **Kubernetes** (via **Kind**), com toda a infraestrutura provisionada via **Terraform**.

### Índice
* ➡️ [Requisitos mínimos](#requisitos-mínimos)
* ➡️ [Passo a passo](#passo-a-passo)

### Requisitos mínimos
* Docker (rodando e acessível a partir do WSL)
* [Terraform CLI](https://developer.hashicorp.com/terraform/install)
* [Kind CLI](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
* [kubectl CLI](https://kubernetes.io/docs/tasks/tools/)
* Uma imagem da API publicada no Docker Hub (ex: `seuusuario/mecanica:latest`)

### Passo a passo

#### 01 - Ambiente virtual (venv)
> Não é obrigatório pra essa etapa (a aplicação já roda dentro do container), mas é útil caso queira rodar os testes localmente. Veja: [Como criar um Venv (Windows)](docs/como-criar-venv.md)

#### 02 - Acesse o diretório do Terraform
```bash
cd infra
```

#### 03 - Crie só o cluster Kind primeiro
```bash
terraform init
terraform apply -target=kind_cluster.this
```
> Esse primeiro apply em separado é necessário: o provider `kubectl` depende de atributos que só existem depois que o cluster já foi criado, então aplicar tudo de uma vez só na primeira execução falha.

#### 04 - Crie o secret de acesso ao Docker Hub (necessário se a imagem for privada)
```bash
export KUBECONFIG=$(terraform output -raw kubeconfig_path)

kubectl create secret docker-registry dockerhub-credentials \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=SEU_USUARIO \
  --docker-password='SEU_ACCESS_TOKEN' \
  --docker-email=seu-email@exemplo.com \
  --namespace=zemechanics
```
> Gere um Access Token (nunca use a senha da sua conta) em: Docker Hub → Account Settings → Security. Esse secret é criado direto no cluster e não fica versionado no repositório.

#### 05 - Aplique o restante (namespace, mysql, maildev e api)
```bash
terraform apply
```

#### 06 - Verifique se tudo subiu
```bash
kubectl get pods -n zemechanics -w
```
> Espere todos os pods ficarem `Running`/`Ready`. O pod da API só fica pronto depois que o MySQL aceitar conexões — existe um `initContainer` esperando exatamente por isso.

#### 07 - Acesse localmente
* Swagger da API: http://localhost:30080/docs
* MailDev (aprovação de OS por e-mail): http://localhost:30081

> Login na API com as mesmas credenciais didáticas da primeira etapa: usuário `admin`, senha `admin1234`.

> Pra derrubar tudo depois: `terraform destroy` (dentro de `infra/`).

## Como implementar - Primeira etapa do projeto (Depreciado)

* [Clique aqui para ver o tutorial antigo](docs/como-implementar-primeira-etapa-projeto.md)

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