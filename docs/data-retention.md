# Retenção e descarte

- Eventos técnicos de autenticação terão período configurável; o valor de produção depende de aprovação de privacidade e segurança.
- Dados eleitorais, documentos e auditoria não serão apagados automaticamente até existir política formal aprovada.
- Convites expirados podem ter token/hash descartado, preservando apenas o fato mínimo auditável.
- Grants expirados permanecem como evidência de acesso, sujeitos à política aprovada.
- Backups devem acompanhar os mesmos prazos e possuir rotina de expiração verificável.

Toda futura rotina de descarte deverá produzir relatório, ser idempotente, respeitar legal hold e nunca apagar cédulas isoladamente de um processo ainda retido.
