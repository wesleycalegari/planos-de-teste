"""
Mapeia: apólices disponíveis no HML AXA (tipos, RCF, DDR),
padrão Select2, menu de navegação, seletor e_tr2,
e condições de espera AJAX.
"""
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

BASE  = "https://axa-hml-faturamento.nsseg.com.br/citnet"
USER  = "interno"
PASS  = "11"
OUT   = Path("c:/projetos/planos-de-teste/scripts/screenshots_rctrc")
OUT.mkdir(exist_ok=True)
R     = {}   # resultado consolidado

async def main():
    async with async_playwright() as pw:
        br   = await pw.chromium.launch(headless=False, slow_mo=200)
        ctx  = await br.new_context(viewport={"width": 1366, "height": 768})
        page = await ctx.new_page()
        page.set_default_timeout(30000)

        # ── LOGIN ─────────────────────────────────────────────────────────
        await page.goto(f"{BASE}/")
        await page.fill("#usuario", USER)
        await page.fill("#senha", PASS)
        await page.click("#btLogin1")
        await page.wait_for_load_state("networkidle")
        print("Login OK →", page.url)

        # ── CAPTURAR MENU COMPLETO ────────────────────────────────────────
        menu = await page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a[href]'));
                return links
                    .filter(a => a.href.includes('/citnet/'))
                    .map(a => ({text: a.textContent.trim(), href: a.href}))
                    .filter(a => a.text.length > 0);
            }
        """)
        R["menu_links"] = menu
        print(f"\nLinks de menu capturados: {len(menu)}")
        for m in menu:
            print(f"  {m['text'][:40]:<40} → {m['href']}")

        # ── NAVEGAR PARA RCTRC ────────────────────────────────────────────
        await page.goto(f"{BASE}/AverbacaoNacional/AverbacaoRCTRC")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=str(OUT/"map_01_form_inicial.png"))

        # ── INSPECIONAR SELECT2 DO CAMPO APÓLICE ─────────────────────────
        select2_info = await page.evaluate("""
            () => {
                const sel = document.querySelector('#u_apo_pnc');
                if (!sel) return {error: 'not found'};
                const container = sel.closest('.select2-container') ||
                                  document.querySelector('.select2-container');
                const s2 = sel.nextSibling;
                return {
                    id: sel.id,
                    tag: sel.tagName,
                    classes: sel.className,
                    parent_html: sel.parentElement?.className,
                    is_select2: !!document.querySelector('.select2-container'),
                    select2_container_selector: document.querySelector('.select2-container') ?
                        '.select2-container' : null,
                    options_count: sel.options?.length || 0,
                    first_options: sel.options ? Array.from(sel.options).slice(0,5)
                        .map(o => ({v: o.value, t: o.text.trim().substring(0,60)})) : []
                };
            }
        """)
        R["select2_info"] = select2_info
        print(f"\nSelect2 info: {json.dumps(select2_info, ensure_ascii=False, indent=2)}")

        # ── VERIFICAR COMO ABRIR SELECT2 ─────────────────────────────────
        select2_dom = await page.evaluate("""
            () => {
                // Tentar identificar o container Select2 associado ao campo apólice
                const field = document.querySelector('#u_apo_pnc');
                if (!field) return {};
                // Select2 normalmente cria um span.select2 após o select
                const next = field.nextElementSibling;
                const parent = field.parentElement;
                return {
                    next_sibling_tag: next?.tagName,
                    next_sibling_class: next?.className,
                    parent_class: parent?.className,
                    parent_id: parent?.id,
                    // Buscar span de trigger do Select2
                    triggers: Array.from(document.querySelectorAll('.select2-selection, .select2-choice, .select2-container'))
                        .map(el => ({
                            tag: el.tagName,
                            class: el.className.substring(0,80),
                            id: el.id,
                            aria_owns: el.getAttribute('aria-owns') || ''
                        })).slice(0,5)
                };
            }
        """)
        R["select2_dom"] = select2_dom
        print(f"\nSelect2 DOM: {json.dumps(select2_dom, ensure_ascii=False, indent=2)}")

        # ── TENTAR ABRIR SELECT2 E LISTAR OPÇÕES ─────────────────────────
        try:
            # Clicar no container Select2 para abrir o dropdown
            s2_trigger = await page.query_selector(
                "#s2id_u_apo_pnc, .select2-container, span.select2, " +
                "#u_apo_pnc + span, .select2-choice"
            )
            if s2_trigger:
                await s2_trigger.click()
                await page.wait_for_timeout(1000)
                await page.screenshot(path=str(OUT/"map_02_select2_open.png"))
                # Capturar opções abertas
                opts = await page.evaluate("""
                    () => {
                        const items = document.querySelectorAll(
                            '.select2-results li, .select2-results__option, ul.select2-results li'
                        );
                        return Array.from(items).slice(0,30).map(i => ({
                            text: i.textContent.trim().substring(0,80),
                            id: i.getAttribute('data-option-array-index') ||
                                i.getAttribute('id') || ''
                        }));
                    }
                """)
                R["apolice_options_visible"] = opts
                print(f"\nOpções Select2 abertas: {json.dumps(opts, ensure_ascii=False, indent=2)}")
                # Fechar pressionando Escape
                await page.keyboard.press("Escape")
            else:
                print("\nSelect2 trigger não encontrado pelo seletor genérico")
        except Exception as e:
            print(f"\nErro ao tentar abrir Select2: {e}")

        # ── LISTAR TODAS AS OPTIONS DO SELECT NATIVO ─────────────────────
        all_opts = await page.evaluate("""
            () => {
                const sel = document.querySelector('#u_apo_pnc');
                if (!sel) return [];
                return Array.from(sel.options).map(o => ({
                    value: o.value,
                    text: o.text.trim()
                }));
            }
        """)
        R["apolice_all_options"] = all_opts
        print(f"\nTodas as opções #u_apo_pnc ({len(all_opts)}):")
        for o in all_opts:
            print(f"  [{o['value']}] {o['text']}")

        # ── SELECIONAR PRIMEIRA APÓLICE DISPONÍVEL ────────────────────────
        valid_opts = [o for o in all_opts if o['value'] not in ('', '0', 'Selecione')]
        if valid_opts:
            first = valid_opts[0]
            print(f"\nSelecionando primeira apólice: {first}")
            # Tentar via JS direto (mais confiável que Select2 click)
            await page.evaluate(f"""
                () => {{
                    const sel = document.querySelector('#u_apo_pnc');
                    sel.value = '{first['value']}';
                    sel.dispatchEvent(new Event('change', {{bubbles: true}}));
                }}
            """)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(1500)
            await page.screenshot(path=str(OUT/"map_03_apolice_selecionada.png"))

            # ── CAPTURAR SUBGRUPOS ────────────────────────────────────────
            sgps = await page.evaluate("""
                () => {
                    const sel = document.querySelector('#u_sgp');
                    if (!sel) return [];
                    return Array.from(sel.options).map(o => ({v: o.value, t: o.text.trim()}));
                }
            """)
            R["subgrupos_apolice_1"] = sgps
            print(f"\nSubgrupos apólice {first['value']}: {sgps}")

            # ── CAPTURAR CAMPOS QUE FICARAM VISÍVEIS ─────────────────────
            campos_visiveis = await page.evaluate("""
                () => {
                    const ids = ['#e_doc_ebq', '#hdTipoApolice', '#hdCircular337',
                                 '#u_cnh_elt', '#c_rmo_rfc', '#hdCte',
                                 '#permitirPercursoOrigem', '#permitirPercursoDestino',
                                 '#permitirEstipulacaoDDR', '#btEnviar'];
                    return ids.map(id => {
                        const el = document.querySelector(id);
                        if (!el) return {id, found: false};
                        return {
                            id,
                            found: true,
                            visible: el.offsetParent !== null,
                            disabled: el.disabled,
                            value: el.value || ''
                        };
                    });
                }
            """)
            R["campos_pos_apolice"] = campos_visiveis
            print(f"\nCampos após apólice selecionada:")
            for c in campos_visiveis:
                print(f"  {c}")

            # ── INSPECIONAR TIPO DA APÓLICE ───────────────────────────────
            tipo_info = await page.evaluate("""
                () => ({
                    hdTipoApolice: document.querySelector('#hdTipoApolice')?.value,
                    c_rmo_rfc: document.querySelector('#c_rmo_rfc')?.value,
                    hdCte: document.querySelector('#hdCte')?.value,
                    permitirEstipulacaoDDR: document.querySelector('#permitirEstipulacaoDDR')?.value,
                    btEnviar_disabled: document.querySelector('#btEnviar')?.disabled
                })
            """)
            R["tipo_apolice_1"] = tipo_info
            print(f"\nTipo da apólice 1: {tipo_info}")

            # ── BUSCAR SELETOR e_tr2 ──────────────────────────────────────
            e_tr2_info = await page.evaluate("""
                () => {
                    // Buscar por diferentes padrões
                    const candidates = [
                        document.querySelector('#e_tr2'),
                        document.querySelector('[name="e_tr2"]'),
                        document.querySelector('input[value="F"]'),
                        ...Array.from(document.querySelectorAll('input[type="checkbox"], input[type="radio"]'))
                            .filter(el => el.name.includes('tr') || el.id.includes('tr') ||
                                         el.id.includes('flu') || el.name.includes('flu'))
                    ];
                    // Buscar também por texto próximo
                    const fluviais = Array.from(document.querySelectorAll('label, span'))
                        .filter(el => /fluvial|transbordo|rodo.fluvial/i.test(el.textContent));
                    return {
                        e_tr2_by_id: !!document.querySelector('#e_tr2'),
                        e_tr2_by_name: !!document.querySelector('[name="e_tr2"]'),
                        candidates: candidates.filter(Boolean).map(el => ({
                            tag: el.tagName, id: el.id, name: el.name,
                            type: el.type, value: el.value,
                            visible: el.offsetParent !== null
                        })),
                        fluvial_labels: fluviais.map(el => ({
                            tag: el.tagName,
                            text: el.textContent.trim().substring(0,60),
                            for: el.htmlFor || '',
                            parent_html: el.parentElement?.innerHTML?.substring(0,150)
                        })).slice(0,5)
                    };
                }
            """)
            R["e_tr2_info"] = e_tr2_info
            print(f"\ne_tr2 info: {json.dumps(e_tr2_info, ensure_ascii=False, indent=2)}")

            # ── INSPECIONAR TODA A SEÇÃO DE PERCURSO ─────────────────────
            percurso_html = await page.evaluate("""
                () => {
                    // Buscar section/div que contenha transbordo ou fluvial
                    const all = Array.from(document.querySelectorAll('div, section, fieldset'));
                    const relevant = all.filter(el =>
                        /fluvial|transbordo|e_tr2|e_tr1/i.test(el.innerHTML) &&
                        el.children.length > 0 && el.innerHTML.length < 3000
                    );
                    return relevant.slice(0, 3).map(el => ({
                        tag: el.tagName,
                        id: el.id,
                        class: el.className.substring(0,50),
                        html: el.innerHTML.substring(0, 800)
                    }));
                }
            """)
            R["percurso_section"] = percurso_html
            print(f"\nSeção de percurso HTML:")
            for s in percurso_html:
                print(f"  [{s['id']}] {s['html'][:300]}")

        # ── ITERAR TODAS AS APÓLICES PARA CLASSIFICAR TIPOS ──────────────
        print(f"\n{'='*60}")
        print("Classificando todas as apólices disponíveis...")
        tipos_encontrados = {}
        for opt in valid_opts[:20]:   # máx 20 para não demorar demais
            await page.evaluate(f"""
                () => {{
                    const sel = document.querySelector('#u_apo_pnc');
                    sel.value = '{opt['value']}';
                    sel.dispatchEvent(new Event('change', {{bubbles: true}}));
                }}
            """)
            await page.wait_for_timeout(1200)
            info = await page.evaluate("""
                () => ({
                    hdTipoApolice: document.querySelector('#hdTipoApolice')?.value || '',
                    c_rmo_rfc: document.querySelector('#c_rmo_rfc')?.value || '0',
                    permitirEstipulacaoDDR: document.querySelector('#permitirEstipulacaoDDR')?.value || '',
                    btEnviar_disabled: document.querySelector('#btEnviar')?.disabled
                })
            """)
            tipos_encontrados[opt['value']] = {
                "texto": opt['text'],
                "tipo": info['hdTipoApolice'],
                "tem_rcf": info['c_rmo_rfc'] != '0',
                "ddr": info['permitirEstipulacaoDDR'],
                "btn_habilitado": not info['btEnviar_disabled']
            }
            print(f"  {opt['value'][:20]:<20} tipo={info['hdTipoApolice']:<3} "
                  f"rcf={info['c_rmo_rfc']:<5} ddr={info['permitirEstipulacaoDDR']:<3} "
                  f"btn={'OK' if not info['btEnviar_disabled'] else 'DIS'}"
                  f"  | {opt['text'][:40]}")

        R["apolices_classificadas"] = tipos_encontrados

        # Salvar JSON completo
        out_json = OUT / "map_result.json"
        out_json.write_text(json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON salvo: {out_json}")
        await br.close()

asyncio.run(main())
