# CT-MRC-005 — Logo nas 4 superfícies (matriz consolidada)

Rodada de **reteste pós-fix do Bug #8121**, medida em **14/08/2026** no CITNET KOVR HML `/citnet/`,
em sessão **logada** (navbar mostra o usuário autenticado). Substitui a matriz da 1ª rodada
(13/08), que ficou sem o artefato consolidado por recusa de login.

| # | Superfície | Como o logo é resolvido | Logo exibido | Captura |
|---|-----------|--------------------------|--------------|---------|
| 1 | navbar (pós-login) | `LogoKOVR.png` no `_Layout-KOVR.cshtml` | **KEV** | `01-navbar-logo-KEV.png` — 14/08, sessão logada |
| 2 | impressão do protocolo de averbação | `Logo<idLayout>.jpg` (extensão fixa, `AverbacaoNacionalController`) | **KEV** | `../CT-MRC-002/ev_CT-MRC-002_03_protocolo-logo-KEV_20260813-175000.png` — 13/08 |
| 3 | relatório — Consulta de Averbações (Nacional) | parâmetro de runtime do RDLC → `LogoKOVR.png` | **KEV** | `03-relatorio-consulta-header-KEV.png` — 14/08 |
| 3b | relatório — Consulta de Averbações Internacionais (Exportação) | idem | **KEV** | `03b-relatorio-internacional-header-KEV.png` — 14/08 |
| 4 | certificado RCV | RDLC de certificado | **KEV** | `04-certificado-rcv-banner-KEV.png` — 14/08 |

## Leitura

- **4/4 superfícies exibem o logo KEV** — nenhum estado misto (novo/antigo) observado.
- O risco R1 do plano (o protocolo hardcoda `.jpg`, que estava **HTTP 404** no baseline de 11/08)
  **não** se materializou: o `LogoKOVR.jpg` passou a ser servido com o conteúdo KEV. Os dois
  caminhos que discordam na extensão — `.png` (navbar/relatórios) e `.jpg` (protocolo) —
  convergem no mesmo logo novo.
- O fix do #8121 alterou apenas o **nome** (`infoCliente` índice 2) e não tocou no logo; por isso
  a captura do protocolo da 1ª rodada (linha 2, 13/08) permanece válida para o eixo LOGO deste CT.

## Método

- Cache furado por hard reload em cada superfície de tela.
- Identificadores técnicos preservados (`LogoKOVR.png` continua sendo o **nome do arquivo**;
  o que mudou é o **conteúdo**) — a regressão desse eixo está no CT-MRC-009.
- Credenciais deste ambiente: apenas por referência às chaves do `.env` — nenhuma credencial é
  registrada neste artefato (repositório público).
