#!/usr/bin/env python3
"""Corrige o index.html: move as 4 entradas Sprint-7 para dentro do array PLANOS."""

import re, json
from pathlib import Path

INDEX = Path(r"c:\projetos\planos-de-teste\docs\index.html")
html = INDEX.read_text(encoding="utf-8")

# 1. Extrair o array PLANOS atual
m = re.search(r'(const PLANOS = )(\[.*?\])(;)', html, re.DOTALL)
if not m:
    print("ERRO: array PLANOS não encontrado"); exit(1)

pre, arr_str, post = m.group(1), m.group(2), m.group(3)
data = json.loads(arr_str)
print(f"Entradas atuais: {len(data)}")

# 2. Remover as 4 entradas mal-posicionadas que estão fora (duplicadas no HTML)
existing_ids = {d["id"] for d in data}
ids_fora = ["pbi-6773", "pbi-6888", "pbi-7137", "bug-7179"]

for eid in ids_fora:
    # Remove raw entry block that was inserted outside the array
    pattern = rf',\n  \{{\n    "id": "{re.escape(eid)}".*?\n  \}}'
    html_new = re.sub(pattern, '', html, flags=re.DOTALL)
    if html_new != html:
        print(f"  Removido bloco solto: {eid}")
        html = html_new

# 3. Re-extrair o array limpo (agora sem as duplicatas externas)
m = re.search(r'(const PLANOS = )(\[.*?\])(;)', html, re.DOTALL)
pre, arr_str, post = m.group(1), m.group(2), m.group(3)
data = json.loads(arr_str)

# 4. Adicionar as entradas corretas ao array
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

current_ids = {d["id"] for d in data}
added = 0
for entry in NOVAS:
    if entry["id"] not in current_ids:
        data.append(entry)
        print(f"  Adicionado: {entry['id']}")
        added += 1

# 5. Serializar o array de volta com indentação limpa
def entry_to_str(d):
    lines = ["  {"]
    for k, v in d.items():
        if isinstance(v, str):
            lines.append(f'    "{k}": "{v}",')
        else:
            lines.append(f'    "{k}": {v},')
    # Remove trailing comma from last field
    lines[-1] = lines[-1].rstrip(',')
    lines.append("  }")
    return "\n".join(lines)

new_arr = "[\n" + ",\n".join(entry_to_str(d) for d in data) + "\n]"

# 6. Reconstruir o HTML
new_html = html[:m.start()] + pre + new_arr + post + html[m.end():]
INDEX.write_text(new_html, encoding="utf-8")

# 7. Verificar
m2 = re.search(r'const PLANOS = (\[.*?\]);', new_html, re.DOTALL)
data2 = json.loads(m2.group(1))
by_sprint = {}
for d in data2:
    by_sprint.setdefault(d["sprint"], []).append(d["id"])
print(f"\nResultado final ({len(data2)} planos):")
for sprint, ids in sorted(by_sprint.items()):
    print(f"  {sprint}: {ids}")
print("\nJSON valido")
