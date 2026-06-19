#!/usr/bin/env python3
"""Corrige docs/index.html: conserta entradas corrompidas e adiciona sprint-7."""

import re
from pathlib import Path

INDEX = Path(r"c:\projetos\planos-de-teste\docs\index.html")

# Entradas corretas para substituir as corrompidas (titulo estava com HTML inline)
CORRECOES = {
    "bug-6842": {
        "titulo": "[CITWEB] Erro no cálculo do prêmio RCV — DM/DC",
        "sistema": "CITWEB / CITNET (DB compartilhado)",
        "modulo": "Ramo 59 — RCV — DM/DC / prêmio",
        "status": "pendente",
        "data_execucao": "13/05/2026",
        "cts_aprovados": 0, "cts_reprovados": 0, "cts_pendentes": 4,
    },
    "pbi-6838": {
        "titulo": "RCV — Condição Comercial: Taxa Única",
        "sistema": "CITWEB",
        "modulo": "Cadastro de Apólice — Condição Comercial RCV",
        "status": "parcial",
        "data_execucao": "19/05/2026",
        "cts_aprovados": 4, "cts_reprovados": 0, "cts_pendentes": 1,
    },
    "pbi-6870": {
        "titulo": "Integração API de KM — Ramo RCV (59)",
        "sistema": "CITWEB / CITNET",
        "modulo": "Condição Comercial VKMCML — API de KM",
        "status": "aprovado",
        "data_execucao": "26/05/2026",
        "cts_aprovados": 3, "cts_reprovados": 0, "cts_pendentes": 0,
    },
    "bug-7086": {
        "titulo": "[CITWEB] Flag Ativo/Inativo de Usuário — FAIRFAX",
        "sistema": "CITWEB",
        "modulo": "Segurança — Cadastro de Usuário",
        "status": "pendente",
        "data_execucao": "28/05/2026",
        "cts_aprovados": 0, "cts_reprovados": 0, "cts_pendentes": 5,
    },
    "pbi-6841": {
        "titulo": "[CITWEB] Ajustar exibição de módulos e ramo RCV Conversor",
        "sistema": "CITWEB",
        "modulo": "Conversor de Arquivos — RCV",
        "status": "aprovado",
        "data_execucao": "26/05/2026",
        "cts_aprovados": 5, "cts_reprovados": 0, "cts_pendentes": 0,
    },
}

# Entradas faltando para Sprint 7
NOVAS = [
    {
        "id": "pbi-6773",
        "sprint": "Sprint 7 Citweb",
        "sprint_slug": "sprint-7-citweb",
        "titulo": "[CITWEB] Data de inclusão de prévia — Ação PRÉVIA LIBERADA PARA O CORRETOR",
        "sistema": "CITWEB",
        "modulo": "Nacional — Fechamento Mensal — Prévia",
        "status": "pendente",
        "data_execucao": "27/05/2026",
        "url": "sprint-7-citweb/pbi-6773/",
        "cts_aprovados": 0, "cts_reprovados": 0, "cts_pendentes": 7,
    },
    {
        "id": "pbi-6888",
        "sprint": "Sprint 7 Citweb",
        "sprint_slug": "sprint-7-citweb",
        "titulo": "[RCV] [MITSUI] Interface Nsconnect Faturamento",
        "sistema": "CITWEB",
        "modulo": "Faturamento RCV — Interface Nsconnect",
        "status": "pendente",
        "data_execucao": "27/05/2026",
        "url": "sprint-7-citweb/pbi-6888/",
        "cts_aprovados": 0, "cts_reprovados": 0, "cts_pendentes": 4,
    },
    {
        "id": "pbi-7137",
        "sprint": "Sprint 7 Citweb",
        "sprint_slug": "sprint-7-citweb",
        "titulo": "[CITWEB] Relação de Embarques Simplificada RCV",
        "sistema": "CITWEB",
        "modulo": "Nacional — Fechamento Mensal — Prévia / Emissão / Impressão",
        "status": "aprovado",
        "data_execucao": "02/06/2026",
        "url": "sprint-7-citweb/pbi-7137/",
        "cts_aprovados": 4, "cts_reprovados": 0, "cts_pendentes": 0,
    },
    {
        "id": "bug-7179",
        "sprint": "Sprint 7 Citweb",
        "sprint_slug": "sprint-7-citweb",
        "titulo": "[CITWEB] Conversor rejeita CNPJ alfanumérico — Starr + AXA",
        "sistema": "CITWEB",
        "modulo": "Conversor de Arquivos — CNPJ Alfanumérico",
        "status": "parcial",
        "data_execucao": "01/06/2026",
        "url": "sprint-7-citweb/bug-7179/",
        "cts_aprovados": 2, "cts_reprovados": 2, "cts_pendentes": 0,
    },
]


def make_entry(d):
    return (
        f'  {{\n'
        f'    "id": "{d["id"]}",\n'
        f'    "sprint": "{d["sprint"]}",\n'
        f'    "sprint_slug": "{d["sprint_slug"]}",\n'
        f'    "titulo": "{d["titulo"]}",\n'
        f'    "sistema": "{d["sistema"]}",\n'
        f'    "modulo": "{d["modulo"]}",\n'
        f'    "status": "{d["status"]}",\n'
        f'    "data_execucao": "{d["data_execucao"]}",\n'
        f'    "url": "{d["url"]}",\n'
        f'    "cts_aprovados": {d["cts_aprovados"]},\n'
        f'    "cts_reprovados": {d["cts_reprovados"]},\n'
        f'    "cts_pendentes": {d["cts_pendentes"]}\n'
        f'  }}'
    )


def fix_entry(html, entry_id, corrections):
    """Replace a PLANOS entry (identified by "id": "entry_id") with corrected data."""
    # Find the entry start
    pattern = rf'\{{\s*\n\s*"id":\s*"{re.escape(entry_id)}".*?\}}'
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        print(f"  AVISO: entrada {entry_id} não encontrada")
        return html

    # Extract sprint/sprint_slug/url from existing entry
    existing = match.group(0)
    sprint_m = re.search(r'"sprint":\s*"([^"]+)"', existing)
    slug_m   = re.search(r'"sprint_slug":\s*"([^"]+)"', existing)
    url_m    = re.search(r'"url":\s*"([^"]+)"', existing)

    d = dict(corrections)
    d["id"] = entry_id
    d["sprint"] = sprint_m.group(1) if sprint_m else ""
    d["sprint_slug"] = slug_m.group(1) if slug_m else ""
    d["url"] = url_m.group(1) if url_m else f"{entry_id}/"

    new_entry = make_entry(d)
    result = html[:match.start()] + new_entry + html[match.end():]
    print(f"  Corrigido: {entry_id}")
    return result


def add_sprint7_entries(html, novas):
    """Insert new entries before the closing ]; of the PLANOS array."""
    # Find the PLANOS array start, then its closing ];
    planos_start = html.find('const PLANOS = [')
    if planos_start == -1:
        print("  ERRO: não encontrou const PLANOS")
        return html
    close_pos = html.find('];', planos_start)
    if close_pos == -1:
        print("  ERRO: não encontrou fechamento do array PLANOS")
        return html

    # Check which IDs already exist
    existing_ids = set(re.findall(r'"id":\s*"([^"]+)"', html))
    to_add = [d for d in novas if d["id"] not in existing_ids]

    if not to_add:
        print("  Todas as entradas Sprint 7 já existem")
        return html

    inserts = ",\n".join(make_entry(d) for d in to_add)
    # Find last } before ]; and insert after it
    last_entry_end = html.rfind('}', 0, close_pos)
    result = html[:last_entry_end+1] + ",\n" + inserts + "\n" + html[last_entry_end+1:]
    for d in to_add:
        print(f"  Adicionado: {d['id']}")
    return result


def run():
    html = INDEX.read_text(encoding="utf-8")

    print("Corrigindo entradas corrompidas...")
    for entry_id, corrections in CORRECOES.items():
        html = fix_entry(html, entry_id, corrections)

    print("Adicionando entradas Sprint 7 faltantes...")
    html = add_sprint7_entries(html, NOVAS)

    INDEX.write_text(html, encoding="utf-8")
    print(f"\nSalvo: {INDEX}")


if __name__ == "__main__":
    run()
