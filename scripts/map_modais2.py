"""
Mapeamento focado dos modais: município e mercadoria.
Captura: estrutura HTML, interação step-by-step, padrão onclick, códigos reais.
"""
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

BASE = "https://axa-hml-faturamento.nsseg.com.br/citnet"
OUT  = Path("c:/projetos/planos-de-teste/scripts/screenshots_rctrc")
OUT.mkdir(exist_ok=True)
R    = {}

async def main():
    async with async_playwright() as pw:
        br   = await pw.chromium.launch(headless=False, slow_mo=300)
        ctx  = await br.new_context(viewport={"width": 1366, "height": 900})
        page = await ctx.new_page()
        page.set_default_timeout(30000)

        await page.goto(f"{BASE}/")
        await page.fill("#usuario", "interno")
        await page.fill("#senha", "11")
        await page.click("#btLogin1")
        await page.wait_for_load_state("networkidle")

        await page.goto(f"{BASE}/AverbacaoNacional/AverbacaoRCTRC")
        await page.wait_for_load_state("networkidle")
        await page.select_option("#c_org_prd", "1")
        await page.wait_for_timeout(1500)
        await page.evaluate("""
            () => {
                const s = document.querySelector('#u_apo_pnc');
                s.value = '10'; s.dispatchEvent(new Event('change', {bubbles:true}));
            }
        """)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1500)
        await page.select_option("#u_sgp", "1")
        await page.wait_for_timeout(800)
        await page.select_option("#e_doc_ebq", "C")
        await page.wait_for_timeout(500)

        # ── MODAL DE MUNICÍPIO ────────────────────────────────────────────
        print("=== MODAL DE MUNICIPIO ===")
        await page.select_option("#n_ori", "SP")
        await page.wait_for_timeout(800)

        # Inspecionar antes de abrir
        pre = await page.evaluate("""
            () => ({
                bt_visible: document.querySelector('#bt_cdd_ori')?.offsetParent !== null,
                modal_classes: document.querySelector('#mdlMunicipio')?.className
            })
        """)
        print(f"Antes de abrir: {pre}")

        # Clicar no botão
        await page.click("#bt_cdd_ori")
        # Aguardar modal ter classe 'in' (Bootstrap modal aberto)
        await page.wait_for_selector("#mdlMunicipio.in, #mdlMunicipio[aria-hidden='false']", timeout=8000)
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(OUT/"mod2_01_mun_aberto.png"))

        modal_html = await page.evaluate("""
            () => {
                const m = document.querySelector('#mdlMunicipio');
                return {
                    classes: m.className,
                    aria_hidden: m.getAttribute('aria-hidden'),
                    full_html: m.innerHTML.substring(0, 2000)
                };
            }
        """)
        R["modal_mun_html"] = modal_html
        print(f"Modal classes: {modal_html['classes']}")
        print(f"Modal HTML preview: {modal_html['full_html'][:600]}")

        # Preencher nome e pesquisar (Enter OU botão)
        await page.fill("#txtNomeMunicipio", "SAO PAULO")
        await page.wait_for_timeout(300)

        # Verificar se há botão de pesquisa
        pesquisa_info = await page.evaluate("""
            () => {
                const m = document.querySelector('#mdlMunicipio');
                const btns = Array.from(m.querySelectorAll('button, input[type=button], input[type=submit], a.btn'));
                const forms = Array.from(m.querySelectorAll('form'));
                return {
                    buttons: btns.map(b=>({tag:b.tagName,id:b.id,type:b.type||'',
                                          text:b.textContent.trim().substring(0,30),
                                          onclick:(b.getAttribute('onclick')||'').substring(0,80)})),
                    form_actions: forms.map(f=>({id:f.id, action:f.action, method:f.method}))
                };
            }
        """)
        R["modal_mun_buttons"] = pesquisa_info
        print(f"Botoes no modal: {json.dumps(pesquisa_info, ensure_ascii=False)}")

        # Pressionar Enter para pesquisar
        await page.focus("#txtNomeMunicipio")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=str(OUT/"mod2_02_mun_resultado.png"))

        resultado_html = await page.evaluate("""
            () => {
                const m = document.querySelector('#mdlMunicipio');
                // Capturar toda a estrutura de resultados
                const rows = Array.from(m.querySelectorAll('tr'));
                const items_list = Array.from(m.querySelectorAll('li, .item'));
                const all_links = Array.from(m.querySelectorAll('a, [onclick]'))
                    .filter(el => el.textContent.trim().length > 0);
                return {
                    rows_count: rows.length,
                    rows: rows.slice(0,10).map(r=>({
                        text: r.textContent.trim().replace(/\s+/g,' ').substring(0,100),
                        tds: Array.from(r.querySelectorAll('td')).map(td=>td.textContent.trim().substring(0,40)),
                        onclick_row: r.getAttribute('onclick') || '',
                        links: Array.from(r.querySelectorAll('a,[onclick]')).map(a=>({
                            tag: a.tagName,
                            text: a.textContent.trim().substring(0,40),
                            onclick: (a.getAttribute('onclick')||'').substring(0,100),
                            href: a.href || ''
                        }))
                    })),
                    items_count: items_list.length,
                    links_count: all_links.length,
                    links_sample: all_links.slice(0,5).map(a=>({
                        text: a.textContent.trim().substring(0,40),
                        onclick: (a.getAttribute('onclick')||'').substring(0,100)
                    })),
                    body_text: m.innerText.replace(/\s+/g,' ').substring(0,500)
                };
            }
        """)
        R["modal_mun_resultado"] = resultado_html
        print(f"Rows: {resultado_html['rows_count']}, Links: {resultado_html['links_count']}")
        print(f"Rows sample:")
        for r in resultado_html['rows'][:5]:
            print(f"  {r['text']}")
        print(f"Links sample:")
        for l in resultado_html['links_sample']:
            print(f"  onclick={l['onclick']}")
        print(f"Body text: {resultado_html['body_text'][:300]}")

        # Tentar clicar no primeiro resultado que pareça um município
        rows = resultado_html['rows']
        clicou = False
        for row in rows:
            for lnk in row['links']:
                if lnk['onclick'] and ('selec' in lnk['onclick'].lower() or
                                       'municipio' in lnk['onclick'].lower() or
                                       'retorno' in lnk['onclick'].lower()):
                    print(f"Clicando: {lnk['onclick']}")
                    await page.evaluate(f"() => {{ {lnk['onclick']} }}")
                    await page.wait_for_timeout(1000)
                    clicou = True
                    break
            if clicou: break

        if not clicou:
            # Tentar clicar na primeira linha da tabela com conteúdo
            for row in rows[1:5]:
                if row['text'] and len(row['tds']) >= 2:
                    try:
                        await page.click(f"#mdlMunicipio table tr:nth-child(2)")
                        await page.wait_for_timeout(800)
                        clicou = True
                        break
                    except: pass

        resultado_campo = await page.evaluate("""
            () => ({
                c_cdd_ori: document.querySelector('#c_cdd_ori')?.value || '',
                t_cdd_ori: document.querySelector('#t_cdd_ori')?.value || '',
                modal_fechado: !document.querySelector('#mdlMunicipio.in')
            })
        """)
        R["resultado_campo_mun"] = resultado_campo
        print(f"Campo preenchido: {resultado_campo}")
        await page.screenshot(path=str(OUT/"mod2_03_apos_selecao_mun.png"))

        # Fechar modal se ainda aberto
        if not resultado_campo['modal_fechado']:
            await page.press("#btnFechar", "Enter") if await page.query_selector("#btnFechar") else await page.keyboard.press("Escape")
            await page.wait_for_timeout(800)

        # ── MODAL DE MERCADORIA ────────────────────────────────────────────
        print("\n=== MODAL DE MERCADORIA ===")
        # Garantir modal fechado
        await page.evaluate("() => { const m=document.querySelector('#mdlMunicipio'); if(m){m.classList.remove('in');m.style.display='none';}}")
        await page.wait_for_timeout(500)

        bt_mdr = await page.query_selector("#btModalMercadoria")
        if bt_mdr:
            await bt_mdr.click()
            await page.wait_for_timeout(1500)
            await page.screenshot(path=str(OUT/"mod2_04_mercadoria_aberto.png"))

            mdr_modais = await page.evaluate("""
                () => {
                    const visibles = Array.from(document.querySelectorAll('.modal.in, .modal[aria-hidden=false]'));
                    return visibles.map(m => ({
                        id: m.id,
                        html: m.innerHTML.substring(0, 1500)
                    }));
                }
            """)
            R["modal_mdr_visible"] = mdr_modais
            print(f"Modais visiveis: {[m['id'] for m in mdr_modais]}")
            for m in mdr_modais:
                print(f"  [{m['id']}] HTML: {m['html'][:400]}")

            # Buscar campo de texto no modal de mercadoria
            for mod in mdr_modais:
                if mod['id'] and mod['id'] != 'mdlMunicipio':
                    modal_id = mod['id']
                    # Preencher busca
                    inps = await page.evaluate(f"""
                        () => Array.from(document.querySelector('#{modal_id}')
                            .querySelectorAll('input[type=text]'))
                            .map(i=>{{return {{id:i.id, name:i.name, placeholder:i.placeholder}}}})
                    """)
                    if inps:
                        campo = inps[0]['id'] or f"[name='{inps[0]['name']}']"
                        ref = f"#{campo}" if inps[0]['id'] else campo
                        await page.fill(ref, "ELETRO")
                        await page.wait_for_timeout(300)
                        await page.keyboard.press("Enter")
                        await page.wait_for_timeout(1500)
                        await page.screenshot(path=str(OUT/"mod2_05_mercadoria_resultado.png"))
                        rows_mdr = await page.evaluate(f"""
                            () => Array.from(document.querySelector('#{modal_id}')
                                .querySelectorAll('tr, li')).slice(0,10)
                                .map(r => ({{
                                    text: r.textContent.trim().replace(/\\s+/g,' ').substring(0,80),
                                    onclick: r.getAttribute('onclick') || '',
                                    links: Array.from(r.querySelectorAll('a,[onclick]')).map(a=>
                                        ({{text:a.textContent.trim().substring(0,30),
                                          onclick:(a.getAttribute('onclick')||'').substring(0,80)}})
                                    )
                                }}))
                        """)
                        R["modal_mdr_rows"] = rows_mdr
                        print("Rows mercadoria:")
                        for row in rows_mdr:
                            print(f"  {row['text']}")
                        # Clicar primeiro resultado
                        for row in rows_mdr:
                            for lnk in row.get('links', []):
                                if lnk['onclick']:
                                    await page.evaluate(f"() => {{ {lnk['onclick']} }}")
                                    await page.wait_for_timeout(800)
                                    val_mdr = await page.evaluate("""
                                        () => ({
                                            c_mdr_irb: document.querySelector('#c_mdr_irb')?.value || '',
                                            t_mdr: document.querySelector('#t_mdr')?.value || ''
                                        })
                                    """)
                                    R["resultado_campo_mdr"] = val_mdr
                                    print(f"Campo mercadoria preenchido: {val_mdr}")
                                    break
                            if R.get("resultado_campo_mdr"): break
                    break

        await page.keyboard.press("Escape")
        await page.wait_for_timeout(500)

        # ── CONDIÇÃO ENABLE btEnviar ──────────────────────────────────────
        print("\n=== CONDICAO ENABLE btEnviar ===")
        states = []
        for desc, fn in [
            ("inicial (filial+apo+sgp selecionados)", None),
        ]:
            st = await page.evaluate("""
                () => ({
                    btEnviar_disabled: document.querySelector('#btEnviar')?.disabled,
                    u_sgp_value: document.querySelector('#u_sgp')?.value,
                    e_doc_ebq_visible: document.querySelector('#e_doc_ebq')?.offsetParent !== null,
                    e_doc_ebq_value: document.querySelector('#e_doc_ebq')?.value
                })
            """)
            states.append({"desc": desc, **st})
            print(f"  [{desc}]: btEnviar_disabled={st['btEnviar_disabled']}, "
                  f"sgp={st['u_sgp_value']}, doc_visible={st['e_doc_ebq_visible']}")

        R["btn_estados"] = states

        # Salvar resultado
        out = OUT / "map_modais2.json"
        out.write_text(json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON: {out}")
        await br.close()

asyncio.run(main())
