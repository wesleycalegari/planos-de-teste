"""
Mapeia modal de município (busca SP, RJ, AM) e modal de mercadoria.
Também confirma comportamento de e_tr1=F (fluvial) e habilita s_uf_bld/n_bld.
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
        br   = await pw.chromium.launch(headless=False, slow_mo=200)
        ctx  = await br.new_context(viewport={"width": 1366, "height": 768})
        page = await ctx.new_page()
        page.set_default_timeout(30000)

        await page.goto(f"{BASE}/")
        await page.fill("#usuario", "interno")
        await page.fill("#senha", "11")
        await page.click("#btLogin1")
        await page.wait_for_load_state("networkidle")

        await page.goto(f"{BASE}/AverbacaoNacional/AverbacaoRCTRC")
        await page.wait_for_load_state("networkidle")

        # Selecionar filial e apólice
        await page.select_option("#c_org_prd", "1")
        await page.wait_for_timeout(1200)
        await page.evaluate("""
            () => {
                const sel = document.querySelector('#u_apo_pnc');
                sel.value = '10';
                sel.dispatchEvent(new Event('change', {bubbles: true}));
            }
        """)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1500)

        # ── 1. CONFIRMAR e_tr1 OPÇÕES E COMPORTAMENTO FLUVIAL ────────────
        print("=== 1. e_tr1 e percurso fluvial ===")
        e_tr1_opts = await page.evaluate("""
            () => {
                const sel = document.querySelector('#e_tr1');
                return {
                    options: Array.from(sel.options).map(o=>({v:o.value, t:o.text.trim()})),
                    current: sel.value
                };
            }
        """)
        R["e_tr1_options"] = e_tr1_opts
        print(f"Opcoes e_tr1: {e_tr1_opts}")

        # Selecionar F (Rodo-Fluvial) e ver o que muda
        await page.select_option("#e_tr1", "F")
        await page.wait_for_timeout(800)
        await page.screenshot(path=str(OUT/"modais_01_fluvial_ativo.png"))

        fluvial_state = await page.evaluate("""
            () => {
                const bld  = document.querySelector('#s_uf_bld');
                const n_bld = document.querySelector('#n_bld');
                const e_tr2 = document.querySelector('#e_tr2');
                // verificar o que ficou visivel/habilitado
                return {
                    s_uf_bld: {
                        found: !!bld, visible: bld?.offsetParent !== null,
                        disabled: bld?.disabled, value: bld?.value
                    },
                    n_bld: {
                        found: !!n_bld, visible: n_bld?.offsetParent !== null,
                        disabled: n_bld?.disabled,
                        options: n_bld ? Array.from(n_bld.options).slice(0,5)
                            .map(o=>({v:o.value, t:o.text.trim()})) : []
                    },
                    e_tr2_exists: !!e_tr2,
                    e_tr1_value: document.querySelector('#e_tr1')?.value
                };
            }
        """)
        R["fluvial_state"] = fluvial_state
        print(f"Estado apos e_tr1=F: {json.dumps(fluvial_state, ensure_ascii=False, indent=2)}")

        # Voltar para Rodoviário
        await page.select_option("#e_tr1", "T")
        await page.wait_for_timeout(500)

        # ── 2. MODAL DE MUNICÍPIO — mapear interação completa ─────────────
        print("\n=== 2. MODAL DE MUNICIPIO ===")

        async def buscar_municipio(uf_select, uf_value, busca_nome, label):
            await page.select_option(uf_select, uf_value)
            await page.wait_for_timeout(600)

            # Clicar no botão de busca
            btn_id = "#bt_cdd_ori" if "ori" in uf_select else "#bt_cdd_dst"
            bt = await page.query_selector(btn_id)
            if not bt or not await bt.is_visible():
                print(f"  {label}: botao {btn_id} nao visivel")
                return None

            await bt.click()
            await page.wait_for_timeout(1000)

            # Aguardar modal ficar visível
            try:
                await page.wait_for_selector("#mdlMunicipio", state="visible", timeout=5000)
            except:
                print(f"  {label}: modal nao abriu")
                return None

            await page.screenshot(path=str(OUT / f"modais_mun_{uf_value}.png"))

            # Preencher nome e pesquisar
            await page.fill("#txtNomeMunicipio", busca_nome)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(1500)
            await page.screenshot(path=str(OUT / f"modais_mun_{uf_value}_resultado.png"))

            # Capturar linhas de resultado
            rows = await page.evaluate("""
                () => {
                    const modal = document.querySelector('#mdlMunicipio');
                    // Procurar tabela de resultados
                    const rows = Array.from(modal.querySelectorAll('table tr, .grid-row, li'));
                    return rows.slice(0, 15).map(r => ({
                        text: r.textContent.trim().replace(/\\s+/g,' ').substring(0,100),
                        onclick: (r.getAttribute('onclick') || ''),
                        links: Array.from(r.querySelectorAll('a, [onclick]'))
                            .map(a => ({
                                text: a.textContent.trim().substring(0,40),
                                onclick: (a.getAttribute('onclick') || '').substring(0,80),
                                href: a.href || ''
                            }))
                    }));
                }
            """)
            print(f"  {label} — rows:")
            for row in rows:
                print(f"    {row['text']}")

            # Tentar clicar no primeiro resultado
            first_link = None
            for row in rows:
                if row['links']:
                    first_link = row['links'][0]
                    break

            if first_link and first_link['onclick']:
                print(f"  Clicando no primeiro resultado: {first_link['text']} | {first_link['onclick'][:60]}")
                try:
                    await page.evaluate(f"() => {{ {first_link['onclick']} }}")
                    await page.wait_for_timeout(800)
                except:
                    pass
            else:
                # Tentar clicar na primeira linha da tabela
                try:
                    await page.click("#mdlMunicipio table tr:nth-child(2) td:first-child")
                    await page.wait_for_timeout(800)
                except:
                    await page.keyboard.press("Escape")
                    await page.wait_for_timeout(500)

            # Capturar valor preenchido no campo
            campo_id = "#c_cdd_ori" if "ori" in uf_select else "#c_cdd_dst"
            campo_nome_id = "#t_cdd_ori" if "ori" in uf_select else "#t_cdd_dst"
            val = await page.evaluate(f"""
                () => ({{
                    codigo: document.querySelector('{campo_id}')?.value || '',
                    nome:   document.querySelector('{campo_nome_id}')?.value || ''
                }})
            """)
            print(f"  Resultado preenchido: {val}")
            return {"busca": busca_nome, "uf": uf_value, "resultado": val, "rows": rows[:5]}

        # Buscar SP
        r_sp = await buscar_municipio("#n_ori", "SP", "SAO PAULO", "SP - Sao Paulo")
        if r_sp: R["municipio_sp"] = r_sp

        # Buscar RJ
        r_rj = await buscar_municipio("#n_dst", "RJ", "RIO DE JANEIRO", "RJ - Rio de Janeiro")
        if r_rj: R["municipio_rj"] = r_rj

        # Buscar AM (fluvial)
        r_am = await buscar_municipio("#n_ori", "AM", "MANAUS", "AM - Manaus")
        if r_am: R["municipio_am"] = r_am

        # ── 3. MODAL DE MERCADORIA ────────────────────────────────────────
        print("\n=== 3. MODAL DE MERCADORIA ===")

        # Garantir que nenhum modal está aberto
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(500)

        bt_mdr = await page.query_selector("#btModalMercadoria")
        if bt_mdr and await bt_mdr.is_visible():
            await bt_mdr.click()
            await page.wait_for_timeout(1200)

            # Aguardar qualquer modal visível
            try:
                modais = await page.evaluate("""
                    () => {
                        const ms = Array.from(document.querySelectorAll('.modal'))
                            .filter(m => m.offsetParent !== null || m.classList.contains('in'));
                        return ms.map(m => ({
                            id: m.id,
                            class: m.className.substring(0,60),
                            visible: m.offsetParent !== null,
                            inputs: Array.from(m.querySelectorAll('input'))
                                .map(i => ({id:i.id, name:i.name, type:i.type, placeholder:i.placeholder})),
                            buttons: Array.from(m.querySelectorAll('button, input[type=button]'))
                                .map(b => ({id:b.id, text:b.textContent.trim().substring(0,30)}))
                        }));
                    }
                """)
                R["modal_mercadoria_state"] = modais
                print(f"Modais abertos: {json.dumps(modais, ensure_ascii=False, indent=2)}")
                await page.screenshot(path=str(OUT/"modais_mercadoria.png"))

                # Tentar buscar no modal de mercadoria
                for modal in modais:
                    if modal['id'] != 'mdlMunicipio':
                        inp = next((i for i in modal['inputs'] if i['id'] and i['type'] == 'text'), None)
                        if inp:
                            await page.fill(f"#{inp['id']}", "ELETRONICO")
                            await page.wait_for_timeout(400)
                            await page.keyboard.press("Enter")
                            await page.wait_for_timeout(1500)
                            await page.screenshot(path=str(OUT/"modais_mercadoria_resultado.png"))
                            rows_mdr = await page.evaluate(f"""
                                () => {{
                                    const m = document.querySelector('#{modal['id']}');
                                    if (!m) return [];
                                    return Array.from(m.querySelectorAll('tr')).slice(0,10)
                                        .map(r => {{
                                            const links = Array.from(r.querySelectorAll('a,[onclick]'));
                                            return {{
                                                text: r.textContent.trim().replace(/\\s+/g,' ').substring(0,100),
                                                links: links.map(a => ({{
                                                    text: a.textContent.trim().substring(0,30),
                                                    onclick: (a.getAttribute('onclick')||'').substring(0,80)
                                                }}))
                                            }};
                                        }});
                                }}
                            """)
                            R["modal_mercadoria_rows"] = rows_mdr
                            print("Rows mercadoria:")
                            for row in rows_mdr:
                                print(f"  {row['text']}")
                            break
            except Exception as e:
                print(f"  Erro modal mercadoria: {e}")

        await page.keyboard.press("Escape")
        await page.wait_for_timeout(500)

        # ── 4. VERIFICAR CONDIÇÃO ENABLE DE btEnviar ─────────────────────
        print("\n=== 4. CONDICAO ENABLE btEnviar ===")
        btn_state = await page.evaluate("""
            () => ({
                btEnviar_disabled: document.querySelector('#btEnviar')?.disabled,
                e_doc_ebq_visible: document.querySelector('#e_doc_ebq')?.offsetParent !== null,
                u_sgp_value: document.querySelector('#u_sgp')?.value
            })
        """)
        R["btn_state_com_apolice"] = btn_state
        print(f"Estado com apolice: {btn_state}")

        # Selecionar subgrupo
        sgps = await page.evaluate("""
            () => Array.from(document.querySelector('#u_sgp').options)
                .filter(o => o.value && o.value !== '0').map(o => ({v:o.value, t:o.text}))
        """)
        if sgps:
            await page.select_option("#u_sgp", sgps[0]['v'])
            await page.wait_for_timeout(800)
            btn_state2 = await page.evaluate("""
                () => ({
                    btEnviar_disabled: document.querySelector('#btEnviar')?.disabled,
                    e_doc_ebq_visible: document.querySelector('#e_doc_ebq')?.offsetParent !== null,
                })
            """)
            R["btn_state_com_sgp"] = btn_state2
            print(f"Estado com subgrupo selecionado: {btn_state2}")

        # Salvar JSON
        out = OUT / "map_modais.json"
        out.write_text(json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON: {out}")
        await br.close()

asyncio.run(main())
