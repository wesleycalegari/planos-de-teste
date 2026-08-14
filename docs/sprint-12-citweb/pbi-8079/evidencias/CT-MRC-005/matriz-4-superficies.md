# CT-MRC-005 — Logo nas 4 superfícies (matriz)

Medido em 13/08/2026 no CITNET KOVR HML `/citnet/`.

| Superfície | Arquivo de logo (fonte) | Dimensão servida | Logo | Como medido |
|-----------|-------------------------|------------------|------|-------------|
| navbar (página inicial) | `LogoKOVR.png` | 494×95 (carregado) | **KEV** | live 13/08 — navbar da tela de login `/citnet/` |
| protocolo de averbação | `LogoKOVR.jpg` | 494×95 (carregado) | **KEV** | live 13/08 — tab PrintProtocolo, averbação 2026000001 |
| relatório (Consulta de Averbações) | parâmetro RDLC → `LogoKOVR.png` | — | **KEV** | disk mesmo dia — CT-MRC-003 |
| certificado (RCV + Exportação) | RDLC | — | **KEV** | disk mesmo dia — CT-MRC-004 |

## Leitura

- **4/4 superfícies exibem o logo KEV** — nenhum estado misto (novo/antigo) observado.
- O risco R1 (protocolo hardcoda `.jpg`, que estava 404) **não** produz estado misto: o `LogoKOVR.jpg` agora É servido e carrega a 494×95 com o conteúdo KEV. `.png` (navbar/relatórios) e `.jpg` (protocolo) convergem no mesmo logo novo.

## Ressalva de método (por que não é APROVADO fechado aqui)

O comparativo **na mesma sessão logada, com cache furado** que o CT exige NÃO foi reproduzido: o login com a credencial do `.env` (`TSTALFA1` / filial `SÃO PAULO - 1`) foi **recusado 2×** ("Verifique o nome de usuário/senha!"). As 2 superfícies live (navbar da tela de login + protocolo já renderizado) não exigiram nova autenticação; relatório e certificado vieram do disco do mesmo dia. O sinal é uniformemente KEV, mas sem o artefato single-session. **Veredito: BLOQUEADO (login) para o artefato consolidado** — recaptura numa sessão logada resolve.
