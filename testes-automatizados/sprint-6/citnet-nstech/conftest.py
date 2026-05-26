"""
Suite de automação — CITNET NSTECH — Sprint 6
Seguradora: NSTECH (core)
Sistema: CITNET v2
Ambiente: HML — https://nstech-hml-faturamento.nsseg.com.br/citnet/

Execução:
  pytest testes-automatizados/sprint-6/citnet-nstech/ -v
  pytest ct_02_rctr_c_nac.py -v   # CT individual

Notas:
  - Em Windows local usar Playwright MCP (não playwright local — timeout)
  - Sessão CITNET via handoff JWT a partir do CITWEB
"""
import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, BrowserContext

# ──────────────────────────────────────────────
# Constantes
# ──────────────────────────────────────────────
BASE_URL       = "https://nstech-hml-faturamento.nsseg.com.br"
CITWEB_USER    = "FRED"
CITWEB_PASS    = "T7JJM6XF"
FILIAL_MATRIZ  = "1"
FILIAL_TESTE   = "999"   # FILIAL TESTE AUTO 0447

EVIDENCE_BASE = Path(
    "c:/projetos/planos-de-teste/docs/sprint-6-citweb/citnet-nstech/evidencias"
)

# ──────────────────────────────────────────────
# Helpers de sessão
# ──────────────────────────────────────────────

def _login_citweb(page: Page) -> None:
    """Login no CITWEB NSTECH (permanece na mesma aba)."""
    page.goto(f"{BASE_URL}/login/")
    page.wait_for_load_state("networkidle")
    # Se já está logado, /login/ redireciona para /Login/Menu
    if "/Menu" in page.url:
        return
    page.fill("#nomeUsuario", CITWEB_USER)
    page.fill("#senhaUsuario", CITWEB_PASS)
    page.click("#btnAcessar")
    page.wait_for_load_state("networkidle")
    assert "/Menu" in page.url or "/Login" in page.url, (
        f"Login CITWEB falhou — URL atual: {page.url}"
    )


def _open_citnet(citweb_page: Page, context: BrowserContext) -> Page:
    """Abre CITNET clicando no botão do menu CITWEB (abre nova aba com JWT)."""
    with context.expect_page() as citnet_info:
        citweb_page.click("button:has-text('CITNET')")
    citnet = citnet_info.value
    citnet.wait_for_load_state("networkidle")
    assert "citnet" in citnet.url.lower(), (
        f"CITNET não abriu — URL: {citnet.url}"
    )
    return citnet


# ──────────────────────────────────────────────
# Fixtures pytest
# ──────────────────────────────────────────────

@pytest.fixture(scope="session")
def _pw():
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def citnet_session(_pw):
    """
    Sessão CITNET compartilhada para toda a suíte.
    scope=session: o browser abre uma vez e navega entre CTs por URL.
    """
    browser = _pw.chromium.launch(headless=False, slow_mo=150)
    context = browser.new_context(viewport={"width": 1280, "height": 800})

    citweb = context.new_page()
    _login_citweb(citweb)
    citnet = _open_citnet(citweb, context)

    yield citnet

    browser.close()


# ──────────────────────────────────────────────
# Utilitário de evidências (importável diretamente)
# ──────────────────────────────────────────────

def ev(ct_id: str) -> Path:
    """Retorna Path para a pasta de evidências do CT, criando se necessário."""
    path = EVIDENCE_BASE / ct_id
    path.mkdir(parents=True, exist_ok=True)
    return path
