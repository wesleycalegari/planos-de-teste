"""
CT-CTN-004 — Averbação RCTF-C Nacional
Módulo : Averbações > Nacional > RCTF-C
Nível  : IGNORADO — funcionalidade não disponível no menu NSTECH
Risco  : N/A
"""
import pytest


@pytest.mark.skip(reason="RCTF-C Nacional não está disponível no menu CITNET NSTECH HML")
def test_ct_04_rctf_c_nacional(citnet_session):
    pass
