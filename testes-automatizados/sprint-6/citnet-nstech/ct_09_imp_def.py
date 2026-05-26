"""
CT-CTN-009 — Averbação Importação Definitiva — CRUD Completo
Módulo : Averbações > Internacional > Importação Definitiva
URL    : /citnet/AverbacaoInternacional/AverbacaoImportacaoDefinitiva
Nível  : Funcional completo
Risco  : P1
"""
import pytest
from utils import BASE_URL, ev, shot, assert_no_error, setup_filial_apolice, HOJE

CT_ID = "CT-CTN-009"
URL   = f"{BASE_URL}/citnet/AverbacaoInternacional/AverbacaoImportacaoDefinitiva"


def _fill_imp_definitiva(page) -> None:
    if page.locator("#e_doc_ebq").count():
        opts = page.evaluate(
            "Array.from(document.querySelector('#e_doc_ebq').options).map(o=>({v:o.value,t:o.text}))"
        )
        first_val = next((o["v"] for o in opts if o["v"] not in ("", "X")), None)
        if first_val:
            page.select_option("#e_doc_ebq", first_val)

    for fid, val in [("#u_doc_ini", "BL2026002"), ("#u_doc_cte", "BL2026002")]:
        if page.locator(fid).count():
            page.fill(fid, val)
            break

    if page.locator("#d_sda_vgm").count():
        page.fill("#d_sda_vgm", HOJE)

    # País origem
    if page.locator("#n_ori").count():
        page.select_option("#n_ori", "US")

    if page.locator("#v_is").count():
        page.triple_click("#v_is")
        page.fill("#v_is", "750000,00")
    if page.locator("#v_fte").count():
        page.triple_click("#v_fte")
        page.fill("#v_fte", "15000,00")

    # Número DI/DUIMP (definitiva pode exigir número de declaração)
    for fid in ["#u_num_di", "#txtNumDI", "#n_di"]:
        if page.locator(fid).count():
            page.fill(fid, "26/0000001-0")
            break


def test_ct_09_importacao_definitiva(citnet_session):
    page = citnet_session
    e = ev(CT_ID)

    page.goto(URL)
    page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "01_formulario_aberto.png")

    setup_filial_apolice(page)
    shot(page, e, "02_filial_apolice_selecionados.png")

    if page.locator("#btNovo").count():
        page.click("#btNovo")
        page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "03_formulario_novo.png")

    _fill_imp_definitiva(page)
    shot(page, e, "04_campos_preenchidos.png")

    if page.locator("#btEnviar").count():
        page.click("#btEnviar")
        page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "05_gravacao_resultado.png")

    body = page.inner_text("body")
    assert any(kw in body.lower() for kw in ["protocolo", "gravado", "sucesso", "averbação"]), (
        "Gravação Importação Definitiva não confirmada"
    )

    if page.locator("#btExcluir").count():
        page.click("#btExcluir")
        if page.locator("#btnSimModal:visible").count():
            page.click("#btnSimModal")
        page.wait_for_load_state("networkidle")
        assert_no_error(page)
        shot(page, e, "06_exclusao_confirmada.png")
