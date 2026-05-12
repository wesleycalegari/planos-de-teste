import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

BASE = "https://axa-hml-faturamento.nsseg.com.br/citnet"
OUT  = Path("c:/projetos/planos-de-teste/scripts/screenshots_rctrc")

async def close_all(page):
    await page.evaluate("""
        () => { document.querySelectorAll('.modal.in,.modal-backdrop').forEach(m=>{
            m.classList.remove('in'); m.style.display='none';});
            document.body.classList.remove('modal-open'); }
    """)
    await page.wait_for_timeout(300)

async def main():
    async with async_playwright() as pw:
        br   = await pw.chromium.launch(headless=True)
        page = await (await br.new_context(viewport={"width":1366,"height":768})).new_page()
        page.set_default_timeout(25000)

        await page.goto(f"{BASE}/"); await page.fill("#usuario","interno"); await page.fill("#senha","11"); await page.click("#btLogin1"); await page.wait_for_load_state("networkidle")
        await page.goto(f"{BASE}/AverbacaoNacional/AverbacaoRCTRC"); await page.wait_for_load_state("networkidle")
        await page.select_option("#c_org_prd","1"); await page.wait_for_timeout(1200)
        await page.evaluate("()=>{const s=document.querySelector('#u_apo_pnc');s.value='10';s.dispatchEvent(new Event('change',{bubbles:true}));}")
        await page.wait_for_load_state("networkidle"); await page.wait_for_timeout(1200)
        await page.select_option("#u_sgp","1"); await page.wait_for_timeout(500)
        await page.select_option("#e_doc_ebq","C"); await page.wait_for_timeout(400)

        await close_all(page)
        await page.locator("#btModalMercadoria").click(force=True)
        await page.wait_for_selector("#mdlMercadoria.in", timeout=8000)
        await page.wait_for_timeout(600)

        # Buscar por código "1" — deve retornar primeiros registros
        for termo in ["1", "CARGA", "CEREAIS", "OLEO", "PAPEL"]:
            await page.fill("#txtNome", ""); await page.fill("#txtCodigo", "")
            await page.fill("#txtNome", termo)
            await page.click("#btnPesquisarMercadoria", force=True)
            await page.wait_for_timeout(1800)
            rows = await page.evaluate("""
                () => Array.from(document.querySelector('#mdlMercadoria').querySelectorAll('tr')).slice(0,8)
                    .map(r=>({text:r.innerText.replace(/\\t|\\n/g,' ').trim().substring(0,80),
                              links:Array.from(r.querySelectorAll('a,[onclick]'))
                                  .map(a=>({t:a.textContent.trim().substring(0,30),
                                            oc:(a.getAttribute('onclick')||'').substring(0,80)})) }))
            """)
            print(f"Busca '{termo}':")
            has_data = False
            for r in rows:
                if r['text'] and r['text'] not in ('', 'Código Nome'):
                    print(f"  {r['text']}")
                    for lnk in r['links']:
                        if lnk['oc']: print(f"    onclick={lnk['oc']}")
                    has_data = True
            if has_data:
                # Clicar no primeiro resultado e capturar código
                for r in rows:
                    for lnk in r['links']:
                        if lnk['oc']:
                            await page.evaluate(f"()=>{{ {lnk['oc']} }}")
                            await page.wait_for_timeout(800)
                            val = await page.evaluate("()=>({c:document.querySelector('#c_mdr_irb')?.value,t:document.querySelector('#t_mdr')?.value})")
                            print(f"  >> Mercadoria preenchida: codigo={val['c']}, nome={val['t']}")
                            (OUT/"map_mercadoria.json").write_text(json.dumps({"rows":rows,"onclick_sample":lnk['oc'],"codigo":val['c'],"nome":val['t']}, ensure_ascii=False, indent=2), encoding="utf-8")
                            await br.close(); return
                break
            await page.fill("#txtNome","")

        await br.close()

asyncio.run(main())
