"""
Script final: captura interação completa dos modais com os botões corretos.
Código de município SP=34401, AC=13 (fornecidos pelo usuário).
"""
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

BASE = "https://axa-hml-faturamento.nsseg.com.br/citnet"
OUT  = Path("c:/projetos/planos-de-teste/scripts/screenshots_rctrc")
OUT.mkdir(exist_ok=True)
R    = {}

async def close_all_modals(page):
    await page.evaluate("""
        () => {
            document.querySelectorAll('.modal.in, .modal-backdrop').forEach(m => {
                m.classList.remove('in');
                m.style.display = 'none';
            });
            document.body.classList.remove('modal-open');
        }
    """)
    await page.wait_for_timeout(400)

async def main():
    async with async_playwright() as pw:
        br   = await pw.chromium.launch(headless=False, slow_mo=200)
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
        await page.wait_for_timeout(1200)
        await page.evaluate("""
            () => {
                const s = document.querySelector('#u_apo_pnc');
                s.value = '10'; s.dispatchEvent(new Event('change', {bubbles:true}));
            }
        """)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1200)
        await page.select_option("#u_sgp", "1")
        await page.wait_for_timeout(500)
        await page.select_option("#e_doc_ebq", "C")
        await page.wait_for_timeout(500)
        await page.select_option("#n_ori", "SP")
        await page.wait_for_timeout(600)

        # ── 1. MODAL MUNICÍPIO — busca por código ─────────────────────────
        print("=== 1. MODAL MUNICIPIO — busca por codigo ===")

        await page.click("#bt_cdd_ori")
        await page.wait_for_selector("#mdlMunicipio.in", timeout=8000)
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(OUT/"m3_01_mun_aberto.png"))

        # Preencher código diretamente
        await page.fill("#txtCodMunicipio", "34401")
        await page.wait_for_timeout(200)
        await page.click("#btnPesquisarMunicipio")
        await page.wait_for_timeout(2000)
        await page.screenshot(path=str(OUT/"m3_02_mun_resultado.png"))

        resultado_mun = await page.evaluate("""
            () => {
                const m = document.querySelector('#mdlMunicipio');
                const rows = Array.from(m.querySelectorAll('table tr, tbody tr'));
                const allLinks = Array.from(m.querySelectorAll('a, [onclick]'))
                    .filter(a => a.textContent.trim().length > 1 && a.id !== 'btnPesquisarMunicipio');
                return {
                    rows: rows.slice(0,10).map(r => ({
                        text: r.textContent.trim().replace(/\s+/g,' ').substring(0,100),
                        tds: Array.from(r.querySelectorAll('td')).map(t=>t.textContent.trim().substring(0,40)),
                        onclick: r.getAttribute('onclick') || '',
                        links: Array.from(r.querySelectorAll('a,[onclick]:not(#btnPesquisarMunicipio)')).map(a=>({
                            text: a.textContent.trim().substring(0,40),
                            onclick: (a.getAttribute('onclick')||'').substring(0,120)
                        }))
                    })),
                    all_links: allLinks.slice(0,5).map(a=>({
                        text: a.textContent.trim().substring(0,40),
                        onclick: (a.getAttribute('onclick')||'').substring(0,120)
                    })),
                    body: m.innerText.replace(/\s+/g,' ').substring(0,600)
                };
            }
        """)
        R["modal_mun_cod_34401"] = resultado_mun
        print(f"Body: {resultado_mun['body'][:400]}")
        print(f"Rows ({len(resultado_mun['rows'])}):")
        for r in resultado_mun['rows']:
            print(f"  {r['text']} | onclick={r['onclick'][:60]}")
        print(f"Links:")
        for l in resultado_mun['all_links']:
            print(f"  {l['text']} | onclick={l['onclick'][:80]}")

        # Tentar clicar no resultado
        selecionou = False
        for r in resultado_mun['rows']:
            if r['onclick']:
                await page.evaluate(f"() => {{ {r['onclick']} }}")
                await page.wait_for_timeout(800)
                selecionou = True
                break
            for lnk in r['links']:
                if lnk['onclick']:
                    await page.evaluate(f"() => {{ {lnk['onclick']} }}")
                    await page.wait_for_timeout(800)
                    selecionou = True
                    break
            if selecionou: break

        campos_mun = await page.evaluate("""
            () => ({
                c_cdd_ori: document.querySelector('#c_cdd_ori')?.value || '',
                t_cdd_ori: document.querySelector('#t_cdd_ori')?.value || '',
                modal_still_open: !!document.querySelector('#mdlMunicipio.in')
            })
        """)
        R["campos_pos_selecao_mun"] = campos_mun
        print(f"Campos pos-selecao: {campos_mun}")
        await page.screenshot(path=str(OUT/"m3_03_apos_selecao.png"))

        # ── 2. INJEÇÃO DIRETA DO CÓDIGO (estratégia alternativa) ──────────
        print("\n=== 2. INJECAO DIRETA DE CODIGO (alternativa robusta) ===")
        await close_all_modals(page)
        await page.wait_for_timeout(300)

        # Preencher código diretamente via JS (bypass do modal)
        await page.evaluate("""
            () => {
                const cod = document.querySelector('#c_cdd_ori');
                const nome = document.querySelector('#t_cdd_ori');
                if (cod) { cod.value = '34401'; cod.dispatchEvent(new Event('change',{bubbles:true})); }
                if (nome) { nome.value = 'SAO PAULO'; }
            }
        """)
        await page.wait_for_timeout(500)
        val_direto = await page.evaluate("""
            () => ({
                c_cdd_ori: document.querySelector('#c_cdd_ori')?.value,
                t_cdd_ori: document.querySelector('#t_cdd_ori')?.value
            })
        """)
        R["injecao_direta"] = val_direto
        print(f"Injecao direta: {val_direto}")

        # ── 3. MODAL DE MERCADORIA ────────────────────────────────────────
        print("\n=== 3. MODAL DE MERCADORIA ===")
        await close_all_modals(page)
        await page.wait_for_timeout(400)

        bt_mdr = page.locator("#btModalMercadoria")
        await bt_mdr.click(force=True)
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(OUT/"m3_04_mdr_aberto.png"))

        mdr_state = await page.evaluate("""
            () => {
                const all_modals = Array.from(document.querySelectorAll('.modal'))
                    .filter(m => m.offsetParent !== null || m.classList.contains('in'));
                return all_modals.map(m => ({
                    id: m.id,
                    visible: m.offsetParent !== null,
                    in_class: m.classList.contains('in'),
                    body_text: m.innerText.replace(/\s+/g,' ').substring(0,300),
                    inputs: Array.from(m.querySelectorAll('input')).map(i=>({id:i.id,name:i.name,type:i.type})),
                    buttons: Array.from(m.querySelectorAll('a.btn,button,[onclick]'))
                        .filter(b => b.textContent.trim().length > 0)
                        .map(b=>({tag:b.tagName,id:b.id,text:b.textContent.trim().substring(0,30),
                                  onclick:(b.getAttribute('onclick')||'').substring(0,80)}))
                }));
            }
        """)
        R["modal_mdr_state"] = mdr_state
        for m in mdr_state:
            print(f"  Modal [{m['id']}] in={m['in_class']} text={m['body_text'][:150]}")
            for inp in m['inputs']:
                print(f"    input: {inp}")
            for btn in m['buttons']:
                print(f"    btn: {btn}")

        # Tentar busca no modal de mercadoria
        mdr_modal = next((m for m in mdr_state if m['id'] not in ('', 'mdlMunicipio')
                          and (m['in_class'] or m['visible'])), None)
        if mdr_modal:
            mdr_id = mdr_modal['id']
            text_inp = next((i for i in mdr_modal['inputs'] if i['type'] == 'text'), None)
            pesq_btn = next((b for b in mdr_modal['buttons']
                             if 'pesquis' in b['text'].lower() or 'buscar' in b['text'].lower()), None)
            print(f"\nModal mercadoria ID={mdr_id}, campo={text_inp}, btn={pesq_btn}")

            if text_inp and text_inp['id']:
                await page.fill(f"#{text_inp['id']}", "ELETRONICO")
                await page.wait_for_timeout(300)
                if pesq_btn and pesq_btn['id']:
                    await page.click(f"#{pesq_btn['id']}", force=True)
                else:
                    await page.keyboard.press("Enter")
                await page.wait_for_timeout(2000)
                await page.screenshot(path=str(OUT/"m3_05_mdr_resultado.png"))

                rows_mdr = await page.evaluate(f"""
                    () => {{
                        const m = document.querySelector('#{mdr_id}');
                        return Array.from(m.querySelectorAll('tr,li')).slice(0,10).map(r => ({{
                            text: r.textContent.trim().replace(/\\s+/g,' ').substring(0,100),
                            onclick: r.getAttribute('onclick') || '',
                            links: Array.from(r.querySelectorAll('a,[onclick]'))
                                .map(a=>{{return {{text:a.textContent.trim().substring(0,30),
                                    onclick:(a.getAttribute('onclick')||'').substring(0,100)}};}})
                        }}));
                    }}
                """)
                R["modal_mdr_rows"] = rows_mdr
                print("Rows mercadoria:")
                for row in rows_mdr:
                    print(f"  {row['text']}")

                # Clicar no primeiro resultado
                for row in rows_mdr:
                    for lnk in row.get('links', []):
                        if lnk['onclick']:
                            await page.evaluate(f"() => {{ {lnk['onclick']} }}")
                            await page.wait_for_timeout(1000)
                            val = await page.evaluate("""
                                () => ({
                                    c_mdr_irb: document.querySelector('#c_mdr_irb')?.value,
                                    t_mdr: document.querySelector('#t_mdr')?.value
                                })
                            """)
                            R["resultado_mdr"] = val
                            print(f"Mercadoria preenchida: {val}")
                            break
                    if R.get("resultado_mdr"): break

        await close_all_modals(page)

        # ── 4. CTE KEY — algoritmo módulo 11 ────────────────────────────
        print("\n=== 4. CTE KEY — verificar campo e max length ===")
        cte_info = await page.evaluate("""
            () => {
                const f = document.querySelector('#u_cnh_elt');
                return f ? {maxlength: f.maxLength, placeholder: f.placeholder, required: f.required} : null;
            }
        """)
        R["cte_field_info"] = cte_info
        print(f"Campo CTE: {cte_info}")

        # Salvar
        out = OUT / "map_modais3.json"
        out.write_text(json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON: {out}")
        await br.close()

asyncio.run(main())
