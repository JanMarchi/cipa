# ADR 0004 — Auditoria encadeada

**Decisão:** eventos append-only, serialização canônica, SHA-256 e head serializado por lock.

**Consequência:** detecta adulteração acidental/maliciosa comum, mas não elimina confiança no DBA.
