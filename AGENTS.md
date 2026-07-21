# Instruções permanentes para agentes

1. Leia `README.md`, `SECURITY.md` e os documentos de arquitetura antes de editar.
2. Preserve o monólito modular; não introduza microsserviços, SPA, API pública ou infraestrutura eleitoral sem necessidade aprovada.
3. Toda tabela de negócio deve declarar sua fronteira de tenant. Não use managers globais em views e não remova RLS para contornar testes.
4. Escritas relevantes passam por serviços de domínio transacionais e geram auditoria no mesmo commit.
5. Nunca registre senha, token, credencial eleitoral, conteúdo de voto ou corpo de requests de autenticação/votação.
6. `ballot_box` não pode importar nem referenciar modelos de funcionário, eleitor, credencial ou participação.
7. Não altere um estado eleitoral por edição direta; use serviços de transição.
8. Use UUIDs aleatórios, timezone-aware datetimes e apresentação pt-BR.
9. Não crie tabelas vazias para funcionalidades futuras.
10. Para cada alteração: migration consistente, testes de autorização/tenant, lint, tipos e documentação atualizada.
11. Não afirme conformidade jurídica. Registre premissas e riscos residuais.
12. Novas dependências devem estar ativamente mantidas, fixadas no lockfile e verificadas por auditoria.
