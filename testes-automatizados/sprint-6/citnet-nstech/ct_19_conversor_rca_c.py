"""
CT-CTN-019 — Conversor RCA-C (Ramo 56)
Módulo : Conversor > Conversor de Arquivos
Ramo   : 56;CIT-AVB-RCA
"""
import pytest
from pathlib import Path
from utils import BASE_URL, ev, shot, assert_no_error

CT_ID    = "CT-CTN-019"
URL      = f"{BASE_URL}/citnet/Conversor/Conversor"
RAMO_VAL = "56;CIT-AVB-RCA"
TEST_FILE = Path("c:/projetos/planos-de-teste/scripts/arquivos-teste/rca_c_teste.txt")


def test_ct_19_conversor_rca_c(citnet_session):
    page = citnet_session
    e = ev(CT_ID)

    page.goto(URL)
    page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "01_conversor_aberto.png")

    ramos = page.evaluate(
        "Array.from(document.querySelector('#c_rmo').options).map(o => o.value)"
    )
    assert RAMO_VAL in ramos, f"Ramo RCA-C ({RAMO_VAL}) não encontrado"

    page.select_option("#c_org_prd", "1")
    page.wait_for_load_state("networkidle")
    page.select_option("#c_rmo", RAMO_VAL)
    page.wait_for_load_state("networkidle")

    segurado_val = page.evaluate(
        "Array.from(document.querySelector('#c_idt_pes').options)"
        ".find(o => o.value && o.value !== '0')?.value || ''"
    )
    if segurado_val:
        page.select_option("#c_idt_pes", segurado_val)

    shot(page, e, "02_ramo_selecionado.png")

    if TEST_FILE.exists():
        page.set_input_files("#arq", str(TEST_FILE))
        if page.locator("#btImportar").count():
            page.click("#btImportar")
            page.wait_for_load_state("networkidle")
            assert_no_error(page)
            shot(page, e, "03_importacao_resultado.png")
        if page.locator("#btConverter").count():
            page.click("#btConverter")
            page.wait_for_load_state("networkidle")
            assert_no_error(page)
            shot(page, e, "04_conversao_resultado.png")
    else:
        print(f"[{CT_ID}] Sem arquivo de teste — validando UI apenas")
        shot(page, e, "03_ui_verificada.png")

    assert_no_error(page)
