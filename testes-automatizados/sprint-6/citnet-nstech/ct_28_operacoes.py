"""
CT-CTN-028 — Operações
Módulo : Operações (não mapeado no CITNET NSTECH)
Risco  : P3

SKIP: funcionalidade não disponível no menu CITNET NSTECH HML.
O menu CITNET NSTECH é composto por: Averbações, Relatórios, Conversor,
Faturamento e INTERNO (Alterar Senha). Não há menu "Operações".
"""
import pytest


@pytest.mark.skip(reason="Operações não disponível no menu CITNET NSTECH HML")
def test_ct_28_operacoes(citnet_session):
    pass
