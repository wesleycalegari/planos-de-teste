"""
Passo 2: seleciona filial → captura apólices → classifica tipos.
Também mapeia e_tr2, modal de município e modal de mercadoria.
"""
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

BASE  = "https://axa-hml-faturamento.nsseg.com.br/citnet"
USER  = "interno"
PASS  = "11"
OUT   = Path("c:/projetos/planos-de-teste/scripts/screenshots_rctrc")
OUT.mkdir(exist_ok=True)
R     = {}

async def main():
    async with async_playwright() as pw:
        br   = await pw.chromium.launch(headless=False, slow_mo=150)
        ctx  = await br.new_context(viewport={"width": 1366, "height": 768})
        page = await ctx.new_page()
        page.set_default_timeout(30000)

        # ── LOGIN ─────────────────────────────────────────────────────────
        await page.goto(f"{BASE}/")
        await page.fill("#usuario", USER)
        await page.fill("#senha", PASS)
        await page.click("#btLogin1")
        await page.wait_for_load_state("networkidle")

        # ── NAVEGAR PARA RCTRC ────────────────────────────────────────────
        await page.goto(f"{BASE}/AverbacaoNacional/AverbacaoRCTRC")
        await page.wait_for_load_state("networkidle")

        # ── FILIAIS DISPONÍVEIS ───────────────────────────────────────────
        filiais = await page.evaluate("""
            () => {
                const sel = document.querySelector('#c_org_prd');
                if (!sel) return {error: 'not found'};
                return {
                    id: sel.id,
                    options: Array.from(sel.options).map(o => ({v: o.value, t: o.text.trim()}))
                };
            }
        """)
        R["filiais"] = filiais
        print("Filiais:", json.dumps(filiais, ensure_ascii=False))

        valid_filiais = [o for o in filiais.get("options", []) if o["v"] not in ("", "0")]
        if not valid_filiais:
            print("ERRO: nenhuma filial disponivel")
            await br.close()
            return

        primeira_filial = valid_filiais[0]
        print(f"Selecionando filial: {primeira_filial}")

        # ── SELECIONAR FILIAL ─────────────────────────────────────────────
        await page.select_option("#c_org_prd", primeira_filial["v"])
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(OUT/"map2_01_filial_selecionada.png"))

        # ── CAPTURAR APÓLICES ─────────────────────────────────────────────
        apolices_raw = await page.evaluate("""
            () => {
                const sel = document.querySelector('#u_apo_pnc');
                if (!sel) return [];
                return Array.from(sel.options).map(o => ({v: o.value, t: o.text.trim()}));
            }
        """)
        R["apolices_raw"] = apolices_raw
        valid_apos = [o for o in apolices_raw if o["v"] not in ("", "0")]
        print(f"Apolicies encontradas ({len(valid_apos)}):")
        for a in valid_apos:
            print(f"  [{a['v']}] {a['t']}")

        # ── CLASSIFICAR CADA APÓLICE ──────────────────────────────────────
        classificadas = {}
        for apo in valid_apos[:25]:
            await page.evaluate(f"""
                () => {{
                    const sel = document.querySelector('#u_apo_pnc');
                    sel.value = '{apo['v']}';
                    sel.dispatchEvent(new Event('change', {{bubbles: true}}));
                }}
            """)
            await page.wait_for_timeout(1300)
            info = await page.evaluate("""
                () => ({
                    hdTipoApolice: document.querySelector('#hdTipoApolice')?.value || '',
                    c_rmo_rfc:     document.querySelector('#c_rmo_rfc')?.value || '0',
                    ddr:           document.querySelector('#permitirEstipulacaoDDR')?.value || '',
                    cte_habilit:   document.querySelector('#hdCte')?.value || '',
                    btn_disabled:  document.querySelector('#btEnviar')?.disabled,
                    sgps: (() => {
                        const s = document.querySelector('#u_sgp');
                        return s ? Array.from(s.options)
                            .filter(o => o.value && o.value !== '0')
                            .map(o => ({v: o.value, t: o.text.trim()})) : [];
                    })()
                })
            """)
            classificadas[apo['v']] = {
                "texto": apo['t'],
                "tipo": info['hdTipoApolice'],
                "tem_rcf": info['c_rmo_rfc'] != '0',
                "rcf_numero": info['c_rmo_rfc'],
                "ddr": info['ddr'],
                "cte": info['cte_habilit'],
                "btn_ok": not info['btn_disabled'],
                "subgrupos": info['sgps']
            }
            print(f"  {apo['v']:<25} T={info['hdTipoApolice']:<3} "
                  f"RCF={info['c_rmo_rfc']:<8} DDR={info['ddr']:<3} "
                  f"CTE={info['cte_habilit']:<3} "
                  f"SGPs={len(info['sgps'])} "
                  f"| {apo['t'][:35]}")

        R["classificadas"] = classificadas

        # ── SELECIONAR APÓLICE COM MAIOR INFO PARA INSPEÇÃO PROFUNDA ─────
        apo_para_inspecao = valid_apos[0]['v'] if valid_apos else None
        if apo_para_inspecao:
            await page.evaluate(f"""
                () => {{
                    const sel = document.querySelector('#u_apo_pnc');
                    sel.value = '{apo_para_inspecao}';
                    sel.dispatchEvent(new Event('change', {{bubbles: true}}));
                }}
            """)
            await page.wait_for_timeout(1500)

            # ── INSPECIONAR e_tr2 e SEÇÃO PERCURSO ───────────────────────
            print("\n=== MAPEANDO e_tr2 / PERCURSO FLUVIAL ===")
            e_tr2 = await page.evaluate("""
                () => {
                    // Busca exaustiva por e_tr2
                    const by_id   = document.querySelector('#e_tr2');
                    const by_name = document.querySelector('[name="e_tr2"]');
                    // Todos os inputs em torno da área de meio de transporte
                    const e_tr1   = document.querySelector('#e_tr1');
                    let around = [];
                    if (e_tr1) {
                        const parent = e_tr1.closest('.row, .form-group, fieldset');
                        if (parent) {
                            around = Array.from(parent.querySelectorAll('input, select'))
                                .map(el => ({tag:el.tagName, id:el.id, name:el.name,
                                             type:el.type, value:el.value}));
                        }
                    }
                    // Busca por texto "fluvial" ou "transbordo" no HTML inteiro
                    const full_html = document.body.innerHTML;
                    const fluvial_idx = full_html.toLowerCase().indexOf('fluvial');
                    const fluvial_ctx = fluvial_idx >= 0
                        ? full_html.substring(Math.max(0, fluvial_idx-200), fluvial_idx+400)
                        : 'nao encontrado';
                    return {
                        by_id:    by_id ? {id:by_id.id, type:by_id.type, value:by_id.value} : null,
                        by_name:  by_name ? {id:by_name.id, name:by_name.name} : null,
                        around_e_tr1: around,
                        fluvial_ctx: fluvial_ctx.substring(0, 600)
                    };
                }
            """)
            R["e_tr2_deep"] = e_tr2
            print(f"by_id: {e_tr2['by_id']}")
            print(f"by_name: {e_tr2['by_name']}")
            print(f"around e_tr1: {e_tr2['around_e_tr1']}")
            print(f"fluvial ctx: {e_tr2['fluvial_ctx'][:400]}")

            # ── TESTAR INTERAÇÃO COM MODAL DE MUNICÍPIO ───────────────────
            print("\n=== MAPEANDO MODAL DE MUNICIPIO ===")
            # Selecionar UF origem para habilitar o botão de município
            await page.select_option("#n_ori", "SP")
            await page.wait_for_timeout(800)
            await page.screenshot(path=str(OUT/"map2_02_uf_sp_selecionada.png"))

            modal_mun_pre = await page.evaluate("""
                () => {
                    const bt_ori = document.querySelector('#bt_cdd_ori');
                    const modal  = document.querySelector('#mdlMunicipio');
                    const c_ori  = document.querySelector('#c_cdd_ori');
                    return {
                        bt_ori_found:    !!bt_ori,
                        bt_ori_visible:  bt_ori ? bt_ori.offsetParent !== null : false,
                        bt_ori_disabled: bt_ori ? bt_ori.disabled : null,
                        modal_found:     !!modal,
                        c_cdd_ori_visible: c_ori ? c_ori.offsetParent !== null : false
                    };
                }
            """)
            R["modal_mun_pre"] = modal_mun_pre
            print(f"Pre-modal municipio: {modal_mun_pre}")

            # Tentar clicar no botão de município de origem
            try:
                bt = await page.query_selector("#bt_cdd_ori")
                if bt and await bt.is_visible():
                    await bt.click()
                    await page.wait_for_timeout(1500)
                    await page.screenshot(path=str(OUT/"map2_03_modal_municipio.png"))
                    modal_state = await page.evaluate("""
                        () => {
                            const modal = document.querySelector('#mdlMunicipio');
                            if (!modal) return {found: false};
                            const inputs  = Array.from(modal.querySelectorAll('input'));
                            const buttons = Array.from(modal.querySelectorAll('button, input[type=button]'));
                            const grid    = modal.querySelector('table, .grid, [id*="grid"], [id*="Grid"]');
                            return {
                                found:   true,
                                visible: modal.offsetParent !== null,
                                inputs:  inputs.map(i => ({id:i.id, name:i.name, type:i.type, placeholder:i.placeholder})),
                                buttons: buttons.map(b => ({id:b.id, text:b.textContent.trim().substring(0,30)})),
                                grid_id: grid ? (grid.id || grid.className.substring(0,40)) : null
                            };
                        }
                    """)
                    R["modal_mun_state"] = modal_state
                    print(f"Modal municipio: {json.dumps(modal_state, ensure_ascii=False, indent=2)}")

                    # Tentar pesquisar "Sao Paulo" no campo de busca do modal
                    if modal_state.get("found") and modal_state.get("visible"):
                        search_input = modal_state["inputs"][0] if modal_state["inputs"] else None
                        if search_input:
                            await page.fill(f"#{search_input['id']}", "SAO PAULO")
                            await page.wait_for_timeout(500)
                            # Clicar botão de pesquisa
                            search_btn = next((b for b in modal_state["buttons"]
                                               if "pesquis" in b["text"].lower() or "buscar" in b["text"].lower()
                                               or "ok" in b["text"].lower()), None)
                            if search_btn:
                                await page.click(f"#{search_btn['id']}")
                                await page.wait_for_timeout(1500)
                                await page.screenshot(path=str(OUT/"map2_04_modal_resultado_mun.png"))
                                # Capturar linhas da tabela resultado
                                rows = await page.evaluate("""
                                    () => {
                                        const modal = document.querySelector('#mdlMunicipio');
                                        if (!modal) return [];
                                        const rows = Array.from(modal.querySelectorAll('tr')).slice(0,10);
                                        return rows.map(r => ({
                                            html: r.innerHTML.substring(0,200),
                                            text: r.textContent.trim().substring(0,100)
                                        }));
                                    }
                                """)
                                R["modal_mun_rows"] = rows
                                print("Rows municipio:")
                                for row in rows:
                                    print(f"  {row['text']}")
                        # Fechar modal
                        await page.keyboard.press("Escape")
                        await page.wait_for_timeout(500)
                else:
                    print("  bt_cdd_ori nao visivel ou nao encontrado")
            except Exception as e:
                print(f"  Erro ao interagir com modal municipio: {e}")
                await page.keyboard.press("Escape")

            # ── TESTAR MODAL DE MERCADORIA ────────────────────────────────
            print("\n=== MAPEANDO MODAL DE MERCADORIA ===")
            try:
                bt_mdr = await page.query_selector("#btModalMercadoria")
                if bt_mdr and await bt_mdr.is_visible():
                    await bt_mdr.click()
                    await page.wait_for_timeout(1500)
                    await page.screenshot(path=str(OUT/"map2_05_modal_mercadoria.png"))
                    modal_mdr = await page.evaluate("""
                        () => {
                            // Encontrar o modal de mercadoria — pode ter id diferente
                            const modals = Array.from(document.querySelectorAll('.modal, [role=dialog]'))
                                .filter(m => m.offsetParent !== null);
                            if (modals.length === 0) return {found: false};
                            const m = modals[modals.length - 1];  // o último aberto
                            const inputs  = Array.from(m.querySelectorAll('input'));
                            const buttons = Array.from(m.querySelectorAll('button, a[onclick], input[type=button]'));
                            const rows    = Array.from(m.querySelectorAll('tr')).slice(0,5);
                            return {
                                found: true,
                                modal_id: m.id,
                                modal_class: m.className.substring(0,60),
                                inputs:  inputs.map(i => ({id:i.id, name:i.name, placeholder:i.placeholder})),
                                buttons: buttons.map(b => ({id:b.id, text:b.textContent.trim().substring(0,30)})),
                                rows: rows.map(r => r.textContent.trim().substring(0,80))
                            };
                        }
                    """)
                    R["modal_mdr"] = modal_mdr
                    print(f"Modal mercadoria: {json.dumps(modal_mdr, ensure_ascii=False, indent=2)}")

                    if modal_mdr.get("found"):
                        # Tentar buscar mercadoria
                        inp = next((i for i in modal_mdr["inputs"] if i["id"] or i["name"]), None)
                        if inp:
                            field_id = inp["id"] or f"[name='{inp['name']}']"
                            await page.fill(f"#{field_id}" if inp["id"] else field_id, "ELETR")
                            await page.wait_for_timeout(500)
                            # Clicar buscar
                            await page.keyboard.press("Enter")
                            await page.wait_for_timeout(1500)
                            await page.screenshot(path=str(OUT/"map2_06_modal_mercadoria_resultado.png"))
                            rows_mdr = await page.evaluate("""
                                () => {
                                    const modals = Array.from(document.querySelectorAll('.modal, [role=dialog]'))
                                        .filter(m => m.offsetParent !== null);
                                    const m = modals[modals.length-1];
                                    if (!m) return [];
                                    return Array.from(m.querySelectorAll('tr')).slice(0,10)
                                        .map(r => ({
                                            text: r.textContent.trim().substring(0,100),
                                            links: Array.from(r.querySelectorAll('a, [onclick]'))
                                                .map(a => ({href: a.href||'', onclick: (a.getAttribute('onclick')||'').substring(0,80)}))
                                        }));
                                }
                            """)
                            R["modal_mdr_rows"] = rows_mdr
                            print("Rows mercadoria:")
                            for row in rows_mdr:
                                print(f"  {row['text']}")
                    await page.keyboard.press("Escape")
                    await page.wait_for_timeout(500)
                else:
                    print("  btModalMercadoria nao visivel")
            except Exception as e:
                print(f"  Erro modal mercadoria: {e}")
                await page.keyboard.press("Escape")

        # ── SALVAR RESULTADO ──────────────────────────────────────────────
        out_json = OUT / "map_result2.json"
        out_json.write_text(json.dumps(R, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON salvo: {out_json}")
        await br.close()

asyncio.run(main())
