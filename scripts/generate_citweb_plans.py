"""Gerador de HTML para planos de teste CITWEB AXA."""
# -*- coding: utf-8 -*-

import json
import os
from pathlib import Path
from datetime import datetime

BASE = Path(r"c:\projetos\planos-de-teste\docs\citweb-axa")
DATA = BASE / "data"
TOOL_RESULTS = Path(r"C:\Users\wesley.moreira\.claude\projects\c--projetos-satelites-citweb\8fbca690-0347-49a8-8bff-68ac4f90ef47\tool-results")

MODULES = [
    {
        "slug": "cadas",
        "name": "Cadastros Gerais",
        "file": DATA / "cadas.json",
        "tool_result": TOOL_RESULTS / "mcp-voidr-test_plans_list_suites-1778284045177.txt",
    },
    {
        "slug": "rcv",
        "name": "RCV Ramo 59",
        "file": DATA / "rcv.json",
        "tool_result": TOOL_RESULTS / "mcp-voidr-test_plans_list_suites-1778284046219.txt",
    },
    {"slug": "opera", "name": "Operações Administrativas", "file": DATA / "opera.json"},
    {"slug": "rcdcn", "name": "RC-DC (Nacional)", "file": DATA / "rcdcn.json"},
    {"slug": "cnpja", "name": "CNPJ Alfanumérico", "file": DATA / "cnpja.json"},
    {"slug": "rcacn", "name": "RCA-C (Nacional)", "file": DATA / "rcacn.json"},
    {"slug": "rctrc", "name": "RCTR-C (Nacional)", "file": DATA / "rctrc.json"},
    {"slug": "rctfc", "name": "RCTF-C (Nacional)", "file": DATA / "rctfc.json"},
    {"slug": "rctac", "name": "RCTA-C (Nacional)", "file": DATA / "rctac.json"},
    {"slug": "trans", "name": "Transporte Nacional", "file": DATA / "trans.json"},
    {"slug": "impor", "name": "Importação (Internacional)", "file": DATA / "impor.json"},
    {"slug": "expor", "name": "Exportação (Internacional)", "file": DATA / "expor.json"},
    {"slug": "rctrv", "name": "RCTR-VI (Internacional)", "file": DATA / "rctrv.json"},
]


def load_suites(module):
    # Try standard data file first
    if module["file"].exists():
        with open(module["file"], encoding="utf-8") as f:
            return json.load(f)
    # Fall back to tool-result file
    if "tool_result" in module and module["tool_result"].exists():
        with open(module["tool_result"], encoding="utf-8") as f:
            raw = json.load(f)
        return json.loads(raw[0]["text"])
    raise FileNotFoundError(f"No data found for module {module['slug']}")


TAG_COLORS = {
    "LIVE": ("#107c10", "#dff6dd"),
    "PENDING": ("#ca5010", "#fce9d9"),
    "DEV": ("#0078d4", "#deecf9"),
    "FIX": ("#d13438", "#fde7e9"),
    "QUARANTINE": ("#605e5c", "#edebe9"),
}

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', sans-serif; font-size: 13px; background: #f3f2f1; color: #323130; }
.header { background: #0078d4; color: white; padding: 16px 24px; }
.header h1 { font-size: 20px; font-weight: 600; }
.header p { font-size: 12px; opacity: 0.85; margin-top: 4px; }
.container { max-width: 1100px; margin: 0 auto; padding: 20px 16px; }
.stats { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.stat-card { background: white; border: 1px solid #edebe9; border-radius: 4px; padding: 12px 16px; min-width: 120px; }
.stat-card .num { font-size: 24px; font-weight: 700; color: #0078d4; }
.stat-card .lbl { font-size: 11px; color: #605e5c; margin-top: 2px; }
.suite-header {
  background: #0078d4; color: white;
  padding: 10px 16px; border-radius: 4px 4px 0 0;
  margin-top: 20px; cursor: pointer;
  display: flex; align-items: center; justify-content: space-between;
}
.suite-header:first-of-type { margin-top: 0; }
.suite-header .suite-title { font-weight: 600; font-size: 14px; }
.suite-header .suite-count { font-size: 12px; opacity: 0.85; }
.suite-body { border: 1px solid #0078d4; border-top: none; border-radius: 0 0 4px 4px; overflow: hidden; }
.suite-body.collapsed { display: none; }
.ct-card { background: white; border-bottom: 1px solid #edebe9; padding: 12px 16px; }
.ct-card:last-child { border-bottom: none; }
.ct-header { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 8px; cursor: pointer; }
.ct-id { font-weight: 700; color: #0078d4; white-space: nowrap; font-size: 12px; }
.ct-name { font-weight: 600; flex: 1; }
.badges { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.badge { border-radius: 3px; padding: 2px 8px; font-size: 11px; font-weight: 600; white-space: nowrap; }
.ct-body { display: none; margin-top: 10px; }
.ct-body.open { display: block; }
.ct-section { margin-bottom: 10px; }
.ct-section-title { font-size: 11px; font-weight: 700; text-transform: uppercase; color: #605e5c; margin-bottom: 4px; letter-spacing: 0.5px; }
.ct-section ol, .ct-section ul { padding-left: 18px; }
.ct-section li { margin-bottom: 3px; line-height: 1.4; }
.ct-section .arrange-list { list-style-type: disc; }
.ct-section .act-list { list-style-type: decimal; }
.ct-section .assert-list { list-style-type: disc; color: #107c10; }
.back-link { display: inline-block; margin-bottom: 16px; color: #0078d4; text-decoration: none; font-size: 12px; }
.back-link:hover { text-decoration: underline; }
"""

JS = """
function toggleSuite(el) {
  const body = el.nextElementSibling;
  body.classList.toggle('collapsed');
  el.querySelector('.toggle-icon').textContent = body.classList.contains('collapsed') ? '▶' : '▼';
}
function toggleCase(header) {
  const body = header.nextElementSibling;
  body.classList.toggle('open');
}
"""


def tag_badge(tag):
    fg, bg = TAG_COLORS.get(tag, ("#605e5c", "#edebe9"))
    return f'<span class="badge" style="color:{fg};background:{bg};border:1px solid {fg}">{tag}</span>'


def auto_badge(is_auto):
    if is_auto:
        return '<span class="badge" style="color:#107c10;background:#dff6dd;border:1px solid #107c10">AUTO</span>'
    return '<span class="badge" style="color:#605e5c;background:#edebe9;border:1px solid #605e5c">MANUAL</span>'


def render_case(case):
    cid = case.get("slug", "")
    name = case.get("name", "")
    tag = case.get("current_tag", "PENDING")
    is_auto = case.get("isAutomated", False)
    arrange = case.get("arrange", [])
    act = case.get("act", [])
    assert_ = case.get("assert", [])

    arrange_html = "".join(f"<li>{a}</li>" for a in arrange)
    act_html = "".join(f"<li>{a}</li>" for a in act)
    assert_html = "".join(f"<li>{a}</li>" for a in assert_)

    return f"""
<div class="ct-card">
  <div class="ct-header" onclick="toggleCase(this)">
    <span class="ct-id">{cid}</span>
    <span class="ct-name">{name}</span>
    <div class="badges">
      {tag_badge(tag)}
      {auto_badge(is_auto)}
    </div>
  </div>
  <div class="ct-body">
    <div class="ct-section">
      <div class="ct-section-title">Pré-condições (Arrange)</div>
      <ul class="arrange-list">{arrange_html}</ul>
    </div>
    <div class="ct-section">
      <div class="ct-section-title">Passos de Execução (Act)</div>
      <ol class="act-list">{act_html}</ol>
    </div>
    <div class="ct-section">
      <div class="ct-section-title">Resultado Esperado (Assert)</div>
      <ul class="assert-list">{assert_html}</ul>
    </div>
  </div>
</div>"""


def render_suite(suite):
    cases = suite.get("cases", [])
    suite_name = suite.get("name", suite.get("slug", ""))
    slug = suite.get("slug", "")
    cases_html = "".join(render_case(c) for c in cases)
    count = len(cases)
    return f"""
<div class="suite-header" onclick="toggleSuite(this)">
  <span class="suite-title">{suite_name} <span style="opacity:0.7;font-weight:400;font-size:12px">({slug})</span></span>
  <span class="suite-count">{count} caso(s) <span class="toggle-icon">▼</span></span>
</div>
<div class="suite-body">
  {cases_html}
</div>"""


def render_module_html(module_name, suites, slug):
    total_cases = sum(len(s.get("cases", [])) for s in suites)
    total_suites = len(suites)
    live = sum(1 for s in suites for c in s.get("cases", []) if c.get("current_tag") == "LIVE")
    pending = sum(1 for s in suites for c in s.get("cases", []) if c.get("current_tag") == "PENDING")
    automated = sum(1 for s in suites for c in s.get("cases", []) if c.get("isAutomated"))
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    suites_html = "".join(render_suite(s) for s in suites)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Plano de Teste — {module_name}</title>
<style>{CSS}</style>
</head>
<body>
<div class="header">
  <h1>Plano de Teste — {module_name}</h1>
  <p>CITWEB AXA &nbsp;|&nbsp; Gerado em {now}</p>
</div>
<div class="container">
  <a class="back-link" href="index.html">← Voltar ao índice</a>
  <div class="stats">
    <div class="stat-card"><div class="num">{total_cases}</div><div class="lbl">Total de casos</div></div>
    <div class="stat-card"><div class="num">{total_suites}</div><div class="lbl">Suítes</div></div>
    <div class="stat-card"><div class="num" style="color:#107c10">{live}</div><div class="lbl">LIVE</div></div>
    <div class="stat-card"><div class="num" style="color:#ca5010">{pending}</div><div class="lbl">PENDING</div></div>
    <div class="stat-card"><div class="num">{automated}</div><div class="lbl">Automatizados</div></div>
  </div>
  {suites_html}
</div>
<script>{JS}</script>
</body>
</html>"""


def render_index(modules_data):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    total_all = sum(m["total"] for m in modules_data)
    cards_html = ""
    for m in modules_data:
        cards_html += f"""
<a class="module-card" href="{m['slug']}.html">
  <div class="module-name">{m['name']}</div>
  <div class="module-stats">
    <span>{m['total']} casos</span>
    <span style="color:#107c10">{m['live']} LIVE</span>
    <span style="color:#ca5010">{m['pending']} PENDING</span>
  </div>
  <div class="module-suites">{m['suites']} suítes</div>
</a>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Planos de Teste — CITWEB AXA</title>
<style>
{CSS}
.index-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; margin-top: 8px; }}
.module-card {{
  background: white; border: 1px solid #edebe9; border-radius: 4px;
  padding: 16px; text-decoration: none; color: #323130;
  transition: box-shadow 0.15s, border-color 0.15s;
  display: block;
}}
.module-card:hover {{ box-shadow: 0 2px 8px rgba(0,0,0,0.12); border-color: #0078d4; }}
.module-name {{ font-weight: 600; font-size: 14px; margin-bottom: 8px; color: #0078d4; }}
.module-stats {{ font-size: 12px; display: flex; gap: 10px; margin-bottom: 4px; }}
.module-suites {{ font-size: 11px; color: #605e5c; }}
</style>
</head>
<body>
<div class="header">
  <h1>Planos de Teste — CITWEB AXA</h1>
  <p>{len(modules_data)} módulos &nbsp;|&nbsp; {total_all} casos no total &nbsp;|&nbsp; Gerado em {now}</p>
</div>
<div class="container">
  <div class="index-grid">
    {cards_html}
  </div>
</div>
</body>
</html>"""


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)

    modules_data = []

    for module in MODULES:
        print(f"Processando: {module['name']}...", end=" ")
        try:
            suites = load_suites(module)
        except FileNotFoundError as e:
            print(f"ERRO: {e}")
            continue

        total = sum(len(s.get("cases", [])) for s in suites)
        live = sum(1 for s in suites for c in s.get("cases", []) if c.get("current_tag") == "LIVE")
        pending = sum(1 for s in suites for c in s.get("cases", []) if c.get("current_tag") == "PENDING")
        n_suites = len(suites)

        html = render_module_html(module["name"], suites, module["slug"])
        out = BASE / f"{module['slug']}.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)

        modules_data.append({
            "slug": module["slug"],
            "name": module["name"],
            "total": total,
            "live": live,
            "pending": pending,
            "suites": n_suites,
        })
        print(f"OK - {total} casos, {n_suites} suites -> {module['slug']}.html")

    # Generate index
    index_html = render_index(modules_data)
    with open(BASE / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"\nindex.html gerado com {len(modules_data)} módulos.")
    print(f"Output: {BASE}")


if __name__ == "__main__":
    main()
