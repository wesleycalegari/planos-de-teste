"""
Captura todos os campos, checkboxes e botões visíveis do form RCTRC após seleção da apólice.
"""
import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

BASE = "https://axa-hml-faturamento.nsseg.com.br/citnet"
OUT  = Path("c:/projetos/planos-de-teste/scripts/screenshots_rctrc")

async def main():
    async with async_playwright() as pw:
        br   = await pw.chromium.launch(headless=True)
        page = await (await br.new_context(viewport={"width":1366,"height":900})).new_page()
        page.set_default_timeout(25000)

        await page.goto(f"{BASE}/"); await page.fill("#usuario","interno"); await page.fill("#senha","11"); await page.click("#btLogin1"); await page.wait_for_load_state("networkidle")
        await page.goto(f"{BASE}/AverbacaoNacional/AverbacaoRCTRC"); await page.wait_for_load_state("networkidle")
        await page.select_option("#c_org_prd","1"); await page.wait_for_timeout(1500)
        await page.evaluate("()=>{const s=document.querySelector('#u_apo_pnc');s.value='10';s.dispatchEvent(new Event('change',{bubbles:true}));}")
        await page.wait_for_load_state("networkidle"); await page.wait_for_timeout(1500)
        await page.select_option("#u_sgp","1"); await page.wait_for_timeout(600)
        await page.select_option("#e_doc_ebq","C"); await page.wait_for_timeout(500)

        result = await page.evaluate("""
            () => {
                const form = document.querySelector('#frmAvb') || document.body;

                // Todos os inputs/selects/textareas
                const fields = Array.from(form.querySelectorAll('input, select, textarea')).map(el => ({
                    tag:      el.tagName,
                    id:       el.id,
                    name:     el.name,
                    type:     el.type,
                    value:    el.value ? el.value.substring(0,30) : '',
                    visible:  el.offsetParent !== null,
                    disabled: el.disabled,
                    checked:  el.type === 'checkbox' ? el.checked : undefined,
                    label:    (() => {
                        // procurar label próximo
                        const lbl = document.querySelector(`label[for="${el.id}"]`);
                        if (lbl) return lbl.textContent.trim().substring(0,40);
                        if (el.closest('label')) return el.closest('label').textContent.trim().substring(0,40);
                        if (el.closest('div')) {
                            const txt = el.closest('div').textContent.trim().substring(0,40);
                            return txt;
                        }
                        return '';
                    })()
                }));

                // Todos os botões visíveis
                const buttons = Array.from(form.querySelectorAll('button, a.btn, input[type=button], input[type=submit]'))
                    .filter(b => b.offsetParent !== null || b.closest('.btn-group'))
                    .map(b => ({
                        tag:      b.tagName,
                        id:       b.id,
                        text:     b.textContent.trim().substring(0,40),
                        disabled: b.disabled || b.classList.contains('disabled'),
                        href:     b.href || '',
                        onclick:  (b.getAttribute('onclick')||'').substring(0,60)
                    }));

                // HTML dos divs principais para entender a estrutura
                const paneis = Array.from(document.querySelectorAll('[id^="pnl"], [id^="div"], [id*="Panel"], [id*="painel"], [id*="Painel"]'))
                    .filter(el => el.id)
                    .map(el => ({
                        id:      el.id,
                        visible: el.offsetParent !== null,
                        display: window.getComputedStyle(el).display,
                        text:    el.textContent.trim().substring(0,60)
                    }));

                return { fields, buttons, paneis };
            }
        """)

        print("=== TODOS OS CAMPOS DO FORM (#frmAvb) ===")
        print(f"\n{'ID':<30} {'TYPE':<12} {'VISIBLE':<8} {'DISABLED':<10} {'LABEL'}")
        print("-"*100)
        for f in result['fields']:
            if f['id'] or f['name']:
                vis = 'SIM' if f['visible'] else 'não'
                dis = 'SIM' if f['disabled'] else ''
                chk = f' checked={f["checked"]}' if f['checked'] is not None else ''
                print(f"{f['id'] or f['name']:<30} {f['type']:<12} {vis:<8} {dis:<10} {f['label'][:40]}{chk}")

        print("\n\n=== BOTÕES VISÍVEIS ===")
        for b in result['buttons']:
            print(f"  [{b['id']}] '{b['text']}' disabled={b['disabled']}")

        print("\n\n=== PAINÉIS/DIVS COM ID ===")
        for p in result['paneis']:
            vis = 'VISÍVEL' if p['visible'] else 'OCULTO '
            print(f"  [{vis}] #{p['id']} | {p['text'][:50]}")

        OUT.mkdir(exist_ok=True)
        (OUT/"form_full_inspect.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nSalvo em form_full_inspect.json")
        await br.close()

asyncio.run(main())
