"""
CT-CTN-027 — Aprovação de Fatura
Módulo : Faturamento > Aprovação de Fatura
Risco  : P2

SKIP: funcionalidade não disponível no menu CITNET NSTECH HML.
O menu Faturamento contém apenas: Status/Consulta, Histórico Nacional,
Histórico Internacional e Aprovação de Prévias (tipo=N).
Não há submenu "Aprovação de Fatura" para o tenant NSTECH.
"""
import pytest


@pytest.mark.skip(reason="Aprovação de Fatura não disponível no menu CITNET NSTECH HML")
def test_ct_27_aprovacao_fatura(citnet_session):
    pass
