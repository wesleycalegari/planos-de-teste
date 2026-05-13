# Plano de teste E2E — BUG 6842 — Erro cálculo prêmio RCV (DM/DC)

| Campo | Valor |
|-------|--------|
| Work item | [BUG 6842](https://dev.azure.com/SimetriasDev/CITWEB/_workitems/edit/6842) |
| Sprint | Sprint 6 Citweb (`CITWEB\Sprint_6_Citweb`) |
| Base SQL (massa real) | **smt-hom-citweb-kovr** (`smt-hom-citweb.database.windows.net`) |
| Apólice (`u_apo_pnc`) | **15122025** |
| Filial (`c_org_prd`) | **1** |
| Ramo | **59** (RCV) |
| Subgrupo (cadastro) | **1** *(confirmar na tela; distinct em `tb_sgp_col_cit`)* |

## Snapshot SQL (KOVR — consulta de referência)

**`tb_apo_nac_cit` + `tb_apo_cit`** para a massa acima *(executado na homologação)*:

- `u_apo_pnc = 15122025`, `c_org_prd = 1`, `c_rmo = 59`
- Vigência nacional: **2025-08-01** → **2026-08-01**
- `d_can_apo`: **NULL** (sem cancelamento na nacional)

**`tb_mov_avb_rcv_cit`:** neste snapshot **não há linhas** para essa apólice/filial/ramo — os CTs de persistência devem rodar **após** inclusão de nova averbação no teste.

## Premissa de UI — cálculo automático

No **CITWEB**, **não existe** passo de “clicar em botão Calcular” para o prêmio RCV. O valor é atualizado por **gatilhos de campo** (por exemplo `onchange` / **blur** / perda de foco) quando os **campos obrigatórios** estão consistentes.

## Validação núcleo CITNET / SQL

Após gravar a averbação, validar persistência dos limites DM/DC e coerência do prêmio:

```sql
SELECT TOP (20)
    u_apo_pnc,
    c_org_prd,
    c_rmo,
    u_sgp,
    u_avb,
    v_lmr_dm,
    v_lmr_dc,
    v_cml_pmo,
    v_tar_pmo,
    d_sda_vgm
FROM dbo.tb_mov_avb_rcv_cit WITH (NOLOCK)
WHERE u_apo_pnc = 15122025
  AND c_org_prd = 1
  AND c_rmo = 59
ORDER BY u_avb DESC;
```

**Esperado:** `v_lmr_dm` / `v_lmr_dc` alinhados ao fallback da apólice ou aos valores informados na averbação, conforme regra da correção (Bug 6842 / task 6848); prêmio não deve colapsar a zero apenas por divergência de indicativo.

Opcional — controlo de funcionalidade:

```sql
SELECT n_fun_sis, i_fun_sis
FROM dbo.tb_ctl_sis_cit WITH (NOLOCK)
WHERE n_fun_sis IN ('EditarDmDcRamo59', 'Ind_Taxa_Por_Percurso');
```

---

## Casos de teste (BDD)

### Feature: Prêmio RCV por gatilhos de campo e fallback DM/DC

```gherkin
Feature: Cálculo automático do prêmio RCV (sem botão Calcular)
  Como operador CITWEB
  Quero que DM/DC e prêmio reflitam a apólice 15122025 e a condição comercial sem ação explícita de cálculo
  Para validar a correção do Bug 6842 em ambiente KOVR HML

  Background:
    Given base de dados smt-hom-citweb-kovr
    And apólice 15122025, filial 1, ramo 59, subgrupo 1
    And o prêmio é recalculado por gatilhos de interface (onchange/blur), não por botão "Calcular"

  @CT-BUG-6842-B01 @P1
  Scenario: Fallback DM/DC da apólice atualiza prêmio automaticamente ao completar obrigatórios e sair do foco
    Given estou na averbação RCV vinculada à apólice 15122025, filial 1, subgrupo 1
    And a condição comercial vigente da apólice está definida para o cenário de teste
    When preencho todos os campos obrigatórios da averbação exceto DM/DC quando o caso exercitar fallback
    And para cada campo obrigatório, ao concluir o preenchimento, movimento o foco para fora do campo (Tab ou clique fora) para disparar o processamento automático
    Then os campos DM e DC na averbação passam a exibir os valores de fallback provenientes da apólice 15122025 quando aplicável
    And o valor do prêmio exibido na tela atualiza-se automaticamente sem clicar em qualquer botão de cálculo
    When confirmo a gravação da averbação
    Then em dbo.tb_mov_avb_rcv_cit existe linha para (15122025, 1, 59, u_sgp do teste, u_avb gerado)
      And v_lmr_dm e v_lmr_dc persistem de forma coerente com o exibido antes da gravação
      And v_cml_pmo / v_tar_pmo refletem o resultado do fluxo automático, sem zeramento indevido

  @CT-BUG-6842-B02 @P1
  Scenario: Alteração manual de DM/DC recalcula prêmio ao blur, sem botão Calcular
    Given estou na averbação RCV da apólice 15122025, filial 1, subgrupo 1 com DM/DC já refletindo fallback ou valores iniciais
    When altero DM e/ou DC para valores distintos dos da apólice
    And saio do campo alterado (perda de foco)
    Then o prêmio na interface atualiza-se automaticamente
    When gravo o movimento
    Then tb_mov_avb_rcv_cit registra v_lmr_dm e v_lmr_dc iguais aos valores finais da averbação

  @CT-BUG-6842-B03 @P2
  Scenario: Playwright — blur como gatilho, não clique em Calcular
    Given automação aponta para URL de averbação RCV do ambiente KOVR
    When localizo campos com locator resiliente (ex.: page.locator("[id$='SufixoEstável']"))
    And aplico fill + blur (Tab ou locator.blur()) nos obrigatórios e em DM/DC quando aplicável
    Then aguardo estabilização do elemento que exibe o prêmio (expect com timeout adequado)
    And não existe passo que clique em botão de calcular prêmio

  @CT-BUG-6842-B04 @P2
  Scenario: Regressão — indicativo e cadastro alinhados não geram prêmio zerado por DM/DC ignorados
    Given EditarDmDcRamo59 e fluxo de cadastro/averbação conforme escopo da correção
    When executo fluxo completo com gatilhos de campo até gravação
    Then prêmio na UI e totais em tb_mov_avb_rcv_cit permanecem consistentes com a condição comercial e limites DM/DC
```

---

## Evidências

Registrar screenshots por CT (login, tela com prêmio após blur, resultado SQL).

---

*Documento gerado para revisão — Bug 6842 — massa **15122025** / filial **1** / base **smt-hom-citweb-kovr**.*
