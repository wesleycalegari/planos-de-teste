"""
Utilitários compartilhados — suite CITNET NSTECH Sprint 6.
Importar em cada CT: from utils import *
"""
from datetime import datetime
from pathlib import Path
from playwright.sync_api import Page

BASE_URL = "https://nstech-hml-faturamento.nsseg.com.br"
FILIAL_MATRIZ = "1"
HOJE = datetime.now().strftime("%d/%m/%Y")

# ──────────────────────────────────────────────
# Evidências
# ──────────────────────────────────────────────
EVIDENCE_BASE = Path(
    "c:/projetos/planos-de-teste/docs/sprint-6-citweb/citnet-nstech/evidencias"
)


def ev(ct_id: str) -> Path:
    path = EVIDENCE_BASE / ct_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def shot(page: Page, ev_path: Path, nome: str) -> None:
    """Screenshot com scroll ao topo antes de capturar."""
    page.evaluate("window.scrollTo(0, 0)")
    page.screenshot(path=str(ev_path / nome))


# ──────────────────────────────────────────────
# Verificação de erro
# ──────────────────────────────────────────────
ERROR_PATTERNS = [
    "ocorreu um erro",
    "erro inesperado",
    "exception",
    "internal server error",
    "server error",
]


def assert_no_error(page: Page) -> None:
    """Falha o CT se a página exibe mensagem de erro visível ao usuário."""
    text = page.inner_text("body").lower()
    for pat in ERROR_PATTERNS:
        assert pat not in text, (
            f"Erro detectado na tela: '{pat}'\n"
            f"URL: {page.url}"
        )


def page_has_error(page: Page) -> bool:
    text = page.inner_text("body").lower()
    return any(p in text for p in ERROR_PATTERNS)


# ──────────────────────────────────────────────
# Seleção de filial + apólice (formulários de averbação)
# ──────────────────────────────────────────────

def select_filial(page: Page, filial: str = FILIAL_MATRIZ) -> None:
    page.select_option("#c_org_prd", filial)


def wait_and_select_apolice(page: Page, timeout: int = 15_000) -> str:
    """Aguarda as apólices carregarem e seleciona a primeira vigente."""
    page.wait_for_function(
        "document.querySelector('#u_apo_pnc') && "
        "document.querySelector('#u_apo_pnc').options.length > 1",
        timeout=timeout,
    )
    val = page.evaluate(
        "Array.from(document.querySelector('#u_apo_pnc').options)"
        ".find(o => o.value && o.value !== '0')?.value || ''"
    )
    assert val, "Nenhuma apólice disponível para a filial selecionada"
    page.select_option("#u_apo_pnc", val)
    return val


def wait_and_select_sgp(page: Page, timeout: int = 8_000) -> str:
    """Aguarda subgrupos carregarem e seleciona o primeiro."""
    try:
        page.wait_for_function(
            "document.querySelector('#u_sgp') && "
            "document.querySelector('#u_sgp').options.length > 1",
            timeout=timeout,
        )
        val = page.evaluate(
            "Array.from(document.querySelector('#u_sgp').options)"
            ".find(o => o.value && o.value !== '')?.value || ''"
        )
        if val:
            page.select_option("#u_sgp", val)
        return val
    except Exception:
        return ""


def setup_filial_apolice(page: Page, filial: str = FILIAL_MATRIZ) -> None:
    """Seleciona filial e primeira apólice disponível."""
    select_filial(page, filial)
    wait_and_select_apolice(page)
    wait_and_select_sgp(page)


# ──────────────────────────────────────────────
# Ações do formulário de averbação
# ──────────────────────────────────────────────

def click_novo(page: Page) -> None:
    page.click("#btNovo")
    page.wait_for_load_state("networkidle")


def click_gravar(page: Page) -> None:
    page.click("#btEnviar")
    page.wait_for_load_state("networkidle")


def click_excluir_confirmar(page: Page) -> None:
    """Clica em Excluir e confirma no modal de confirmação."""
    page.click("#btExcluir")
    page.wait_for_selector("#btnSimModal:visible", timeout=5_000)
    page.click("#btnSimModal")
    page.wait_for_load_state("networkidle")


def click_imprimir(page: Page) -> None:
    page.click("#btImprimir")
    page.wait_for_load_state("networkidle")


# ──────────────────────────────────────────────
# Pesquisa na grade de averbações
# ──────────────────────────────────────────────

def pesquisar_por_periodo(page: Page, data_ini: str = None, data_fim: str = None) -> None:
    data_ini = data_ini or HOJE
    data_fim = data_fim or HOJE
    page.select_option("#cmbSelecao", "3")  # PERÍODO
    page.fill("#txtPesqDataIni", data_ini)
    page.fill("#txtPesqDataFim", data_fim)
    page.keyboard.press("Enter")
    page.wait_for_load_state("networkidle")


def grid_row_count(page: Page) -> int:
    return page.evaluate(
        "document.querySelectorAll('table tbody tr').length || 0"
    )


# ──────────────────────────────────────────────
# Helpers para formulários de averbação nacional
# (campos comuns a RCTR-C, RCTA-C, RCA-C, RCV, Transporte)
# ──────────────────────────────────────────────

def fill_common_nacional(
    page: Page,
    doc_type: str = "C",       # C=CTE, N=NFE, O=Outros
    serie_cte: str = "001",
    num_cte: str = "999001",
    modal: str = "T",           # T=RODOVIÁRIO
    uf_ori: str = "SP",
    uf_dst: str = "RJ",
    data_saida: str = None,
    placa: str = "ABC1D234",
    valor_is: str = "100000,00",
    valor_frete: str = "5000,00",
) -> None:
    data_saida = data_saida or HOJE
    if page.locator("#e_doc_ebq").count():
        page.select_option("#e_doc_ebq", doc_type)
    if doc_type == "C":
        if page.locator("#u_ser_doc_cte").count():
            page.fill("#u_ser_doc_cte", serie_cte)
        if page.locator("#u_doc_cte").count():
            page.fill("#u_doc_cte", num_cte)
    else:
        if page.locator("#u_ser_doc").count():
            page.fill("#u_ser_doc", serie_cte)
        if page.locator("#u_doc_ini").count():
            page.fill("#u_doc_ini", num_cte)
    if page.locator("#e_tr1").count():
        page.select_option("#e_tr1", modal)
    if page.locator("#n_ori").count():
        page.select_option("#n_ori", uf_ori)
    if page.locator("#n_dst").count():
        page.select_option("#n_dst", uf_dst)
    if page.locator("#d_sda_vgm").count():
        page.fill("#d_sda_vgm", data_saida)
    if page.locator("#t_vei_tpr").count():
        page.fill("#t_vei_tpr", placa)
    if page.locator("#v_is").count():
        page.triple_click("#v_is")
        page.fill("#v_is", valor_is)
    if page.locator("#v_fte").count():
        page.triple_click("#v_fte")
        page.fill("#v_fte", valor_frete)
