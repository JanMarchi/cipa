# Roadmap

1. Fundação: identidade administrativa, tenant/RLS, RBAC, empresas, estabelecimentos e auditoria.
2. Administração eleitoral: mandato, eleição/estados/calendário, eleitores versionados e candidaturas.
3. Urna: credenciais hash-only, schema isolado, voto único atômico e comprovante de participação.
4. Participação/apuração: prorrogação, fechamento, integridade, desempate e resultado imutável.
5. Operação: outbox, notificações, PDFs versionados, observabilidade, hardening e E2E.
6. Gestão do mandato: reuniões, atas, presença, ações e evidências.

Cada fase exige migrations, testes, lint, documentação, demonstração e ausência de regressão. A Fase 3 não começa sem os gates de isolamento da Fase 1.
