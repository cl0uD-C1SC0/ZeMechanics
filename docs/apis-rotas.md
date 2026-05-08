# Rotas in a Deep View

Nesta documentação, você verá todos os pontos cruciais referente as **rotas** que foram desenvolvidas por mim durante o processo da construção de um sistema para a mecânica ZeMechanics.

Dentro do diretório **api** contém um subdiretório chamado **v1** que armazena todos os arquivos de todas as rotas desenvolvidas.

## 📝 api/router.py 
O **"pai"** das rotas, é ele quem faz o FastAPI enxergar todos os arquivos e todas suas rotas, funcionando como um roteador que encaminha a requisição para o lugar certo.

## 📝 v1/auth_router.py
Esse é um arquivo responsável por realizar o LOGIN, onde resulta na geração do **Bearer Token**, que será utilizado para se autenticar e liberar acesso as rotas, tudo isso seguindo o padrão JWT.

## 📝 v1/cliente_api.py
Arquivo que contém todas as rotas para gerenciar o cliente, seja cadastrar, consultar ou até mesmo remover, veja mais detalhes:
* **api/v1/cliente/novo_cliente**: Cadastra um novo cliente
* **api/v1/cliente/clientes**: Lista todos os clientes cadastrados
* **api/v1/cliente/{cpf}**: Consulta as informações de um cliente específico
* **api/v1/cliente/{cpf}/veiculos**: Lista somente os veículos de um cliente
* **api/v1/cliente/{cpf}/atualizar_informacoes**: Atualiza as informações de um cliente em específico
* **api/v1/cliente/{novo_cpf}/transferir_veiculo/{placa}**: Transfere um veículo para um outro CPF
* **api/v1/cliente/{cpf}/remover_cliente**: Remove um cliente cadastrado

## 📝 v1/ordemservico_api.py
Arquivo que contém todas as rotas para gerenciar as Ordem de Serviço, que é o cerne da aplicação como um todo, veja mais detalhes:
* **api/v1/ordem_servico/nova_os**: Cria uma nova OS
* **api/v1/ordem_servico/consultar/{os_id}**: Consulta todas as informações de uma OS
* **api/v1/ordem_servico/{os_id}/adicionar_peca/{peca_id}**: Adicona uma peça a OS
* **api/v1/ordem_servico/{os_id}/adicionar_servico/{servico_id}**: Adiciona um serviço a OS
* **api/v1/ordem_servico/confirmar_aprovacao/{os_id}**: Confirma a aprovação de uma OS
* **api/v1/ordem_servico/avancar/{os_id}**: Avança o status de uma OS
* **api/v1/ordem_servico/atualizar/{os_id}**: Atualiza as informações de uma OS
* **api/v1/ordem_servico/ordens**: Lista todas as OS criadas
* **api/v1/ordem_servico/aprovar/{os_id}**: Aprova uma OS (É utilizada em conjunto com a *confirmar_aprovacao*)
* **api/v1/ordem_servico/{os_id}/remover_peca/{peca_id}**: Remove uma Peça da OS
* **api/v1/ordem_servico/{os_id}/remover_servico/{servico_id}**: Remove um serviço da OS
* **api/v1/ordem_servico/excluir/{os_id}**: exclui uma OS


## 📝 v1/peca_api.py
Todas as rotas necessárias para gerenciamento de Estoque/Peça, veja mais detalhes:
* **api/v1/peca/adicionar_peca**: Adiciona uma nova peça no estoque
* **api/v1/peca/consultar_peca/{peca_id}**: Consulta as informações de uma peca
* **api/v1/peca/atualizar_peca/{peca_id}**: Atualiza uma dados de uma peça
* **api/v1/peca/adicionar_quantidade/{peca_id}**: Adiciona uma QTD da peça no estoque
* **api/v1/peca/remover_quantidade/{peca_id}**: Remove uma QTD da peça do estoque
* **api/v1/peca/pecas**: Lista todas as peças
* **api/v1/peca/remover_peca/{peca_id}**: Remove uma por completo do sistema


## 📝 v1/servico_api.py
Todas as rotas necessárias para gerenciamento de Serviços, veja mais detalhes:
* **api/v1/servico/adicionar_servico**: Adiciona um novo serviço ao sistema
* **api/v1/servico/servicos**: Lista todos os serviços
* **api/v1/servico/consultar_servico/{servico_id}**: Consulta um serviço no sistema
* **api/v1/servico/atualizar_servico/{servico_id}**: Atualiza um serviço no sistema
* **api/v1/servico/remover_servico/{servico_id}**: remove um serviço

## 📝 v1/veiculo_api.py
* **api/v1/veiculo/cadastrar_veiculo**: Adiciona um novo veículo no cliente
* **api/v1/veiculo/consultar_placa/{placa}**: Consulta um veículo pela placa
* **api/v1/veiculo/veiculos**: Lista todos os veículos
* **api/v1/veiculo/atualizar_veiculo/{placa}**: Atualiza informações de um veículo
* **api/v1/veiculo/remover_veiculo/{veiculo_placa}**: Remove um veículo do sistema