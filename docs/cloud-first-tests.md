# Primeiros testes na nuvem

Este fluxo usa um GitHub Codespace apenas como ambiente temporario. Ele nao publica a aplicacao em producao, nao exige dados reais e evita instalar Docker, PostgreSQL ou Redis no computador local.

## Criar o ambiente

1. Abra o repositorio `JanMarchi/cipa` no GitHub.
2. Selecione **Code**, depois **Codespaces** e **Create codespace on main**.
3. Aguarde a mensagem do bootstrap no terminal.
4. Execute:

   ```bash
   bash .devcontainer/first-test.sh
   ```

O script gera um `.env` ignorado pelo Git com segredos aleatorios, cria os containers, aplica as migrations, executa a seed ficticia e roda os testes de integracao com PostgreSQL, Redis e RLS. Ao final, os quatro servicos ficam ativos para inspecao.

## Abrir e encerrar

A porta `8000` e encaminhada de forma privada. Abra-a pela aba **Ports** do Codespaces.

Quando terminar:

```bash
docker compose down --volumes
```

Depois, pare ou exclua o Codespace pelo GitHub para interromper o consumo da cota. Nenhum dado desse ambiente deve ser tratado como permanente.

## GitHub Actions

O workflow de CI executa os mesmos gates em PostgreSQL e Redis reais em pushes para `main`, pull requests e acionamento manual. Alteracoes somente em Markdown nao disparam a suite completa.

## Limites desta etapa

- O ambiente e exclusivo para criacao e primeiros testes.
- Nao ha dominio, deploy permanente, SLA, backup ou dados de producao.
- O fluxo E2E com navegador continua como gate posterior; a primeira execucao cobre testes unitarios e de integracao, incluindo RLS.
