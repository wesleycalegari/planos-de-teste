"""
Percorre até 100 apólices para encontrar tipos A, M e com RCF (c_rmo_rfc != 0).
Salva os primeiros exemplares de cada tipo encontrado.
"""
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

BASE = "https://axa-hml-faturamento.nsseg.com.br/citnet"
OUT  = Path("c:/projetos/planos-de-teste/scripts/screenshots_rctrc")
OUT.mkdir(exist_ok=True)

async def main():
    async with async_playwright() as pw:
        br   = await pw.chromium.launch(headless=True)
        ctx  = await br.new_context(viewport={"width": 1366, "height": 768})
        page = await ctx.new_page()
        page.set_default_timeout(20000)

        await page.goto(f"{BASE}/")
        await page.fill("#usuario", "interno")
        await page.fill("#senha", "11")
        await page.click("#btLogin1")
        await page.wait_for_load_state("networkidle")

        await page.goto(f"{BASE}/AverbacaoNacional/AverbacaoRCTRC")
        await page.wait_for_load_state("networkidle")

        # Selecionar filial 1 (SP)
        await page.select_option("#c_org_prd", "1")
        await page.wait_for_timeout(1500)

        apolices = await page.evaluate("""
            () => Array.from(document.querySelector('#u_apo_pnc').options)
                .filter(o => o.value && o.value !== '0' && o.value !== '')
                .map(o => ({v: o.value, t: o.text.trim()}))
        """)
        print(f"Total de apolices: {len(apolices)}")

        # Tipos que queremos encontrar
        achados = {
            "D_sem_rcf": None,
            "D_com_rcf": None,
            "A":         None,
            "M":         None,
            "DDR_S":     None,
            "DDR_E":     None,
            "DDR_outro": None,
        }

        for apo in apolices[:150]:  # checar até 150
            await page.evaluate(f"""
                () => {{
                    const sel = document.querySelector('#u_apo_pnc');
                    sel.value = '{apo['v']}';
                    sel.dispatchEvent(new Event('change', {{bubbles: true}}));
                }}
            """)
            await page.wait_for_timeout(900)

            info = await page.evaluate("""
                () => ({
                    tipo:  document.querySelector('#hdTipoApolice')?.value || '',
                    rfc:   document.querySelector('#c_rmo_rfc')?.value || '0',
                    ddr:   document.querySelector('#permitirEstipulacaoDDR')?.value || '',
                    sgps: (() => {
                        const s = document.querySelector('#u_sgp');
                        return s ? Array.from(s.options)
                            .filter(o => o.value && o.value !== '0')
                            .map(o => ({v: o.value, t: o.text.trim()})) : [];
                    })()
                })
            """)
            t = info['tipo']
            rfc = info['rfc']
            ddr = info['ddr']

            entry = {"apolice": apo['v'], "texto": apo['t'],
                     "tipo": t, "rfc": rfc, "ddr": ddr,
                     "subgrupos": info['sgps']}

            if t == 'D' and rfc == '0' and not achados["D_sem_rcf"]:
                achados["D_sem_rcf"] = entry
            if t == 'D' and rfc != '0' and not achados["D_com_rcf"]:
                achados["D_com_rcf"] = entry
            if t == 'A' and not achados["A"]:
                achados["A"] = entry
            if t == 'M' and not achados["M"]:
                achados["M"] = entry
            if ddr == 'S' and not achados["DDR_S"]:
                achados["DDR_S"] = entry
            if ddr == 'E' and not achados["DDR_E"]:
                achados["DDR_E"] = entry
            if ddr not in ('', 'S', 'E') and not achados["DDR_outro"]:
                achados["DDR_outro"] = entry

            # Progresso
            achou = sum(1 for v in achados.values() if v)
            print(f"  {apo['v']:<20} T={t:<3} RFC={rfc:<8} DDR={ddr:<3} | achados: {achou}/7")

            if all(v for v in achados.values()):
                print("Todos os tipos encontrados!")
                break

        print("\n=== RESULTADO FINAL ===")
        for tipo, info in achados.items():
            if info:
                sgp_1 = info['subgrupos'][0]['v'] if info['subgrupos'] else 'N/A'
                print(f"  {tipo:<12}: apolice={info['apolice']:<20} "
                      f"tipo={info['tipo']:<3} rfc={info['rfc']:<10} "
                      f"ddr={info['ddr']:<3} sgp1={sgp_1}")
            else:
                print(f"  {tipo:<12}: NAO ENCONTRADO")

        out = OUT / "map_tipos.json"
        out.write_text(json.dumps(achados, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON: {out}")
        await br.close()

asyncio.run(main())
