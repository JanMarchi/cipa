#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

if [[ ! -f .env ]]; then
  cp .env.example .env

  owner_password="$(openssl rand -hex 24)"
  app_password="$(openssl rand -hex 24)"
  django_secret="$(openssl rand -hex 48)"
  mfa_key="$(openssl rand -base64 32 | tr '+/' '-_' | tr -d '\n')"

  sed -i "s/change-me-owner/${owner_password}/g" .env
  sed -i "s/change-me-app/${app_password}/g" .env
  sed -i "s/change-me-with-at-least-50-random-characters/${django_secret}/g" .env
  sed -i "s/^MFA_ENCRYPTION_KEYS=$/MFA_ENCRYPTION_KEYS=${mfa_key}/" .env

  if [[ -n "${CODESPACE_NAME:-}" ]]; then
    forwarding_domain="${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
    codespace_host="${CODESPACE_NAME}-8000.${forwarding_domain}"
    sed -i "s|^DJANGO_ALLOWED_HOSTS=.*|DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,${codespace_host}|" .env
    sed -i "s|^DJANGO_CSRF_TRUSTED_ORIGINS=.*|DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8000,https://${codespace_host}|" .env
  fi

  echo "Arquivo .env local criado com segredos aleatorios (nao versionados)."
else
  echo "Arquivo .env existente preservado."
fi

echo
echo "Para criar os containers e executar os primeiros testes:"
echo "  bash .devcontainer/first-test.sh"
