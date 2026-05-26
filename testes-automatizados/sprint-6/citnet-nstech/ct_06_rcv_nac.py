"""
CT-CTN-006 — Averbação RCV Nacional — CRUD Completo
Módulo : Averbações > Nacional > RCV
URL    : /citnet/AverbacaoNacional/AverbacaoRCV
Nível  : Funcional completo
Risco  : P1

RCV (Responsabilidade Civil do Veículo) usa ramo 59.
O formulário pode ter campos adicionais específicos (placa obrigatória,
veículo, coberturas RCV). Inspecionar os campos ao rodar pela primeira vez.
"""
import pytest
from utils import (
    BASE_URL, ev, shot, assert_no_error,
    setup_filial_apolice, click_novo, click_gravar, click_excluir_confirmar,
    fill_common_nacional, pesquisar_por_periodo, grid_row_count, HOJE,
)

CT_ID = "CT-CTN-006"
URL   = f"{BASE_URL}/citnet/AverbacaoNacional/AverbacaoRCV"


def test_ct_06_rcv_nacional(citnet_session):
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

    # RCV pode ter campos específicos — fill_common_nacional cobre os comuns
    fill_common_nacional(
        page,
        doc_type="C",
        serie_cte="001",
        num_cte="900004",
        modal="T",
        uf_ori="SP",
        uf_dst="RS",
        data_saida=HOJE,
        placa="JKL4G567",
        valor_is="150000,00",
        valor_frete="7000,00",
    )

    # Campos específicos RCV (se presentes)
    if page.locator("#v_is_rcf").count():
        page.triple_click("#v_is_rcf")
        page.fill("#v_is_rcf", "50000,00")

    shot(page, e, "04_campos_preenchidos.png")

    click_gravar(page)
    assert_no_error(page)
    shot(page, e, "05_gravacao_resultado.png")

    body = page.inner_text("body")
    assert any(kw in body.lower() for kw in ["protocolo", "gravado", "sucesso", "averbação"]), (
        "Gravação RCV não confirmada"
    )

    pesquisar_por_periodo(page, HOJE, HOJE)
    assert_no_error(page)
    shot(page, e, "06_pesquisa_resultado.png")

    rows = grid_row_count(page)
    assert rows > 0, "Registro RCV não encontrado na grade"

    if page.locator("#btExcluir").count() > 0:
        click_excluir_confirmar(page)
        assert_no_error(page)
        shot(page, e, "07_exclusao_confirmada.png")
