"""
Captura código IRB de mercadoria no modal #mdlMercadoria.
Busca por código numérico e aguarda resultados reais.
"""
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

BASE = "https://axa-hml-faturamento.nsseg.com.br/citnet"
OUT  = Path("c:/projetos/planos-de-teste/scripts/screenshots_rctrc")
OUT.mkdir(exist_ok=True)

async def close_all(page):
    await page.evaluate("""
        () => { document.querySelectorAll('.modal.in,.modal-backdrop').forEach(m=>{
            m.classList.remove('in'); m.style.display='none';});
            document.body.classList.remove('modal-open'); }
    """)
    await page.wait_for_timeout(400)

async def main():
    async with async_playwright() as pw:
        br   = await pw.chromium.launch(headless=False, slow_mo=150)
        page = await (await br.new_context(viewport={"width":1366,"height":768})).new_page()
        page.set_default_timeout(30000)

        print("Fazendo login...")
        await page.goto(f"{BASE}/"); await page.fill("#usuario","interno"); await page.fill("#senha","11"); await page.click("#btLogin1"); await page.wait_for_load_state("networkidle")
        print("Login OK, navegando para RCTRC...")
        await page.goto(f"{BASE}/AverbacaoNacional/AverbacaoRCTRC"); await page.wait_for_load_state("networkidle")
        await page.select_option("#c_org_prd","1"); await page.wait_for_timeout(1500)
        await page.evaluate("()=>{const s=document.querySelector('#u_apo_pnc');s.value='10';s.dispatchEvent(new Event('change',{bubbles:true}));}")
        await page.wait_for_load_state("networkidle"); await page.wait_for_timeout(1500)
        await page.select_option("#u_sgp","1"); await page.wait_for_timeout(600)
        await page.select_option("#e_doc_ebq","C"); await page.wait_for_timeout(500)

        await close_all(page)
        print("Abrindo modal mercadoria...")
        await page.locator("#btModalMercadoria").click(force=True)
        await page.wait_for_selector("#mdlMercadoria.in", timeout=10000)
        await page.wait_for_timeout(1000)
        await page.screenshot(path=str(OUT/"mdr2_01_modal_aberto.png"))
        print("Modal aberto.")

        # Tentar busca por código vazio (lista tudo) e por termos variados
        for termo, campo in [("", "txtNome"), ("1", "txtCodigo"), ("10", "txtCodigo"), ("CARGA", "txtNome"), ("ELETR", "txtNome"), ("ALIM", "txtNome")]:
            print(f"\nBuscando campo={campo} termo='{termo}'...")
            await page.fill("#txtCodigo", "")
            await page.fill("#txtNome", "")
            if termo:
                await page.fill(f"#{campo}", termo)
            await page.wait_for_timeout(300)
            await page.click("#btnPesquisarMercadoria", force=True)
            await page.wait_for_timeout(3000)
            await page.screenshot(path=str(OUT/f"mdr2_busca_{campo}_{termo or 'vazio'}.png"))

            result = await page.evaluate("""
                () => {
                    const m = document.querySelector('#mdlMercadoria');
                    const rows = Array.from(m.querySelectorAll('table tr, tbody tr'));
                    const body = m.innerText.replace(/\\s+/g,' ').substring(0,500);
                    return {
                        body,
                        row_count: rows.length,
                        rows: rows.slice(0,8).map(r => ({
                            text: r.innerText.replace(/\\t|\\n/g,' ').trim().substring(0,80),
                            links: Array.from(r.querySelectorAll('a,[onclick]')).map(a => ({
                                t: a.textContent.trim().substring(0,30),
                                oc: (a.getAttribute('onclick')||'').substring(0,100)
                            }))
                        }))
                    };
                }
            """)
            print(f"  Body: {result['body'][:300]}")
            print(f"  Rows ({result['row_count']}):")
            for r in result['rows']:
                if r['text'] and r['text'] not in ('Código Nome', ''):
                    print(f"    {r['text']}")
                    for lnk in r['links']:
                        if lnk['oc']:
                            print(f"      onclick: {lnk['oc']}")

            # Se achou linhas com dados reais, selecionar o primeiro
            for r in result['rows']:
                for lnk in r['links']:
                    if lnk['oc'] and 'Codigo' not in lnk['t'] and r['text'] not in ('Código Nome', ''):
                        print(f"\n>>> Clicando: {lnk['oc']}")
                        await page.evaluate(f"()=>{{ {lnk['oc']} }}")
                        await page.wait_for_timeout(1200)
                        val = await page.evaluate("()=>({c:document.querySelector('#c_mdr_irb')?.value,t:document.querySelector('#t_mdr')?.value})")
                        print(f">>> Mercadoria preenchida: codigo={val['c']}, nome={val['t']}")
                        out_file = OUT / "map_mercadoria2.json"
                        out_file.write_text(json.dumps({"rows": result['rows'], "onclick": lnk['oc'], "codigo": val['c'], "nome": val['t']}, ensure_ascii=False, indent=2), encoding="utf-8")
                        await br.close()
                        return

        print("\nNenhum resultado encontrado em nenhuma busca.")
        await br.close()

asyncio.run(main())
