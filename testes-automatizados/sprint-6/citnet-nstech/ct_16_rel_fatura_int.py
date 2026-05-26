"""
CT-CTN-016 — Relatório Consulta de Fatura Internacional
Módulo : Relatórios > Internacional > Consulta de Fatura
URL    : /citnet/Relatorio/ConsultaFatura?tipo=I
Nível  : Funcional completo
Risco  : P2
"""
import pytest
from utils import BASE_URL, ev, shot, assert_no_error
from datetime import datetime

CT_ID = "CT-CTN-016"
URL   = f"{BASE_URL}/citnet/Relatorio/ConsultaFatura?tipo=I"

MES_ATUAL = datetime.now().month - 1 or 12
ANO_ATUAL = datetime.now().year


def test_ct_16_relatorio_fatura_internacional(citnet_session):
    page = citnet_session
    e = ev(CT_ID)

    page.goto(URL)
    page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "01_relatorio_aberto.png")

    if page.locator("#c_org_prd").count():
        page.select_option("#c_org_prd", "1")
        page.wait_for_load_state("networkidle")

    if page.locator("#u_apo_pnc").count():
        try:
            page.wait_for_function(
                "document.querySelector('#u_apo_pnc').options.length > 1", timeout=8_000
            )
            val = page.evaluate(
                "Array.from(document.querySelector('#u_apo_pnc').options)"
                ".find(o => o.value && o.value !== '0')?.value || ''"
            )
            if val:
                page.select_option("#u_apo_pnc", val)
        except Exception:
            pass

    for fid in ["#cmbMes", "#mes", "#selectMes"]:
        if page.locator(fid).count():
            page.select_option(fid, str(MES_ATUAL - 1))
            break

    for fid in ["#cmbAno", "#ano", "#selectAno"]:
        if page.locator(fid).count():
            page.select_option(fid, str(ANO_ATUAL))
            break

    shot(page, e, "02_filtros_preenchidos.png")

    for sel in [
        "button:has-text('Pesquisar')", "button:has-text('Consultar')",
        "button:has-text('Gerar')", "#btPesquisar",
    ]:
        if page.locator(sel).count():
            page.click(sel)
            page.wait_for_load_state("networkidle")
            break
    else:
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")

    assert_no_error(page)
    shot(page, e, "03_resultado_pesquisa.png")

    body = page.inner_text("body").lower()
    has_data = page.evaluate("document.querySelectorAll('table tbody tr').length") > 0
    no_data_ok = any(kw in body for kw in ["nenhum", "sem registros", "não encontrado"])
    assert has_data or no_data_ok, "Resultado inesperado no relatório de fatura internacional"
