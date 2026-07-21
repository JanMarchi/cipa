# Política de segurança

## Relato de vulnerabilidades

Não abra issue pública com detalhes exploráveis. Envie o relato ao canal privado definido pelo operador, contendo impacto, reprodução mínima e versão afetada. O canal definitivo deve ser configurado antes de produção.

## Princípios

- Menor privilégio, negação por padrão e autorização por objeto.
- Isolamento duplo: políticas da aplicação e PostgreSQL RLS.
- Segredos exclusivamente por variáveis ou secret manager.
- HTTPS obrigatório em produção, cookies `Secure`, `HttpOnly` e `SameSite=Lax`.
- CSRF, CSP, proteção contra clickjacking e headers de segurança habilitados.
- Uploads privados, com allowlist de tipo/tamanho e interface para antivírus nas fases que aceitarem arquivos.
- Dependências fixadas, CI com `pip-audit` e política de atualização mensal/emergencial.

## Dados proibidos em logs

Senhas, tokens de convite/recuperação, segredos MFA, credenciais eleitorais, corpo integral de autenticação/votação e qualquer escolha eleitoral.

## Acesso privilegiado

Suporte e plataforma não possuem bypass permanente de tenant. O acesso exige grant temporário, justificativa, MFA e evento de auditoria.

## Limites

A cadeia hash detecta alterações, mas não impede que um administrador de banco comprometido reescreva dados e hashes. Backups, restauração, segregação de funções e monitoramento externo continuam necessários.
