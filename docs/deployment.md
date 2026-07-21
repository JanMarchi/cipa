# Deployment

## Perfis de banco

- `migration`: proprietário controlado, usado apenas em deploy.
- `application`: sem `BYPASSRLS`, sem ownership e sem direito de alterar policies/triggers.

O deploy executa: build imutável → auditoria de dependências → migrations com lock → collectstatic → checks → troca de aplicação → smoke de health/readiness.

Produção exige HTTPS no proxy confiável, secret manager, bucket privado, backups cifrados, teste de restauração, Redis autenticado/restrito e logs estruturados com redaction.

A credencial de migrations e funções privilegiadas deve ser separada da aplicação e possuir `BYPASSRLS` (ou superusuário somente no ambiente local), para que funções `SECURITY DEFINER` validem memberships sob `FORCE ROW LEVEL SECURITY`. Ela nunca é entregue ao processo web/worker; `cipa_app` permanece `NOSUPERUSER NOBYPASSRLS`. Senhas inseridas em URLs PostgreSQL precisam estar percent-encoded.

Rollback de aplicação não implica rollback destrutivo de schema. Migrations devem seguir expansão/contração quando houver dados reais.
