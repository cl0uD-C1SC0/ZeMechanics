# language: pt
Funcionalidade: Saga da Ordem de Serviço
  Como oficina mecânica com vários microsserviços
  Quero que a OS passe por orçamento, pagamento e execução de forma coordenada
  Para que, se qualquer etapa falhar, tudo o que já foi feito seja desfeito

  Contexto:
    Dado um cliente com um veículo cadastrado
    E uma OS com 2 filtros de óleo e uma troca de óleo
    E o estoque de filtros no catálogo é 18

  Cenário: Caminho feliz - da abertura à entrega
    Quando o atendente avança a OS até aguardar aprovação
    Então o billing-service recebe o comando "GERAR_ORCAMENTO" com total de 211.80
    Quando o billing-service informa "ORCAMENTO_GERADO"
    E o billing-service informa "PAGAMENTO_APROVADO"
    Então o execution-service recebe o comando "EXECUTAR_OS"
    Quando o execution-service informa "EXECUCAO_INICIADA"
    Então a OS fica "Em Execução"
    Quando o execution-service informa "EXECUCAO_FINALIZADA"
    E o atendente entrega a OS
    Então a OS fica "Entregue"
    E o estoque de filtros no catálogo é 18

  Cenário: A execução falha e a Saga compensa tudo
    Dado que a OS está aguardando aprovação
    Quando o billing-service informa "PAGAMENTO_APROVADO"
    E o execution-service informa "EXECUCAO_INICIADA"
    E o execution-service informa "EXECUCAO_FALHOU"
    Então o billing-service recebe o comando "ESTORNAR_PAGAMENTO"
    Quando o billing-service informa "PAGAMENTO_ESTORNADO"
    Então a OS fica "Cancelada"
    E o estoque de filtros no catálogo é 20

  Cenário: O cliente reprova o orçamento
    Dado que a OS está aguardando aprovação
    Quando o billing-service informa "ORCAMENTO_REPROVADO"
    Então a OS fica "Reprovada"
    E o estoque de filtros no catálogo é 20

  Cenário: Uma mensagem repetida não é compensada duas vezes
    Dado que a OS está aguardando aprovação
    Quando o billing-service informa "PAGAMENTO_RECUSADO"
    E o billing-service informa "PAGAMENTO_RECUSADO"
    Então a OS fica "Cancelada"
    E o estoque de filtros no catálogo é 20
