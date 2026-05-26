"""
CT-CTN-014 — Relatório Consulta de Fatura Nacional
Módulo : Relatórios > Nacional > Consulta de Fatura
URL    : /citnet/Relatorio/ConsultaFatura?tipo=N
Nível  : Funcional completo
Risco  : P2
"""
import pytest
from utils import BASE_URL, ev, shot, assert_no_error, HOJE
from datetime import datetime

CT_ID = "CT-CTN-014"
URL   = f"{BASE_URL}/citnet/Relatorio/ConsultaFatura?tipo=N"

# Mês/ano atual para filtro de fatura
MES_ATUAL = datetime.now().month - 1 or 12   # mês anterior (faturas são do mês fechado)
ANO_ATUAL = datetime.now().year


def test_ct_14_relatorio_fatura_nacional(citnet_session):
    page = citnet_session
    e = ev(CT_ID)

    page.goto(URL)
    page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "01_relatorio_aberto.png")

    # Selecionar filial
    if page.locator("#c_org_prd").count():
        page.select_option("#c_org_prd", "1")
        page.wait_for_load_state("networkidle")

    # Selecionar apólice
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

    # Selecionar mês/ano (relatório de fatura usa select de mês e ano)
    for fid in ["#cmbMes", "#mes", "#selectMes"]:
        if page.locator(fid).count():
            page.select_option(fid, str(MES_ATUAL - 1))   # select 0-based
            break

    for fid in ["#cmbAno", "#ano", "#selectAno"]:
        if page.locator(fid).count():
            page.select_option(fid, str(ANO_ATUAL))
            break

    shot(page, e, "02_filtros_preenchidos.png")

    for sel in [
        "button:has-text('Pesquisar')", "button:has-text('Consultar')",
        "button:has-text('Gerar')", "#btPesquisar", "#btConsultar",
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
    assert has_data or no_data_ok, "Resultado inesperado no relatório de fatura"

    if has_data:
        shot(page, e, "04_faturas_encontradas.png")
        # Tentar visualizar a fatura
        link = page.locator("table tbody tr:first-child a").first
        if link.count() > 0:
            link.click()
            page.wait_for_load_state("networkidle")
            assert_no_error(page)
            shot(page, e, "05_detalhe_fatura.png")
