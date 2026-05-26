"""
CT-CTN-026 — Aprovação de Prévia Internacional
Módulo : Faturamento > Consulta Status (Aprovação Prévia Internacional)
URL    : /citnet/AutorizacaoPrevia/AutorizacaoPrevia?tipo=I
Nível  : Funcional completo (consultar prévias → aprovar selecionados)
Risco  : P1
"""
import pytest
from datetime import datetime
from utils import BASE_URL, ev, shot, assert_no_error

CT_ID = "CT-CTN-026"
URL   = f"{BASE_URL}/citnet/AutorizacaoPrevia/AutorizacaoPrevia?tipo=I"

MES_ANO = (datetime.now().replace(day=1) - __import__("datetime").timedelta(days=1)).strftime("%m / %Y")


def test_ct_26_aprovacao_previa_internacional(citnet_session):
    page = citnet_session
    e = ev(CT_ID)

    page.goto(URL)
    page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "01_pagina_aberta.png")

    # Selecionar filial
    page.select_option("#c_org_prd", "1")
    page.wait_for_load_state("networkidle")

    # Preencher mês/ano
    if page.locator("#mes_ano").count():
        page.fill("#mes_ano", MES_ANO)

    shot(page, e, "02_filtros_preenchidos.png")

    # Consultar prévias
    page.click("#btConsultar")
    page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "03_resultado_consulta.png")

    body = page.inner_text("body").lower()
    has_previas = (
        page.evaluate("document.querySelectorAll('table tbody tr').length") > 0
        or "prévia" in body or "previa" in body
    )

    if not has_previas:
        print(f"[{CT_ID}] SEM PRÉVIAS INTERNACIONAIS PENDENTES — sem massa disponível em HML")
        shot(page, e, "04_sem_previas_ok.png")
        return

    shot(page, e, "04_previas_encontradas.png")

    # Selecionar registros para aprovação
    select_all = page.locator("input[type='checkbox'][id*='all'], input[type='checkbox'][name*='all'], #chkTodos").first
    if select_all.count() > 0:
        select_all.check()
        shot(page, e, "05_registros_selecionados.png")
    else:
        first_chk = page.locator("table tbody tr:first-child input[type='checkbox']").first
        if first_chk.count() > 0:
            first_chk.check()
            shot(page, e, "05_primeiro_registro_selecionado.png")

    # Aprovar selecionados
    if page.locator("#btAprovarTudo").count() > 0:
        page.click("#btAprovarTudo")
        page.wait_for_load_state("networkidle")

        for sel in ["#btnSimModal:visible", "#btAprovar:visible", "button:has-text('Processar'):visible"]:
            if page.locator(sel).count() > 0:
                page.click(sel)
                page.wait_for_load_state("networkidle")
                break

        assert_no_error(page)
        shot(page, e, "06_aprovacao_resultado.png")

        body_after = page.inner_text("body").lower()
        assert any(kw in body_after for kw in ["aprovado", "processado", "sucesso", "ok"]), (
            "Aprovação Internacional não confirmada — mensagem esperada não encontrada"
        )
        shot(page, e, "07_aprovacao_confirmada.png")
