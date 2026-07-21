# Modelo de domínio

## Fundação

- `Tenant`: fronteira de dados, segurança e operação.
- `Organization`: operadora direta ou consultoria dentro do tenant.
- `Company`: empresa cliente, identificada por CNPJ quando aplicável.
- `Establishment`: unidade separada da empresa, futura proprietária de eleições e mandatos.
- `User`: identidade administrativa por e-mail.
- `Role`: catálogo imutável dos nove papéis do produto.
- `UserMembership`: papel atribuído em um escopo tenant/organização/empresa/estabelecimento.
- `AccountInvitation`: convite de uso único que materializa usuário e membership.
- `PrivilegedAccessGrant`: acesso temporário e justificado de plataforma/suporte.
- `AuditEvent`: fato append-only encadeado por tenant ou plataforma.

## Futuro eleitoral

- `Employee` é cadastro administrativo; `Voter` é snapshot eleitoral versionado.
- `Election` pertence a um estabelecimento e evolui por máquina de estados.
- `ElectionSchedule` referencia regras versionadas, nunca prazos soltos em views.
- `CandidateApplication` preserva decisão, justificativa e auditoria.
- `ElectionParticipation` registra somente que alguém participou.
- `Ballot` contém somente eleição e escolha anônima, sem chave identificadora.
- `ElectionResult`, `DocumentVersion` e `Mandate` derivam de snapshots fechados.
- `NotificationOutbox` acopla confirmação de negócio e entrega assíncrona sem perda.

## Invariantes

- Company e Establishment repetem `tenant_id` para constraint e RLS, validado contra o ancestral.
- Um membership possui apenas campos de escopo compatíveis com seu papel.
- Objetos desativados não são apagados silenciosamente.
- Auditoria não aceita escolha eleitoral nem segredo em metadata.
