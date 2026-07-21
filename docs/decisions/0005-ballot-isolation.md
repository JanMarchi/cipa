# ADR 0005 — Isolamento futuro da urna

**Decisão:** schema `ballot_box` no mesmo PostgreSQL durante o MVP, sem FKs para identidade e com privilégios próprios.

**Consequência:** preserva atomicidade local. Banco separado só será adotado com protocolo que mantenha idempotência e reconciliação sem criar vínculo eleitor-voto.
