"""
CT-CTN-017 — Conversor RCTR-C (Ramo 54)
Módulo : Conversor > Conversor de Arquivos
URL    : /citnet/Conversor/Conversor
Nível  : Funcional completo
Risco  : P2

Campos documentados (25/05/2026):
  #c_org_prd — filial
  #c_rmo      — ramo (valor: "54;CIT-AVB-RCT" para RCTR-C)
  #c_idt_pes  — segurado
  #cmbLayout  — layout (carrega após ramo)
  #arq        — file upload
  Botões: #btImportar, #btConverter, #btProcessar
"""
import pytest
from pathlib import Path
from utils import BASE_URL, ev, shot, assert_no_error

CT_ID    = "CT-CTN-017"
URL      = f"{BASE_URL}/citnet/Conversor/Conversor"
RAMO_VAL = "54;CIT-AVB-RCT"
TEST_FILE = Path("c:/projetos/planos-de-teste/scripts/arquivos-teste/rctr_c_teste.txt")


def _setup_conversor(page, ramo_val: str, filial: str = "1"):
    """Seleciona filial, ramo e primeiro segurado disponível."""
    page.select_option("#c_org_prd", filial)
    page.wait_for_load_state("networkidle")
    page.select_option("#c_rmo", ramo_val)
    page.wait_for_load_state("networkidle")

    # Selecionar segurado se disponível
    segurado_val = page.evaluate(
        "Array.from(document.querySelector('#c_idt_pes').options)"
        ".find(o => o.value && o.value !== '0')?.value || ''"
    )
    if segurado_val:
        page.select_option("#c_idt_pes", segurado_val)


def test_ct_17_conversor_rctr_c(citnet_session):
    page = citnet_session
    e = ev(CT_ID)

    page.goto(URL)
    page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "01_conversor_aberto.png")

    # Verificar opções do select de ramo
    ramos = page.evaluate(
        "Array.from(document.querySelector('#c_rmo').options).map(o => o.value)"
    )
    assert RAMO_VAL in ramos, f"Ramo RCTR-C ({RAMO_VAL}) não encontrado nas opções do conversor"

    # Configurar filial + ramo + segurado
    _setup_conversor(page, RAMO_VAL)
    shot(page, e, "02_ramo_selecionado.png")

    # Verificar que o campo de arquivo está presente
    assert page.locator("#arq").count() > 0, "Campo de upload (#arq) não encontrado"

    # Clicar Novo para criar novo layout
    if page.locator("#btNovo").count():
        page.click("#btNovo")
        page.wait_for_load_state("networkidle")
        shot(page, e, "03_novo_layout.png")

    # Importar arquivo de teste se existir
    if TEST_FILE.exists():
        page.set_input_files("#arq", str(TEST_FILE))
        shot(page, e, "04_arquivo_selecionado.png")

        if page.locator("#btImportar").count():
            page.click("#btImportar")
            page.wait_for_load_state("networkidle")
            assert_no_error(page)
            shot(page, e, "05_importacao_resultado.png")

        # Converter
        if page.locator("#btConverter").count():
            page.click("#btConverter")
            page.wait_for_load_state("networkidle")
            assert_no_error(page)
            shot(page, e, "06_conversao_resultado.png")

        # Processar
        if page.locator("#btProcessar").count():
            page.click("#btProcessar")
            page.wait_for_load_state("networkidle")
            assert_no_error(page)
            shot(page, e, "07_processamento_resultado.png")
    else:
        # Sem arquivo de teste: verificar apenas UI
        print(f"[{CT_ID}] Arquivo de teste não encontrado em {TEST_FILE} — validando UI apenas")
        shot(page, e, "04_ui_verificada_sem_arquivo.png")

    assert_no_error(page)
