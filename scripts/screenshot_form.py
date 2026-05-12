"""
Captura screenshot full-page do formulário RCTRC após seleção de apólice.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE = "https://axa-hml-faturamento.nsseg.com.br/citnet"
OUT  = Path("c:/projetos/planos-de-teste/scripts/screenshots_rctrc")

async def main():
    async with async_playwright() as pw:
        br   = await pw.chromium.launch(headless=True)
        page = await (await br.new_context(viewport={"width":1366,"height":900})).new_page()
        page.set_default_timeout(25000)

        await page.goto(f"{BASE}/", wait_until="domcontentloaded")
        await page.wait_for_selector("#usuario", timeout=30000)
        await page.fill("#usuario","interno"); await page.fill("#senha","11"); await page.click("#btLogin1"); await page.wait_for_load_state("networkidle")
        await page.goto(f"{BASE}/AverbacaoNacional/AverbacaoRCTRC"); await page.wait_for_load_state("networkidle")
        await page.select_option("#c_org_prd","1"); await page.wait_for_timeout(1500)
        await page.evaluate("()=>{const s=document.querySelector('#u_apo_pnc');s.value='10';s.dispatchEvent(new Event('change',{bubbles:true}));}")
        await page.wait_for_load_state("networkidle"); await page.wait_for_timeout(1500)
        await page.select_option("#u_sgp","1"); await page.wait_for_timeout(600)
        await page.select_option("#e_doc_ebq","C"); await page.wait_for_timeout(500)

        # Screenshot da tela completa (com scroll)
        await page.screenshot(path=str(OUT/"form_tela_completa.png"), full_page=True)
        print("Screenshot salvo em form_tela_completa.png")

        # Verificar via CSS computed style o que está REALMENTE visível
        visibilidade = await page.evaluate("""
            () => {
                const ids = [
                    'i_tar_adl_ocd','i_tar_adl_ica','i_tar_adl_avr','i_tar_adl_pmf',
                    'i_tar_adl_lbr_pst','i_tar_adl_rbo_prl_rcf','i_tar_adl_rbo_dpt_rcf',
                    'i_tar_dsc_bnf_itn','btImprimir','btExcluir','btNovo','btEnviar',
                    'v_is_rcf','v_is_cnn','v_fte','v_is_cnn_rcf','v_fte_rcf',
                    'mostraReferencial','mostraReferencialRcf'
                ];
                return ids.map(id => {
                    const el = document.querySelector('#' + id) || document.getElementById(id);
                    if (!el) return {id, found: false};
                    const cs = window.getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    const parent = el.closest('[style*="display:none"], [style*="display: none"]');
                    return {
                        id,
                        found:      true,
                        display:    cs.display,
                        visibility: cs.visibility,
                        opacity:    cs.opacity,
                        offsetParent: el.offsetParent !== null,
                        rect_w:     Math.round(rect.width),
                        rect_h:     Math.round(rect.height),
                        hidden_parent: !!parent,
                        disabled:   el.disabled || false
                    };
                });
            }
        """)

        print("\n=== VISIBILIDADE REAL (computed style) ===")
        print(f"{'ID':<35} {'display':<12} {'visibility':<12} {'offsetP':<8} {'w×h':<10} {'disabled'}")
        print("-"*95)
        for v in visibilidade:
            if not v['found']:
                print(f"{v['id']:<35} NÃO ENCONTRADO NO DOM")
                continue
            wp = 'SIM' if v['offsetParent'] else 'não'
            print(f"{v['id']:<35} {v['display']:<12} {v['visibility']:<12} {wp:<8} {v['rect_w']}×{v['rect_h']:<6} {'DIS' if v['disabled'] else ''}")

        # Verificar se há div pai que esconde os adicionais
        contexto_adl = await page.evaluate("""
            () => {
                const el = document.querySelector('#i_tar_adl_ocd');
                if (!el) return null;
                // subir até 5 níveis
                let node = el, chain = [];
                for (let i = 0; i < 8; i++) {
                    if (!node || node === document.body) break;
                    const cs = window.getComputedStyle(node);
                    chain.push({tag: node.tagName, id: node.id||'', cls: node.className.substring(0,40), display: cs.display, visibility: cs.visibility});
                    node = node.parentElement;
                }
                return chain;
            }
        """)
        print("\n=== CADEIA DE PAIS de #i_tar_adl_ocd ===")
        if contexto_adl:
            for n in contexto_adl:
                print(f"  <{n['tag']}#{n['id']} .{n['cls']}> display={n['display']} visibility={n['visibility']}")

        await br.close()

asyncio.run(main())
