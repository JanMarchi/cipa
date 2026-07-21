# CIPA Eleitoral

SaaS B2B multiempresa para auxiliar a organização, execução, documentação e auditoria de processos eleitorais da CIPA. O produto não substitui análise jurídica nem garante, por si só, conformidade legal ou trabalhista.

## Estado atual

A Fase 1 implementa a fundação: autenticação administrativa por convite, MFA, isolamento por tenant, organizações, empresas, estabelecimentos, RBAC e auditoria encadeada. A urna e o cadastro eleitoral não fazem parte desta fase.

### Verificação desta entrega

- Suíte local: 37 testes aprovados e cobertura total de 84,45%.
- CI em Python 3.13.14: 39 testes aprovados e cobertura de 85,18%, usando PostgreSQL 17 e Redis 8 reais; os testes de RLS e as migrations de triggers passaram.
- Ruff, formatação, mypy, Bandit, `makemigrations --check`, `check --deploy`, build Tailwind/HTMX, lockfiles e `pip-audit` passaram no GitHub Actions.
- A Fase 1 permanece **não concluída** até demonstrar os quatro serviços saudáveis no Compose/Codespaces e o fluxo E2E convite → MFA → seleção de tenant → autorização → auditoria.

## Arquitetura

- Monólito modular em Python 3.13 e Django 5.2 LTS.
- PostgreSQL com isolamento por aplicação e Row-Level Security.
- Django Templates, HTMX e Tailwind CSS; nenhuma SPA ou API pública.
- Redis para cache/rate limiting e Celery para tarefas assíncronas.
- Arquivos privados preparados para armazenamento S3-compatible.

Consulte `docs/architecture.md`, `docs/domain-model.md` e `docs/threat-model.md` antes de alterar fronteiras de domínio ou segurança.

## Requisitos

- Docker com Compose v2; ou Python 3.13, PostgreSQL 17 e Redis 8.
- GNU Make é opcional no Windows; os comandos equivalentes estão no `Makefile`.

## Início rápido

1. Copie `.env.example` para `.env` e substitua todos os segredos.
2. Execute `docker compose up --build`.
3. Em outro terminal, execute `make migrate` para usar a credencial separada de migrations.
4. Crie dados fictícios com `make seed`.

O servidor ficará em `http://localhost:8000`. E-mails de desenvolvimento são escritos no console do serviço `web`.

## Primeiros testes na nuvem

Para não instalar Docker, PostgreSQL ou Redis neste computador, abra o repositório `JanMarchi/cipa` em um GitHub Codespace e execute:

```bash
bash .devcontainer/first-test.sh
```

Esse ambiente é temporário e serve apenas para criação e testes iniciais; não é um deploy de produção. O procedimento completo e a forma de liberar os recursos estão em `docs/cloud-first-tests.md`.

## Comandos

- Subir: `make up`
- Parar: `make down`
- Testes: `make test`
- Lint: `make lint`
- Migrations: `make migrations`
- Aplicar migrations: `make migrate`
- Seed idempotente: `make seed`

## Variáveis principais

`DJANGO_SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `DJANGO_ALLOWED_HOSTS`, `MFA_ENCRYPTION_KEYS`, `DJANGO_SETTINGS_MODULE` e as opções `AWS_*` documentadas em `.env.example`. Segredos nunca devem ser versionados.

## Usuários de demonstração

O comando `seed_demo` cria contas com e-mails sob `example.invalid`. Nenhuma senha é criada: use o fluxo de convite ou `createsuperuser` somente em desenvolvimento.

## Qualidade

O projeto usa pytest, Ruff, mypy/django-stubs, Bandit, pip-audit, migration checks e Playwright. Os testes de isolamento exigem PostgreSQL; SQLite não é substituto aceito.

## Limitações conhecidas

- A urna, eleições, eleitores, candidatos, documentos e mandatos entram nas fases posteriores.
- RLS e triggers só podem ser validados integralmente em PostgreSQL.
- Políticas de retenção, licença do Redis e textos jurídicos exigem revisão especializada.

## Próximos passos

Concluir e demonstrar todos os gates da Fase 1 antes de iniciar a administração eleitoral da Fase 2. Consulte `docs/roadmap.md`.
