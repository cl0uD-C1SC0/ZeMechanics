#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Ze Mechanics - Fase 4 | Teste ponta a ponta da Saga (docker compose)
#
# Uso (na raiz do repositório, com o compose no ar):
#   ./scripts/testar-saga.sh              -> roda os cenários principais (A, B, C)
#   ./scripts/testar-saga.sh todos        -> roda todos (inclui os que derrubam containers)
#   ./scripts/testar-saga.sh feliz        -> um cenário específico
#
# Cenários:
#   feliz     A - caminho feliz: orçamento → aprovação → execução → entrega
#   falha     B - execução falha → estorno + peças devolvidas + OS cancelada
#   reprova   C - cliente reprova → peças devolvidas + OS reprovada
#   recusado  D - pagamento recusado (mock) → peças devolvidas + OS cancelada   [reinicia o billing]
#   async     E - billing fora do ar: a mensagem espera na fila e é processada depois [para o billing]
#   rabbit    F - RabbitMQ fora do ar: o os-service responde 503 e nada muda       [para o rabbitmq]
# ─────────────────────────────────────────────────────────────────────────────
set -u
cd "$(dirname "$0")/.."

OS=localhost:8000/api/v1
CAT=localhost:8001/api/v1
BIL=localhost:8002/api/v1
EXE=localhost:8003/api/v1
H='Content-Type: application/json'
CPF=52998224725

OK=0; FALHAS=0
verde()    { printf '\033[32m%s\033[0m\n' "$*"; }
vermelho() { printf '\033[31m%s\033[0m\n' "$*"; }
titulo()   { printf '\n\033[1;34m== %s ==\033[0m\n' "$*"; }
info()     { printf '   %s\n' "$*" >&2; }

# ── helpers de JSON (sem depender de jq) ────────────────────────────────────
campo()  { grep -o "\"$1\":\"[^\"]*\"" | head -1 | cut -d'"' -f4; }   # campo texto
numero() { grep -o "\"$1\":[0-9]*" | head -1 | cut -d: -f2; }          # campo número

# ── verificações ────────────────────────────────────────────────────────────
check() {  # descrição esperado obtido
  if [ "$2" = "$3" ]; then verde "   ✔ $1: $3"; OK=$((OK + 1))
  else vermelho "   ✘ $1: esperado '$2', veio '$3'"; FALHAS=$((FALHAS + 1)); fi
}

esperar() {  # descrição url campo esperado  (a Saga é assíncrona: tenta por até 20s)
  local valor=""
  for _ in $(seq 1 20); do
    valor=$(curl -s "$2" | campo "$3")
    [ "$valor" = "$4" ] && break
    sleep 1
  done
  check "$1" "$4" "$valor"
}

esperar_url() {  # url  (espera um serviço responder 200)
  for _ in $(seq 1 60); do curl -sf "$1" >/dev/null && return 0; sleep 1; done
  vermelho "   ✘ $1 não respondeu em 60s"; FALHAS=$((FALHAS + 1)); return 1
}

estoque() { curl -s $CAT/peca/consultar_peca/1 | numero quantidade; }
status_os() { curl -s $OS/ordem_servico/consultar/$1 | campo status; }
placa() { echo "T$(date +%s%N | cut -c9-15)"; }

# ── preparação (só cria o que ainda não existe) ─────────────────────────────
preparar() {
  titulo "Preparação"
  esperar_url $OS/health/ready && esperar_url $CAT/health/ready && esperar_url $BIL/health/ready && esperar_url $EXE/health/ready || exit 1

  if [ "$(curl -s -o /dev/null -w '%{http_code}' $CAT/peca/consultar_peca/1)" = "404" ]; then
    curl -s -X POST $CAT/peca/adicionar_peca -H "$H" -d '{"nome":"Filtro de Oleo","preco":45.9,"quantidade":50}' >/dev/null
    info "peça 1 criada no catalog-service"
  fi
  if [ "$(curl -s -o /dev/null -w '%{http_code}' $CAT/servico/consultar_servico/1)" = "404" ]; then
    curl -s -X POST $CAT/servico/adicionar_servico -H "$H" -d '{"nome":"Troca de Oleo","preco":120,"descricao":"Troca completa"}' >/dev/null
    info "serviço 1 criado no catalog-service"
  fi
  if [ "$(curl -s -o /dev/null -w '%{http_code}' $OS/cliente/$CPF)" = "404" ]; then
    curl -s -X POST $OS/cliente/novo_cliente -H "$H" \
      -d "{\"nome\":\"Joao\",\"cpf\":\"$CPF\",\"endereco\":\"Rua X\",\"telefone\":\"11999999999\",\"email\":\"joao@teste.com\"}" >/dev/null
    info "cliente $CPF criado no os-service"
  fi
  CLIENTE_ID=$(curl -s $OS/cliente/$CPF | numero id)

  local qtd; qtd=$(estoque)
  if [ "${qtd:-0}" -lt 20 ]; then
    curl -s -X PATCH "$CAT/peca/adicionar_quantidade/1?quantidade=50" >/dev/null
    info "estoque reabastecido"
  fi
  verde "   ✔ ambiente pronto (estoque do filtro: $(estoque))"
}

# Cria veículo + OS com 2 filtros e 1 serviço. Com "--ate-diagnostico" para em
# "Em Diagnóstico"; sem ele, avança até "Aguardando Aprovação" (dispara a Saga).
nova_os() {
  local p id; p=$(placa)
  curl -s -X POST $OS/veiculo/cadastrar_veiculo -H "$H" \
    -d "{\"modelo\":\"Fit\",\"marca\":\"Honda\",\"placa\":\"$p\",\"ano\":\"2014\",\"cliente_id\":$CLIENTE_ID}" >/dev/null
  id=$(curl -s -X POST $OS/ordem_servico/nova_os -H "$H" -d "{\"cliente_cpf\":$CPF,\"veiculo_placa\":\"$p\"}" \
    | grep -o 'ID: [0-9]*' | grep -o '[0-9]*')
  curl -s -X POST "$OS/ordem_servico/$id/adicionar_peca/1?quantidade=2" >/dev/null
  curl -s -X POST "$OS/ordem_servico/$id/adicionar_servico/1" >/dev/null
  curl -s -X PATCH $OS/ordem_servico/avancar/$id >/dev/null
  [ "${1:-}" != "--ate-diagnostico" ] && curl -s -X PATCH $OS/ordem_servico/avancar/$id >/dev/null
  info "OS $id criada (placa $p)"
  echo "$id"
}

# ── cenários ────────────────────────────────────────────────────────────────
cenario_feliz() {
  titulo "A · Caminho feliz"
  local e0 id; e0=$(estoque); id=$(nova_os)
  check "estoque baixou 2" "$((e0 - 2))" "$(estoque)"
  esperar "billing gerou o orçamento" "$BIL/orcamento/$id" status "Aguardando Aprovação"

  curl -s -X POST "$BIL/orcamento/$id/confirmar_aprovacao?cliente_cpf=$CPF" >/dev/null
  info "cliente aprovou e pagou"
  esperar "OS entrou em execução" "$OS/ordem_servico/consultar/$id" status "Em Execução"
  esperar "execution recebeu a OS" "$EXE/execucao/$id" status "Na Fila"

  for _ in 1 2 3; do curl -s -X PATCH $EXE/execucao/$id/avancar >/dev/null; done
  info "mecânico avançou: diagnóstico → reparo → finalizada"
  esperar "OS finalizada" "$OS/ordem_servico/consultar/$id" status "Finalizada"

  curl -s -X PATCH $OS/ordem_servico/avancar/$id >/dev/null
  check "OS entregue" "Entregue" "$(status_os $id)"
  check "estoque continua baixado (peças usadas)" "$((e0 - 2))" "$(estoque)"
}

cenario_falha() {
  titulo "B · Execução falha → compensação completa"
  local e0 id; e0=$(estoque); id=$(nova_os)
  esperar "billing gerou o orçamento" "$BIL/orcamento/$id" status "Aguardando Aprovação"
  curl -s -X POST "$BIL/orcamento/$id/confirmar_aprovacao?cliente_cpf=$CPF" >/dev/null
  esperar "OS entrou em execução" "$OS/ordem_servico/consultar/$id" status "Em Execução"

  curl -s -X PATCH "$EXE/execucao/$id/falhar?motivo=peca%20incompativel" >/dev/null
  info "mecânico marcou falha na execução"
  esperar "billing estornou o pagamento" "$BIL/orcamento/$id" status "Estornado"
  esperar "OS cancelada" "$OS/ordem_servico/consultar/$id" status "Cancelada"
  check "peças devolvidas ao estoque" "$e0" "$(estoque)"
}

cenario_reprova() {
  titulo "C · Cliente reprova o orçamento"
  local e0 id; e0=$(estoque); id=$(nova_os)
  esperar "billing gerou o orçamento" "$BIL/orcamento/$id" status "Aguardando Aprovação"

  curl -s -X POST "$BIL/orcamento/$id/reprovar?cliente_cpf=$CPF" >/dev/null
  info "cliente reprovou"
  esperar "OS reprovada" "$OS/ordem_servico/consultar/$id" status "Reprovada"
  check "peças devolvidas ao estoque" "$e0" "$(estoque)"
}

cenario_recusado() {
  titulo "D · Pagamento recusado (reinicia o billing com MOCK_PAGAMENTO_STATUS=rejected)"
  MOCK_PAGAMENTO_STATUS=rejected docker compose up -d billing-service >/dev/null 2>&1
  esperar_url $BIL/health/ready || return

  local e0 id; e0=$(estoque); id=$(nova_os)
  esperar "billing gerou o orçamento" "$BIL/orcamento/$id" status "Aguardando Aprovação"
  curl -s -X POST "$BIL/orcamento/$id/confirmar_aprovacao?cliente_cpf=$CPF" >/dev/null
  info "cliente tentou pagar (cartão recusado)"
  esperar "pagamento recusado no billing" "$BIL/orcamento/$id" status "Pagamento Recusado"
  esperar "OS cancelada" "$OS/ordem_servico/consultar/$id" status "Cancelada"
  check "peças devolvidas ao estoque" "$e0" "$(estoque)"

  docker compose up -d billing-service >/dev/null 2>&1
  esperar_url $BIL/health/ready
  info "billing voltou ao modo 'approved'"
}

cenario_async() {
  titulo "E · Billing fora do ar: a mensagem espera na fila"
  docker stop billing_service >/dev/null
  info "billing-service parado"

  local id; id=$(nova_os)
  check "os-service não travou (OS aguardando aprovação)" "Aguardando Aprovação" "$(status_os $id)"
  sleep 2
  local na_fila; na_fila=$(docker exec rabbitmq rabbitmqctl list_queues -q name messages | awk '$1=="billing.commands"{print $2}')
  check "mensagem esperando em billing.commands" "1" "$na_fila"

  docker start billing_service >/dev/null
  info "billing-service religado"
  esperar_url $BIL/health/ready
  esperar "billing processou a mensagem atrasada" "$BIL/orcamento/$id" status "Aguardando Aprovação"
}

cenario_rabbit() {
  titulo "F · RabbitMQ fora do ar: 503 e nada muda pela metade"
  local id; id=$(nova_os --ate-diagnostico)
  docker stop rabbitmq >/dev/null
  info "rabbitmq parado"

  check "avançar responde 503" "503" "$(curl -s -o /dev/null -w '%{http_code}' -X PATCH $OS/ordem_servico/avancar/$id)"
  check "OS continua em diagnóstico" "Em Diagnóstico" "$(status_os $id)"

  docker start rabbitmq >/dev/null
  info "rabbitmq religado (aguardando ficar saudável e os consumidores reconectarem)"
  for _ in $(seq 1 60); do
    [ "$(docker inspect -f '{{.State.Health.Status}}' rabbitmq)" = "healthy" ] && break; sleep 1
  done
  sleep 6

  curl -s -X PATCH $OS/ordem_servico/avancar/$id >/dev/null
  esperar "depois de voltar, a Saga segue normal" "$BIL/orcamento/$id" status "Aguardando Aprovação"
}

# ── execução ────────────────────────────────────────────────────────────────
preparar
case "${1:-principais}" in
  feliz)      cenario_feliz ;;
  falha)      cenario_falha ;;
  reprova)    cenario_reprova ;;
  recusado)   cenario_recusado ;;
  async)      cenario_async ;;
  rabbit)     cenario_rabbit ;;
  principais) cenario_feliz; cenario_falha; cenario_reprova ;;
  todos)      cenario_feliz; cenario_falha; cenario_reprova; cenario_recusado; cenario_async; cenario_rabbit ;;
  *)          echo "cenário desconhecido: $1 (use: feliz | falha | reprova | recusado | async | rabbit | todos)"; exit 2 ;;
esac

titulo "Resultado"
if [ "$FALHAS" -eq 0 ]; then verde "   $OK verificações OK"
else vermelho "   $FALHAS falha(s), $OK OK — veja: docker compose logs os-service billing-service execution-service"; fi
exit "$FALHAS"
