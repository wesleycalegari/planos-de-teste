# CT-MRC-010 — Caça-string "KOVR": classificação MARCA × IDENTIFICADOR

Rodada de **reteste pós-fix do Bug #8121** (migração do `infoCliente` índice 2 no `web.KOVR.config`).
Regra do CT: **MARCA** (nome exibido ao usuário) deve ter virado KEV; **IDENTIFICADOR técnico**
deve permanecer KOVR — "sumiu todo KOVR" seria falso positivo.

## (a) MARCA exibida ao usuário — DEVE ser "KEV SEGUROS S.A."

| # | Superfície | 1ª rodada (13/08, pré-fix) | Reteste (14/08, pós-fix) | Captura do pós-fix |
|---|-----------|----------------------------|---------------------------|--------------------|
| a1 | Cabeçalho do protocolo de averbação | `KOVR Seguradora - Averbação - Diária` | **não recapturado** | — (ver ressalva) |
| a2 | Corpo do protocolo ("…através do site da …") | `KOVR Seguradora` | **não recapturado** | — (ver ressalva) |
| a3 | Cabeçalho do relatório Consulta de Averbações (Nacional) | `KOVR Seguradora - CONSULTA DE AVERBAÇÕES` | **`KEV SEGUROS S.A. - CONSULTA DE AVERBAÇÕES`** | `../CT-MRC-007/consulta-averbacoes-nacional-header-KEV.png` |
| a4 | Cabeçalho do relatório Consulta de Averbações Internacionais | `KOVR Seguradora - … INTERNACIONAIS` | **`KEV SEGUROS S.A. - … INTERNACIONAIS`** | `../CT-MRC-007/consulta-averbacoes-internacional-exportacao-header-KEV.png` |
| a5 | `<title>` da página `/citnet/` (aba do navegador) | `KOVR Seguradora- CitNet` | **`KEV SEGUROS S.A.- CitNet`** | `login-document-title-KEV.png` |

As cinco superfícies (a) têm a **mesma fonte**: o nome resolvido de `web.KOVR.config` →
`infoCliente` índice 2. O valor pré-fix era `KOVR Seguradora`; o fix do #8121 migrou para
`KEV SEGUROS S.A.`. Onde o nome é **hardcoded no RDLC** (3 certificados), a marca já estava
correta desde a 1ª rodada (CT-MRC-006).

**Re-checagem independente do a5:** em 14/08/2026 19:17 (BRT), acesso direto à tela de login
de `/citnet/` devolveu `document.title = "KEV SEGUROS S.A.- CitNet"` — confirmando que o valor
migrado do `infoCliente[2]` é o que a aplicação resolve em runtime.

### ⚠️ Ressalva de cobertura — a1 e a2 não foram recapturados

O reteste de 14/08 cobriu a3, a4 e a5. **A impressão do protocolo (a1/a2) não foi recapturada
após o fix** — a última captura dessa superfície é a de 13/08, ainda com `KOVR Seguradora`
(`ev_CT-MRC-010_01_live-protocolo-logoKEV-nomeKOVR_20260813.png`). A recaptura foi tentada em
14/08 e **não foi possível**: o login em `/citnet/` foi recusado (mensagem de validação padrão
do CITNET) nas duas filiais tentadas com a credencial referenciada no `.env`.

O que isso significa, sem exagerar para nenhum lado:
- a migração do `infoCliente[2]` está **provada** (a3, a4 e a5 mudaram, e o `<title>` reflete
  literalmente o novo valor);
- o cabeçalho do protocolo **lê da mesma chave** (pré-fix exibia exatamente
  `infoCliente[2] + " - Averbação - Diária"`), então a expectativa é que exiba KEV;
- mas **expectativa não é evidência**. O protocolo é justamente a superfície com caminho de
  código próprio neste card (é ele que hardcoda a extensão do logo, ver risco nº 1 do plano),
  e é a única que ainda não foi observada pós-fix.

## (b) IDENTIFICADOR técnico — CORRETO que permaneça "KOVR"

| # | Ocorrência | Tipo | Correto? |
|---|-----------|------|----------|
| b1 | `LogoKOVR.png` / `LogoKOVR.jpg` (conteúdo servido = logo KEV) | nome de arquivo de logo | ✓ permanece |
| b2 | `smt-hom-citweb-kovr` | nome da base de dados | ✓ permanece |
| b3 | `kovr-hml-faturamento.nsseg.com.br` | URL do ambiente | ✓ permanece |
| b4 | `Empresa=KOVR`, `infoCliente[0]=KOVR`, `infoCliente[4]=KOVR` | chaves de configuração | ✓ permanece |
| b5 | `web.KOVR.config`, `*_KOVR.rdlc` | nomes de arquivos de config/report | ✓ permanece |

Os identificadores técnicos estão corretamente preservados — a implementação **não** apagou
"KOVR" indevidamente. Evidência do eixo (b): `../CT-MRC-009/ev_CT-MRC-009_01_snapshot-identificadores-mascarado_20260813.png`
(`id_seg` = 1 e SUSEP 6921 preservados, `n_seg` migrado para KEV SEGUROS S.A.).

## Situação

**3 de 5** superfícies de marca recapturadas pós-fix, todas exibindo `KEV SEGUROS S.A.`;
**0 ocorrências** de "KOVR Seguradora" nas superfícies observadas. **a1/a2 pendentes de
recaptura** por bloqueio de credencial — item aberto, registrado para decisão do QA owner.
