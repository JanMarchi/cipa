# Threat model da plataforma eleitoral

Escala: probabilidade e impacto `Baixo/Médio/Alto`. O risco residual pressupõe funcionamento dos controles.

| Ameaça | Impacto | Prob. | Preventivo | Detectivo | Residual |
|---|---|---|---|---|---|
| Voto duplicado, replay, duplo clique ou concorrência | Alto | Alto | constraint única, idempotência, locks e transação única | reconciliação cédulas/participações | Baixo |
| Roubo/reemissão de credencial | Alto | Médio | token forte hash-only, validade, uso único e fluxo justificado | eventos de emissão/revogação e alertas | Médio |
| Enumeração de eleitores/administradores | Médio | Alto | respostas uniformes e rate limiting | métricas de falha agregadas | Baixo |
| Administrador mal-intencionado | Alto | Médio | menor privilégio, MFA, grants e separação urna/cadastro | cadeia de auditoria e alertas | Médio |
| Correlação eleitor-voto | Alto | Médio | nenhum FK, UUIDs aleatórios, schemas/logs separados e tempo reduzido | revisão de schema/logs | Médio |
| Alteração ou exposição antecipada de resultados | Alto | Médio | estados, permissões DB e agregação somente após fechamento | snapshot/hash e reconciliação | Baixo |
| Reabertura indevida | Alto | Baixo | fluxo reforçado separado; nunca edição de campo | evento e alerta privilegiado | Baixo |
| Manipulação da lista de eleitores | Alto | Médio | freeze, versão, justificativa e autorização | diff e auditoria | Baixo |
| Candidato não autorizado | Médio | Médio | estado de candidatura e publicação por serviço | histórico de decisão | Baixo |
| Ata/documento alterado | Alto | Médio | versões, bucket privado e SHA-256 | verificação em download | Baixo |
| Falha de isolamento entre tenants | Alto | Médio | policy por objeto, tenant FK, RLS e papel DB restrito | testes cruzados e alertas | Baixo |
| Indisponibilidade na votação | Alto | Médio | capacidade, health checks, redundância e runbook | métricas/alertas | Médio |
| Vazamento por logs | Alto | Médio | redaction e proibição de bodies sensíveis | testes e scanner de logs | Baixo |
| Backup comprometido | Alto | Baixo | criptografia, IAM e retenção | testes/restauração e acesso auditado | Médio |
| Comprometimento de conta administrativa | Alto | Médio | convite, Argon2, MFA, rate limit e sessões curtas | login/auditoria/alertas | Baixo |
| Adulteração da cadeia de auditoria | Alto | Baixo | append-only, trigger e hash chain | verificador externo | Médio para DBA |
| Upload malicioso | Médio | Médio | allowlist, tamanho, bucket privado e futura varredura AV | quarentena e eventos | Baixo |

O operador de banco continua sendo uma fronteira de confiança residual. Nenhum controle aqui constitui certificação jurídica ou garantia absoluta de sigilo.
