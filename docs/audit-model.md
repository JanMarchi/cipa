# Modelo de auditoria

Eventos são imutáveis, ordenados por cadeia e particionados logicamente por plataforma/tenant. A serialização de hash é JSON canônico UTF-8 com campos allowlisted, hash anterior e SHA-256.

`AuditChainHead` é bloqueado durante append para evitar bifurcações concorrentes. O evento e a alteração de negócio compartilham a mesma transação.

Triggers bloqueiam update/delete pelo papel da aplicação. O comando `verify_audit_chain` recalcula toda a cadeia e retorna erro ao detectar divergência.

Metadados não recebem senha, token, conteúdo de voto, identificador de cédula ou corpo integral de request. Falhas sem tenant conhecido pertencem à cadeia de plataforma.
