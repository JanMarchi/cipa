# Fluxo eleitoral futuro

Estados previstos: `DRAFT`, `PLANNED`, `NOTICE_PUBLISHED`, `REGISTRATION_OPEN`, `REGISTRATION_CLOSED`, `CANDIDATES_UNDER_REVIEW`, `CANDIDATES_APPROVED`, `VOTER_LIST_FROZEN`, `VOTING_SCHEDULED`, `VOTING_OPEN`, `VOTING_EXTENDED`, `VOTING_CLOSED`, `COUNTING`, `RESULT_PUBLISHED`, `HOMOLOGATED`, `CANCELLED`.

Cada transição será executada por serviço de domínio, validará pré-condições, registrará ator/horário, será idempotente quando necessário e produzirá auditoria. Não haverá edição livre de estado.

O fluxo da votação será: autenticar credencial → validar elegibilidade → exibir cédula → confirmar → transação atômica para inserir cédula anônima, marcar participação e consumir credencial → comprovante sem escolha.

Nenhum resultado parcial será calculado ou exposto durante a votação.
