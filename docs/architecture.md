# Arquitetura

## Visão

Monólito modular Django com HTML server-rendered. Cada app contém modelos, serviços de escrita, seletores de leitura, policies, views/forms e testes. Não existe API pública na Fase 1.

## Módulos da Fase 1

- `core`: tipos base, middleware, health checks e logging.
- `accounts`: usuário administrativo, convite, sessão, papéis e memberships.
- `tenants`: fronteira de segurança e contexto RLS.
- `organizations`: organização operadora e empresas clientes.
- `establishments`: unidades onde existirão eleições.
- `audit`: eventos append-only e cadeia de integridade.

## Fluxo de request

1. Correlation ID é aceito somente se válido ou gerado novamente.
2. Django autentica a sessão server-side.
3. O middleware resolve o tenant previamente autorizado da sessão.
4. Uma transação define `app.user_id` e `app.tenant_id` com `SET LOCAL`.
5. Policy valida ação e objeto; RLS limita linhas mesmo em consulta incompleta.
6. Serviços escrevem estado e auditoria na mesma transação.

## RLS

O usuário web não é proprietário das tabelas e não tem `BYPASSRLS`. Migrations usam credencial separada. Tabelas tenant-owned usam `ENABLE/FORCE ROW LEVEL SECURITY` e `tenant_id = current_setting('app.tenant_id', true)::uuid`. Sem contexto, o acesso falha fechado.

A seleção de tenant usa função `SECURITY DEFINER` com `search_path` fixo. Ela consulta membership/grant ativo e devolve apenas booleano. Tasks Celery recebem `tenant_id` explicitamente e reutilizam o context manager.

Validades temporais nas funções de autorização usam `statement_timestamp()`. Isso evita que uma membership criada dentro de uma transação longa seja comparada ao instante fixo do início da transação, sem reduzir o isolamento ou criar bypass de RLS.

## Fronteira futura da urna

`ballot_box` ficará no schema PostgreSQL `ballot_box`, sem foreign keys ou imports para identidades. Permanecer no mesmo banco no MVP permite transação única entre cédula anônima, participação e consumo da credencial. A migração futura para banco separado exigirá protocolo idempotente específico e não será tratada como simples alteração de configuração.

## Frontend

Django Templates + HTMX com fallback HTML + Tailwind compilado. Scripts são locais para permitir CSP `script-src 'self'`. Nenhum dado de autorização é confiado ao cliente.

## ADRs

Consulte `docs/decisions/` para decisões que não devem ser revertidas incidentalmente.
