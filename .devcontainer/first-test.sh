#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

if [[ ! -f .env ]]; then
  echo "Arquivo .env ausente. Execute primeiro: bash .devcontainer/bootstrap.sh" >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "O daemon Docker do Codespace ainda nao esta pronto. Aguarde alguns segundos e tente novamente." >&2
  exit 1
fi

echo "[1/6] Iniciando PostgreSQL e Redis..."
docker compose up -d --wait postgres redis

echo "[2/6] Construindo a imagem da aplicacao..."
docker compose build web worker

echo "[3/6] Aplicando migrations com a credencial proprietaria..."
docker compose run --rm web ./scripts/manage-owner.sh migrate

echo "[4/6] Criando dados ficticios idempotentes..."
docker compose run --rm web ./scripts/manage-owner.sh seed_demo

echo "[5/6] Executando testes reais com PostgreSQL, Redis e RLS..."
docker compose run --rm web ./scripts/owner-command.sh pytest -m "not e2e"

echo "[6/6] Iniciando web e worker e aguardando os health checks..."
docker compose up -d --wait web worker
docker compose ps

echo
echo "Pronto. Abra a porta encaminhada 8000 no painel Ports do Codespaces."
echo "Ao terminar, libere os recursos com: docker compose down --volumes"
