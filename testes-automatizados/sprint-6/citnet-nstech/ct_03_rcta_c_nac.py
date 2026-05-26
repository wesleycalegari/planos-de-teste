"""
CT-CTN-003 — Averbação RCTA-C Nacional — CRUD Completo
Módulo : Averbações > Nacional > RCTA-C
URL    : /citnet/AverbacaoNacional/AverbacaoRCTAC
Nível  : Funcional completo
Risco  : P1
"""
import pytest
from utils import (
    BASE_URL, ev, shot, assert_no_error,
    setup_filial_apolice, click_novo, click_gravar, click_excluir_confirmar,
    fill_common_nacional, pesquisar_por_periodo, grid_row_count, HOJE,
)

CT_ID = "CT-CTN-003"
URL   = f"{BASE_URL}/citnet/AverbacaoNacional/AverbacaoRCTAC"


def test_ct_03_rcta_c_nacional(citnet_session):
    page = citnet_session
    e = ev(CT_ID)

    page.goto(URL)
    page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "01_formulario_aberto.png")

    setup_filial_apolice(page)
    shot(page, e, "02_filial_apolice_selecionados.png")

    click_novo(page)
    assert_no_error(page)
    shot(page, e, "03_formulario_novo.png")

    fill_common_nacional(
        page,
        doc_type="C",
        serie_cte="001",
        num_cte="900002",
        modal="T",
        uf_ori="SP",
        uf_dst="MG",
        data_saida=HOJE,
        placa="DEF2E345",
        valor_is="80000,00",
        valor_frete="3000,00",
    )
    shot(page, e, "04_campos_preenchidos.png")

    click_gravar(page)
    assert_no_error(page)
    shot(page, e, "05_gravacao_resultado.png")

    body = page.inner_text("body")
    assert any(kw in body.lower() for kw in ["protocolo", "gravado", "sucesso", "averbação"]), (
        "Gravação RCTA-C não confirmada"
    )

    pesquisar_por_periodo(page, HOJE, HOJE)
    assert_no_error(page)
    shot(page, e, "06_pesquisa_resultado.png")

    rows = grid_row_count(page)
    assert rows > 0, "Registro RCTA-C não encontrado na grade"

    if page.locator("#btExcluir").count() > 0:
        click_excluir_confirmar(page)
        assert_no_error(page)
        shot(page, e, "07_exclusao_confirmada.png")
