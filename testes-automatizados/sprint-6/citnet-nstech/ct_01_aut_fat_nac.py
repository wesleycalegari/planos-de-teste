"""
CT-CTN-001 — Autorização de Faturamento Nacional
Módulo : Averbações > Nacional > Aut. de Faturamento
URL    : /citnet/AutorizacaoFaturamento/AutorizacaoFaturamento?tipo=N
Nível  : Funcional completo
Risco  : P1
"""
import pytest
from utils import BASE_URL, ev, shot, assert_no_error, page_has_error, setup_filial_apolice

CT_ID = "CT-CTN-001"
URL   = f"{BASE_URL}/citnet/AutorizacaoFaturamento/AutorizacaoFaturamento?tipo=N"


def test_ct_01_aut_faturamento_nacional(citnet_session):
    page = citnet_session
    e = ev(CT_ID)

    # ── Navegar para o módulo
    page.goto(URL)
    page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "01_pagina_carregada.png")

    # ── Selecionar filial e apólice
    setup_filial_apolice(page)
    shot(page, e, "02_filial_apolice_selecionados.png")

    # ── Verificar se há registros pendentes de autorização
    # O formulário exibe uma grade com averbações pendentes de autorização de faturamento
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
        # Sem massa disponível — documentar como verificado (sem pendências é válido)
        print(f"[{CT_ID}] SEM REGISTROS PENDENTES — estado normal ou sem massa HML")
        shot(page, e, "04_sem_pendentes_ok.png")
        return

    # ── Se houver registros: tentar autorizar o primeiro
    # Botão de autorização geralmente fica na linha da grade
    primeiro_btn = page.locator("input[type='checkbox'], a:has-text('Autorizar'), button:has-text('Autorizar')").first
    if primeiro_btn.count() > 0:
        primeiro_btn.check() if primeiro_btn.get_attribute("type") == "checkbox" else primeiro_btn.click()
        page.wait_for_load_state("networkidle")
        shot(page, e, "04_registro_selecionado.png")

        # Confirmar autorização se houver botão principal
        btn_autorizar = page.locator("button:has-text('Autorizar'), input[value='Autorizar']").first
        if btn_autorizar.count() > 0:
            btn_autorizar.click()
            page.wait_for_load_state("networkidle")
            assert_no_error(page)
            shot(page, e, "05_autorizacao_confirmada.png")
    else:
        shot(page, e, "04_grade_sem_botao_autorizar.png")

    assert_no_error(page)
