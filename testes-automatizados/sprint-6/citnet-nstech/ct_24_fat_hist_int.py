"""
CT-CTN-024 — Histórico de Faturamento Internacional
Módulo : Faturamento > Histórico de Faturamento > Internacional
URL    : /citnet/Faturamento/ConsultaHistorico?tipo=I
Nível  : Funcional completo
Risco  : P2
"""
import pytest
from datetime import datetime
from utils import BASE_URL, ev, shot, assert_no_error

CT_ID = "CT-CTN-024"
URL   = f"{BASE_URL}/citnet/Faturamento/ConsultaHistorico?tipo=I"

MES_ANO = (datetime.now().replace(day=1) - __import__("datetime").timedelta(days=1)).strftime("%m / %Y")


def test_ct_24_fat_historico_internacional(citnet_session):
    page = citnet_session
    e = ev(CT_ID)

    page.goto(URL)
    page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "01_pagina_aberta.png")

    if page.locator("#c_org_prd").count():
        page.select_option("#c_org_prd", "1")
        page.wait_for_load_state("networkidle")

    if page.locator("#mes_ano").count():
        page.fill("#mes_ano", MES_ANO)

    shot(page, e, "02_filtros_preenchidos.png")

    for sel in ["#btConsultar", "#btPesquisar", "button:has-text('Consultar')"]:
        if page.locator(sel).count():
            page.click(sel)
            page.wait_for_load_state("networkidle")
            break
    else:
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")

    assert_no_error(page)
    shot(page, e, "03_resultado_consulta.png")

    body = page.inner_text("body").lower()
    has_data = page.evaluate("document.querySelectorAll('table tbody tr').length") > 0
    no_data_ok = any(kw in body for kw in ["nenhum", "sem registro", "não encontrado"])
    assert has_data or no_data_ok, "Resultado inesperado no histórico de faturamento internacional"

    if has_data:
        shot(page, e, "04_historico_encontrado.png")
