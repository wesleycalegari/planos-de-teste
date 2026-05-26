"""
CT-CTN-022 — Consulta Status de Faturamento Nacional
Módulo : Faturamento > Status de Faturamento
URL    : /citnet/Faturamento/ConsultaStatus?tipo=N
Nível  : Funcional completo (filtrar → consultar → verificar resultado)
Risco  : P1

Campos documentados (25/05/2026):
  #c_org_prd  — filial
  #c_rmo      — ramo
  #u_apo_pnc  — apólice (formato {id};{ramo};{tipo})
  #u_sgp      — subgrupo
  #mes_ano    — mês/ano (texto "MM / YYYY")
  #btConsultar — botão consultar
  #btNovo      — iniciar novo fechamento
"""
import pytest
from datetime import datetime
from utils import BASE_URL, ev, shot, assert_no_error

CT_ID = "CT-CTN-022"
URL   = f"{BASE_URL}/citnet/Faturamento/ConsultaStatus?tipo=N"

MES_ANO = (datetime.now().replace(day=1) - __import__("datetime").timedelta(days=1)).strftime("%m / %Y")


def test_ct_22_fat_status_nacional(citnet_session):
    page = citnet_session
    e = ev(CT_ID)

    page.goto(URL)
    page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "01_pagina_aberta.png")

    # Selecionar filial MATRIZ
    page.select_option("#c_org_prd", "1")
    page.wait_for_load_state("networkidle")
    shot(page, e, "02_filial_selecionada.png")

    # Preencher mês/ano (mês anterior — faturas são do mês fechado)
    if page.locator("#mes_ano").count():
        page.fill("#mes_ano", MES_ANO)

    # Selecionar apólice (opcional — deixar "Todos" para ver todas)
    # Não filtrar por apólice para maximizar chance de encontrar registros

    shot(page, e, "03_filtros_preenchidos.png")

    # Consultar
    page.click("#btConsultar")
    page.wait_for_load_state("networkidle")
    assert_no_error(page)
    shot(page, e, "04_resultado_consulta.png")

    body = page.inner_text("body").lower()
    has_data = page.evaluate("document.querySelectorAll('table tbody tr').length") > 0
    no_data_ok = any(
        kw in body for kw in ["nenhum", "sem registro", "não encontrado", "0 registro"]
    )
    assert has_data or no_data_ok, "Resultado inesperado — nem dados nem mensagem de 'sem registros'"

    if has_data:
        shot(page, e, "05_registros_encontrados.png")
        # Tentar abrir o primeiro registro para ver detalhes
        link = page.locator("table tbody tr:first-child a, table tbody tr:first-child td[onclick]").first
        if link.count() > 0:
            link.click()
            page.wait_for_load_state("networkidle")
            assert_no_error(page)
            shot(page, e, "06_detalhe_faturamento.png")
    else:
        print(f"[{CT_ID}] Sem registros de faturamento para o período — estado normal HML")
