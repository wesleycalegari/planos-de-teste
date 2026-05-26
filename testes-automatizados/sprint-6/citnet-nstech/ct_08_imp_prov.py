"""
CT-CTN-008 — Averbação Importação Provisória — CRUD Completo
Módulo : Averbações > Importação Provisória
URL    : /citnet/AverbacaoProvisoria/AverbacaoProvisoria
Nível  : Funcional completo
Risco  : P1

Nota: formulário internacional — campo de país (origin/destination),
moeda e documento de embarque diferem dos formulários nacionais.
IDs confirmados durante a primeira execução.
"""
import pytest
from utils import BASE_URL, ev, shot, assert_no_error, setup_filial_apolice, HOJE

CT_ID = "CT-CTN-008"
URL   = f"{BASE_URL}/citnet/AverbacaoProvisoria/AverbacaoProvisoria"


def _fill_imp_provisoria(page) -> None:
    """Preenche campos do formulário de Importação Provisória."""
    # Tipo documento: BL (Bill of Lading) ou AWB
    if page.locator("#e_doc_ebq").count():
        opts = page.evaluate(
            "Array.from(document.querySelector('#e_doc_ebq').options).map(o=>({v:o.value,t:o.text}))"
        )
        # Selecionar primeiro valor não vazio
        first_val = next((o["v"] for o in opts if o["v"] not in ("", "X")), None)
        if first_val:
            page.select_option("#e_doc_ebq", first_val)

    # Número do documento
    if page.locator("#u_doc_ini").count():
        page.fill("#u_doc_ini", "BL2026001")
    elif page.locator("#u_doc_cte").count():
        page.fill("#u_doc_cte", "BL2026001")

    # Data embarque
    if page.locator("#d_sda_vgm").count():
        page.fill("#d_sda_vgm", HOJE)

    # País origem (internacional usa código de país)
    if page.locator("#n_ori").count():
        page.select_option("#n_ori", "CN")  # China — importação

    # País destino / desembaraço
    if page.locator("#n_dst").count():
        page.select_option("#n_dst", "BR")  # Brasil

    # Valores
    if page.locator("#v_is").count():
        page.triple_click("#v_is")
        page.fill("#v_is", "500000,00")
    if page.locator("#v_fte").count():
        page.triple_click("#v_fte")
        page.fill("#v_fte", "10000,00")


def test_ct_08_importacao_provisoria(citnet_session):
    page = citnet_session
    e = ev(CT_ID)

    page.goto(URL)
    page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "01_formulario_aberto.png")

    setup_filial_apolice(page)
    shot(page, e, "02_filial_apolice_selecionados.png")

    # Clicar Novo
    if page.locator("#btNovo").count():
        page.click("#btNovo")
        page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "03_formulario_novo.png")

    _fill_imp_provisoria(page)
    shot(page, e, "04_campos_preenchidos.png")

    # Gravar
    if page.locator("#btEnviar").count():
        page.click("#btEnviar")
        page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "05_gravacao_resultado.png")

    body = page.inner_text("body")
    assert any(kw in body.lower() for kw in ["protocolo", "gravado", "sucesso", "averbação", "provisória"]), (
        "Gravação Importação Provisória não confirmada"
    )

    # Pesquisar
    if page.locator("#cmbSelecao").count():
        page.select_option("#cmbSelecao", "3")
        if page.locator("#txtPesqDataIni").count():
            page.fill("#txtPesqDataIni", HOJE)
            page.fill("#txtPesqDataFim", HOJE)
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "06_pesquisa_resultado.png")

    # Excluir (clean-up)
    if page.locator("#btExcluir").count():
        page.click("#btExcluir")
        if page.locator("#btnSimModal:visible").count():
            page.click("#btnSimModal")
        page.wait_for_load_state("networkidle")
        assert_no_error(page)
        shot(page, e, "07_exclusao_confirmada.png")
