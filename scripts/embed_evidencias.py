"""
Embebe screenshots (evidências) em base64 diretamente no plano HTML RCTRC.
Executa após run_tests_rctrc_v2.py.
"""
import base64, re
from pathlib import Path

SCREENSHOTS = Path("c:/projetos/planos-de-teste/scripts/screenshots_rctrc/tests")
HTML_PATH   = Path("c:/projetos/planos-de-teste/docs/rctrc/index.html")

# Mapa: número do CT → lista de (label, arquivo)
EVIDENCIAS = {
    "001": [("Formulário carregado", "ct001.png")],
    "002": [("Subgrupo carregado (apólice 10)", "ct002.png")],
    "003": [("Tipo CTE — campo #u_cnh_elt visível", "ct003.png")],
    "004": [("Tipo Outros — campos série/número visíveis", "ct004.png")],
    "005": [("Formulário preenchido", "ct005_form.png"),
            ("Resposta gravação OK + protocolo", "ct005_resultado.png")],
    "010": [("OCD + ICA marcados simultaneamente", "ct010_marcados.png"),
            ("JS bloqueou (sem AJAX)", "ct010_js_block.png")],
    "014": [("IS zerado no formulário", "ct014_vs_zero.png"),
            ("JS bloqueou (sem AJAX)", "ct014_js_block.png")],
    "016": [("Data anterior preenchida", "ct016_form.png"),
            ("Server bloqueou — mensagem de erro", "ct016_resultado.png")],
    "017": [("Município origem em branco", "ct017_form.png"),
            ("Server bloqueou — mensagem de erro", "ct017_resultado.png")],
    "019": [("Formulário Rodo-Fluvial sem transbordo", "ct019_form.png"),
            ("Server bloqueou — transbordo obrigatório", "ct019_resultado.png")],
    "020": [("Formulário Rodo-Fluvial SP=F", "ct020_form.png"),
            ("Server bloqueou — percurso inválido", "ct020_resultado.png")],
    "023": [("Formulário sem subgrupo selecionado", "ct023_form.png"),
            ("JS bloqueou — sem AJAX disparado", "ct023_resultado.png")],
    "027": [("btImprimir habilitado após gravação", "ct027_resultado.png")],
}

CSS_INJECT = """
    .ct-evidencias { margin-top: 12px; grid-column: 1 / -1; }
    .ct-evidencias label { display: block; font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 6px; }
    .ct-evidencias .ev-grid { display: flex; flex-wrap: wrap; gap: 10px; }
    .ct-evidencias .ev-item { flex: 1; min-width: 280px; max-width: 520px; }
    .ct-evidencias .ev-item span { display: block; font-size: 11px; color: #64748b; margin-bottom: 3px; font-style: italic; }
    .ct-evidencias img { width: 100%; border: 1px solid #e2e8f0; border-radius: 4px; display: block; }
"""

def img_b64(path: Path) -> str:
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/png;base64,{data}"

def build_evidencias_html(ct_num: str) -> str:
    ev = EVIDENCIAS.get(ct_num)
    if not ev:
        return ""
    items = []
    for label, fname in ev:
        fpath = SCREENSHOTS / fname
        if not fpath.exists():
            continue
        src = img_b64(fpath)
        items.append(
            f'          <div class="ev-item"><span>{label}</span>'
            f'<img src="{src}" alt="{label}"></div>'
        )
    if not items:
        return ""
    inner = "\n".join(items)
    return (
        '\n          <div class="ct-evidencias ct-field full">'
        '\n            <label>Evidências</label>'
        '\n            <div class="ev-grid">'
        f'\n{inner}'
        '\n            </div>'
        '\n          </div>'
    )

def inject_evidencias(html: str) -> str:
    def replacer(m):
        ct_id_block = m.group(1)          # conteúdo do ct-card-header
        body_content = m.group(2)         # conteúdo do ct-body sem fechar

        # Extrai número do CT do ct-id span
        num_match = re.search(r'CT-RCT-(\d+)', ct_id_block)
        if not num_match:
            return m.group(0)
        ct_num = num_match.group(1)

        ev_html = build_evidencias_html(ct_num)
        if not ev_html:
            return m.group(0)

        # Remove evidências já injetadas antes (idempotente)
        body_clean = re.sub(
            r'\s*<div class="ct-evidencias ct-field full">.*?</div>\s*</div>\s*</div>',
            '',
            body_content,
            flags=re.DOTALL
        )

        return (
            f'<div class="ct-card-header">{ct_id_block}</div>\n'
            f'          <div class="ct-body">{body_clean}'
            f'{ev_html}\n          </div>\n        </div>'
        )

    pattern = re.compile(
        r'<div class="ct-card-header">(.*?)</div>\s*'
        r'<div class="ct-body">(.*?)</div>\s*</div>',
        re.DOTALL
    )
    return pattern.sub(replacer, html)

def inject_css(html: str) -> str:
    marker = ".ct-evidencias"
    if marker in html:
        # Já tem — remove e reinjecta para garantir versão atualizada
        html = re.sub(
            r'/\* ct-evidencias start \*/.*?/\* ct-evidencias end \*/',
            '',
            html,
            flags=re.DOTALL
        )
    insert_before = "  </style>"
    return html.replace(
        insert_before,
        f"    /* ct-evidencias start */{CSS_INJECT}    /* ct-evidencias end */\n{insert_before}"
    )

def main():
    html = HTML_PATH.read_text(encoding="utf-8")
    html = inject_css(html)
    html = inject_evidencias(html)
    HTML_PATH.write_text(html, encoding="utf-8")

    cts_com_ev = list(EVIDENCIAS.keys())
    total_imgs = sum(
        1 for evs in EVIDENCIAS.values()
        for _, f in evs
        if (SCREENSHOTS / f).exists()
    )
    print(f"OK — {total_imgs} imagens embutidas em {len(cts_com_ev)} CTs")
    print(f"Plano atualizado: {HTML_PATH}")

if __name__ == "__main__":
    main()
