# ADR 0002 — Isolamento por aplicação e RLS

**Decisão:** tabelas compartilhadas com `tenant_id`, autorização por objeto e PostgreSQL `FORCE ROW LEVEL SECURITY`.

**Consequência:** testes dependem de PostgreSQL real; migrations usam credencial distinta do processo web.
