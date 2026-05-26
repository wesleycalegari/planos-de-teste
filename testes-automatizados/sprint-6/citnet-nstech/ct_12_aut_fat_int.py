"""
CT-CTN-012 — Autorização de Faturamento Internacional
Módulo : Averbações > Internacional > Aut. de Faturamento
URL    : /citnet/AutorizacaoFaturamento/AutorizacaoFaturamento?tipo=I
Nível  : Funcional completo
Risco  : P1
"""
import pytest
from utils import BASE_URL, ev, shot, assert_no_error, setup_filial_apolice

CT_ID = "CT-CTN-012"
URL   = f"{BASE_URL}/citnet/AutorizacaoFaturamento/AutorizacaoFaturamento?tipo=I"


def test_ct_12_aut_faturamento_internacional(citnet_session):
    page = citnet_session
    e = ev(CT_ID)

    page.goto(URL)
    page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "01_pagina_carregada.png")

    setup_filial_apolice(page)
    shot(page, e, "02_filial_apolice_selecionados.png")

    page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "03_grade_registros.png")

    body = page.inner_text("body").lower()
    has_records = (
        page.evaluate("document.querySelectorAll('table tbody tr').length") > 0
        or "protocolo" in body
        or "autorizar" in body
    )

    if not has_records:
        print(f"[{CT_ID}] SEM REGISTROS PENDENTES — estado normal ou sem massa HML")
        shot(page, e, "04_sem_pendentes_ok.png")
        return

    primeiro_btn = page.locator(
        "input[type='checkbox'], a:has-text('Autorizar'), button:has-text('Autorizar')"
    ).first
    if primeiro_btn.count() > 0:
        primeiro_btn.check() if primeiro_btn.get_attribute("type") == "checkbox" else primeiro_btn.click()
        page.wait_for_load_state("networkidle")
        shot(page, e, "04_registro_selecionado.png")

        btn_autorizar = page.locator(
            "button:has-text('Autorizar'), input[value='Autorizar']"
        ).first
        if btn_autorizar.count() > 0:
            btn_autorizar.click()
            page.wait_for_load_state("networkidle")
            assert_no_error(page)
            shot(page, e, "05_autorizacao_confirmada.png")

    assert_no_error(page)
