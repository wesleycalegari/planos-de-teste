# Reteste PBI-5201 "Taxa por Cidade" — 11/08/2026

**Ambiente:** CITWEB HML BERKLEY · `berkley-hml-faturamento.nsseg.com.br`
**Builds medidos no módulo (não no Login):** NACIONAL `V 1.0.260804.1118` · CONVERSOR `V 1.0.260803.1850`
**Usuário:** SUPORTE · **Massa:** apólice `0000900654001` / filial `901` / subgrupo `001` / ramo 54 RCTR-C

## Gate de DoD
As 4 tasks de QA do PBI estão em **"Pronto para homologação"** desde 04/08/2026 (Roger Victor),
sem comentário de entrega. Fix confirmado **por conteúdo na branch** (não por hash e não pelo
rodapé — ver `reference_build_por_modulo`):

| PR | data | o que entrega |
|---|---|---|
| 1473 | 30/07 | **tela nova** `CondicoesComerciaisPorMunicipio.aspx` + tabela `tb_sgp_nac_cml_cdd_cit` + correção do SELECT de `Fu_Acessa_Condicao_Comercial_Municipio` (`Sql =` → `Sql +=`, que zerava a query) |
| 1507 | 03/08 | aviso não-bloqueante ADO-7778; `return retorno` no lugar de `return true`; null-safe em `RelatorioPrevia/FechamentoDomain`; `IsNullOrEmpty(u_cnh_elt)` |
| 1515/1517/1518 | 03-04/08 | ajuste do link que abre o modal de cadastro |

`DadosApolice/CondicoesComerciaisPorMunicipio.aspx.cs` presente em **origin/hml** e **origin/hml_fix**;
ausente em main / main_fix / stg.

**Mudança de premissa do teste:** a taxa por município deixou de ser a pseudo-UF `PD` em
`tb_tax_nac_cit` e passou a ser **Condição Comercial por Município** da apólice
(`tb_sgp_nac_cml_cdd_cit`), cadastrada pela tela nova. Massa criada para este reteste:
`SP/PERDIZES(9999) → SP/CAMPINAS(9502) = Taxa Comercial 0,123450` (vig. 31/12/2024–31/12/2026).
Referências de contraste: CC "por estado" da apólice = **0,050000** · `tb_tax_nac_cit` SP→SP = **0,020000**.

---

## Placar

| CT | Task | Cenário | 17/07 | 11/08 |
|---|---|---|---|---|
| CT-CVR-001 | **#7833** | Conversor RCTR-C com município → taxa do município | REPROVADO | ✅ **APROVADO** |
| CT-MUN-004 | **#7778** | Município sem taxa cadastrada → avisar o usuário | REPROVADO | ✅ **APROVADO** |
| CT-REG-001 | **#7779** | Gravar averbação sem município (regressão HTTP 500) | REPROVADO | ✅ **APROVADO** |
| CT-MUN-003 | — | Cálculo manual com município com taxa | APROVADO | ✅ **APROVADO** (re-medido) |
| CT-REL-001 | **#7824** | Relação de Embarques com coluna município | REPROVADO 500 | ⚠️ **500 corrigido / CA REPROVADO** |
| CT-REL-002 | **#7824** | Relação Simplificada com coluna município | REPROVADO 500 | ⚠️ **500 corrigido / CA REPROVADO** |
| CT-REL-003 | **#7824** | Resumo de Embarques com coluna município | REPROVADO 500 | ⚠️ **500 corrigido / CA REPROVADO** |
| CT-ATM-001 | — | Averbação via ATM com município (código numérico) | BLOQUEADO | ✅ coberto pelo CT-CVR-001 |

---

## Evidências por CT

### CT-CVR-001 (#7833) — APROVADO
Arquivo TXT gerado por `gerar_txt_reteste_municipio.py` com Município Origem `9999` (pos 200-206)
e Destino `9502` (pos 208-214); layout **TASK 4524 - TESTE CONVERSOR RCTRC** lê os dois campos.
Importar → Converter (1 lido / 1 aceito / 0 rejeitado) → Processar → *"Conversão do arquivo
concluído com sucesso!"*, grid **Aceitas** com "Averbação (202600000051) incluída".

Medição no banco (`tb_mov_avb_nac_cit`) — **a coluna do defeito original é `f_cml_bsc_vgm`**:

| averbação | origem | c_cdd_ori | destino | c_cdd_dst | f_tar_bsc_vgm | **f_cml_bsc_vgm** | prêmio |
|---|---|---|---|---|---|---|---|
| 202600000017 (17/07, Conversor) | SP | 9999 | SP | 0 | — | **0,02 (ESTADO)** ← defeito | — |
| **202600000051 (11/08, Conversor)** | SP | 9999 | SP | 9502 | 0,02 | **0,12345 (MUNICÍPIO)** ✅ | 133,45 |

Arquivos: `ev_CVR001_01..04`, `RelatorioResultadoCarga_CVR001_11082026_143938.xlsx`
(Status: Sucesso · 1 registro · 1 aceito · 0 rejeitados).

### CT-MUN-004 (#7778) — APROVADO
SP/SANTOS(48500) → SP/CAMPINAS(9502), rota **sem** CC por município. Aviso exibido:
> "Não há taxa cadastrada para o município de origem/destino selecionado."

Não bloqueia o cálculo: IS 120.000,00 → taxa 0,020000 (estado) + 0,010000 avarias → prêmio 36,00.
Arquivo: `ev_MUN004_04_aviso-visivel-fullpage_20260811-142800.png`.

### CT-REG-001 (#7779) — APROVADO
4 averbações gravadas SP→MG **sem município** (202600000047/48/49/50).
`POST /Nacional/AverbacaoRCTRC/Gravar` → **HTTP 200** nas duas medições de rede;
mensagem *"Inclusão efetuada com sucesso!"*. O 500 original não reproduz.

### CT-MUN-003 — APROVADO
SP/PERDIZES → SP/CAMPINAS: Taxa Comercial **0,123450**, Referencial 0,020000, IS 150.000 →
prêmio 200,18. Persistido na averbação 202600000046.

---

## ⚠️ Achados novos (não existiam no plano de 17/07)

### A1 — Relatórios: coluna de município vazia ou inexistente (P1, deriva do #7824)
O HTTP 500 foi corrigido (o fix tornou o `SingleOrDefault(...).n_dsc_mnp` null-safe), **mas o
critério de aceite do PBI — "criação de colunas específicas incluindo o Município" nos 3
relatórios — não é atendido**:

- **Relação de Embarques**: tem os rótulos `Município Origem:` / `Município Destino:`, e o valor
  vem **vazio em 6 de 6 linhas**, inclusive nas averbações 202600000046 e 202600000051 que têm
  município gravado no banco (9999 → 9502). Ou seja: o crash virou campo em branco.
- **Relação de Embarques Simplificada**: **não tem coluna de município** (Nº Averbação, Data Saída,
  Documento, Veículo, Estado Origem, Estado Destino, Valor, Taxa Média, Prêmio, Qtde).
- **Resumo de Embarques**: agrupa **só por UF** (SP→MG, SP→SP). Sem município.

Arquivo: `REL_previa_0000900654001_08-2026.zip` (6 XLSX, 102 KB, todos válidos e não-vazios).

### A2 — Conversor rejeita linha quando a coluna de município está mapeada e vazia (P2)
Com o layout que mapeia Município (TASK 4524 — o mesmo do CT-CVR-001), uma linha **sem** município
é rejeitada na conversão:
> `Município de Origem 200 206 — ERRO: Municípo de origem para UF: SP NÃO CADASTRADO`
> `Município de Destino 208 214 — ERRO: Municípo de Destino para UF: SP NÃO CADASTRADO`

Campo vazio está sendo tratado como "município inexistente". **Discriminador executado:** com o
layout que **não** mapeia as posições (RCTRC TESTE NSTECH - TAXA MUNICIPIO), o mesmo arquivo não
produz nenhum erro de município (o único erro é de Subgrupo, por diferença de posições do layout).
Logo a rejeição vem de *coluna mapeada + conteúdo vazio*, não de outro campo.
Impacto: quem mapear a coluna para se beneficiar do PBI passa a ter rejeitada toda linha sem município.
(Há ainda um erro de digitação na mensagem: "Municípo".)

### A3 — Tela nova: Salvar bloqueia sem exibir mensagem (P3)
Em "Condição Comercial por Município", salvar sem preencher **Município de Destino** não grava e
**não exibe nenhuma mensagem**: `Page_Validators → cvrMunicipioDestino.isvalid = false`, mas o
`validation-summary-errors` fica com `<ul></ul>` e o container `divAlertSummary` com `display:none`.
Confirmado no banco: `COUNT(*)` de `tb_sgp_nac_cml_cdd_cit` inalterado (471) após o clique.

---

## Observação de escopo
O #5201 e suas 4 tasks estão em `CITWEB\RollOut CITWEB` / `Sprint_11_Rollout`, atribuídas a
**Roger Victor** — fora do board de melhoria coberto pela rotina. Este reteste foi executado por
pedido direto do Wesley (sessão ad-hoc), não pela varredura automática.

## Massa criada nesta sessão (HML)
- CC por município: `900654001/901/sgp 1 · SP/9999 → SP/9502 · TXCML 0,123450`
- Averbações: `202600000046` (manual, com município), `47/48/49/50` (manual, sem município),
  `202600000051` (Conversor, com município)
