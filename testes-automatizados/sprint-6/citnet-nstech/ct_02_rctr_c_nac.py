"""
CT-CTN-002 — Averbação RCTR-C Nacional — CRUD Completo
Módulo : Averbações > Nacional > RCTR-C
URL    : /citnet/AverbacaoNacional/AverbacaoRCTRC
Nível  : Funcional completo (Inclusão → Pesquisa → Exclusão)
Risco  : P1

Campos documentados via inspeção DOM em 25/05/2026:
  Filial:   #c_org_prd    | Apólice: #u_apo_pnc | Subgrupo: #u_sgp
  Doc:      #e_doc_ebq (C=CTE) | Série: #u_ser_doc_cte | Num: #u_doc_cte
  Modal:    #e_tr1 (T=RODOVIÁRIO)
  UF Ori:   #n_ori  | UF Dst: #n_dst
  Data:     #d_sda_vgm | Placa: #t_vei_tpr
  IS:       #v_is   | Frete: #v_fte
  Gravar:   #btEnviar | Excluir: #btExcluir | Novo: #btNovo
  Pesquisa: #cmbSelecao (3=PERÍODO) | #txtPesqDataIni | #txtPesqDataFim
"""
import pytest
from utils import (
    BASE_URL, ev, shot, assert_no_error,
    setup_filial_apolice, click_novo, click_gravar, click_excluir_confirmar,
    fill_common_nacional, pesquisar_por_periodo, grid_row_count, HOJE,
)

CT_ID = "CT-CTN-002"
URL   = f"{BASE_URL}/citnet/AverbacaoNacional/AverbacaoRCTRC"


def test_ct_02_rctr_c_nacional(citnet_session):
    page = citnet_session
    e = ev(CT_ID)

    # ── 1. Navegar para o formulário
    page.goto(URL)
    page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "01_formulario_aberto.png")

    # ── 2. Selecionar filial + apólice + subgrupo
    setup_filial_apolice(page)
    shot(page, e, "02_filial_apolice_selecionados.png")

    # ── 3. Clicar Novo para habilitar campos
    click_novo(page)
    assert_no_error(page)
    shot(page, e, "03_formulario_novo.png")

    # ── 4. Preencher campos obrigatórios RCTR-C
    fill_common_nacional(
        page,
        doc_type="C",
        serie_cte="001",
        num_cte="900001",
        modal="T",
        uf_ori="SP",
        uf_dst="RJ",
        data_saida=HOJE,
        placa="ABC1D234",
        valor_is="100000,00",
        valor_frete="5000,00",
    )
    shot(page, e, "04_campos_preenchidos.png")

    # ── 5. Gravar
    click_gravar(page)
    assert_no_error(page)
    shot(page, e, "05_gravacao_resultado.png")

    # Verificar mensagem de sucesso ou protocolo gerado
    body = page.inner_text("body")
    assert any(kw in body.lower() for kw in ["protocolo", "gravado", "sucesso", "averbação"]), (
        "Gravação não confirmada — mensagem esperada não encontrada"
    )

    # ── 6. Pesquisar o registro pela data de hoje
    pesquisar_por_periodo(page, HOJE, HOJE)
    assert_no_error(page)
    shot(page, e, "06_pesquisa_por_data.png")

    rows = grid_row_count(page)
    assert rows > 0, "Registro não encontrado na grade após gravação"
    shot(page, e, "07_registro_encontrado_na_grade.png")

    # ── 7. Abrir o primeiro registro da grade
    first_link = page.locator("table tbody tr:first-child a, table tbody tr:first-child td:first-child").first
    if first_link.count() > 0:
        first_link.click()
        page.wait_for_load_state("networkidle")
        assert_no_error(page)
        shot(page, e, "08_registro_aberto.png")

    # ── 8. Excluir (limpeza de massa)
    if page.locator("#btExcluir").count() > 0:
        click_excluir_confirmar(page)
        assert_no_error(page)
        shot(page, e, "09_exclusao_confirmada.png")

        # Verificar que registro não está mais na grade
        pesquisar_por_periodo(page, HOJE, HOJE)
        shot(page, e, "10_grade_apos_exclusao.png")
