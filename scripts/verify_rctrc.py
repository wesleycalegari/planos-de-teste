"""
Script de verificação do formulário RCTRC no CITNET2 HML.
Navega até Averbação Nacional → RCTR-C e captura screenshots + HTML para
confirmar IDs de campo, comportamento condicional e mensagens de validação.
"""
import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "https://axa-hml-faturamento.nsseg.com.br/citnet"
LOGIN_USER = "interno"
LOGIN_PASS = "11"
OUT_DIR = Path("c:/projetos/planos-de-teste/scripts/screenshots_rctrc")
OUT_DIR.mkdir(exist_ok=True)

LOG = []

def log(msg):
    print(msg)
    LOG.append(msg)


async def ss(page, name, desc=""):
    path = OUT_DIR / f"{name}.png"
    await page.screenshot(path=str(path), full_page=False)
    log(f"  [screenshot] {name}.png — {desc}")


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=300)
        ctx = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await ctx.new_page()
        page.set_default_timeout(30000)

        # ── 1. LOGIN ──────────────────────────────────────────────────────
        log("\n=== 1. LOGIN ===")
        await page.goto(f"{BASE_URL}/")
        await ss(page, "01_login_page", "Tela de login")

        # Tenta localizar campos de login
        user_sel = await _find_selector(page, [
            "#usuario", "#txtLogin", "input[name='usuario']", "input[type='text']"
        ])
        pass_sel = await _find_selector(page, [
            "#senha", "#txtSenha", "input[name='senha']", "input[type='password']"
        ])
        btn_sel  = await _find_selector(page, [
            "#btLogin1", "#btEntrar", "input[type='submit']", "button[type='submit']"
        ])

        log(f"  Campo usuário: {user_sel}")
        log(f"  Campo senha:   {pass_sel}")
        log(f"  Botão entrar:  {btn_sel}")

        if user_sel:
            await page.fill(user_sel, LOGIN_USER)
        if pass_sel:
            await page.fill(pass_sel, LOGIN_PASS)
        if btn_sel:
            await page.click(btn_sel)
            await page.wait_for_load_state("networkidle", timeout=15000)

        await ss(page, "02_after_login", "Após login")
        log(f"  URL após login: {page.url}")

        # ── 2. MENU — verificar estrutura de navegação ────────────────────
        log("\n=== 2. MENU PRINCIPAL ===")
        menu_html = await page.inner_html("body")
        # Buscar links de menu que contenham "Averba"
        menu_links = await page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a, li, .menu-item'));
                return links
                    .filter(el => /averba|rctrc|nacional/i.test(el.textContent))
                    .map(el => ({tag: el.tagName, text: el.textContent.trim().substring(0,60), href: el.href || ''}));
            }
        """)
        log(f"  Links de menu relacionados a Averbação/RCTRC: {json.dumps(menu_links, ensure_ascii=False, indent=2)}")
        await ss(page, "03_menu", "Menu principal com Averbação Nacional")

        # ── 3. NAVEGAR PARA RCTRC ─────────────────────────────────────────
        log("\n=== 3. NAVEGAÇÃO RCTRC ===")

        # Tentar ir diretamente pela URL
        await page.goto(f"{BASE_URL}/AverbacaoNacional/AverbacaoRCTRC")
        await page.wait_for_load_state("networkidle", timeout=15000)
        await ss(page, "04_rctrc_form", "Formulário AverbacaoRCTRC — estado inicial")
        log(f"  URL: {page.url}")

        # ── 4. INSPECIONAR CAMPOS DO FORMULÁRIO ───────────────────────────
        log("\n=== 4. CAMPOS DO FORMULÁRIO ===")
        fields = await page.evaluate("""
            () => {
                const form = document.querySelector('#frmAvb') || document.querySelector('form');
                if (!form) return {error: 'form #frmAvb não encontrado'};
                const inputs = Array.from(form.querySelectorAll('input, select, textarea, button'));
                return inputs.map(el => ({
                    id: el.id,
                    name: el.name,
                    type: el.type || el.tagName.toLowerCase(),
                    visible: el.offsetParent !== null,
                    disabled: el.disabled,
                    value: el.value ? el.value.substring(0, 20) : '',
                    label: (() => {
                        let lbl = document.querySelector('label[for="' + el.id + '"]');
                        if (!lbl) lbl = el.closest('.form-group')?.querySelector('label');
                        return lbl ? lbl.textContent.trim().substring(0, 50) : '';
                    })()
                }));
            }
        """)
        log(f"  Campos encontrados no #frmAvb: {json.dumps(fields, ensure_ascii=False, indent=2)}")

        # ── 5. VERIFICAR CAMPO e_doc_ebq (tipo documento) ─────────────────
        log("\n=== 5. DROPDOWN e_doc_ebq ===")
        doc_opts = await page.evaluate("""
            () => {
                const sel = document.querySelector('#e_doc_ebq');
                if (!sel) return {error: '#e_doc_ebq não encontrado'};
                return {
                    id: sel.id,
                    visible: sel.offsetParent !== null,
                    options: Array.from(sel.options).map(o => ({value: o.value, text: o.text}))
                };
            }
        """)
        log(f"  #e_doc_ebq: {json.dumps(doc_opts, ensure_ascii=False)}")

        # ── 6. TESTAR MUDANÇA TIPO DOCUMENTO: C → visibilidade ────────────
        log("\n=== 6. VISIBILIDADE CONDICIONAL ===")
        if "#e_doc_ebq" in str(fields):
            # Selecionar CTE
            try:
                await page.select_option("#e_doc_ebq", "C")
                await page.wait_for_timeout(800)
                vis_cte = await page.evaluate("""
                    () => ({
                        documentoCte_visible: document.querySelector('#documentoCte')?.offsetParent !== null,
                        documentoOutros_visible: document.querySelector('#documentoOutros')?.offsetParent !== null,
                        u_cnh_elt_visible: document.querySelector('#u_cnh_elt')?.offsetParent !== null,
                        pnlCte_visible: document.querySelector('#pnlCte')?.offsetParent !== null,
                    })
                """)
                log(f"  Com e_doc_ebq=C: {json.dumps(vis_cte)}")
                await ss(page, "05_tipo_cte", "Formulário com tipo CTE selecionado")

                # Selecionar Outros
                await page.select_option("#e_doc_ebq", "O")
                await page.wait_for_timeout(800)
                vis_out = await page.evaluate("""
                    () => ({
                        documentoCte_visible: document.querySelector('#documentoCte')?.offsetParent !== null,
                        documentoOutros_visible: document.querySelector('#documentoOutros')?.offsetParent !== null,
                        u_ser_doc2_visible: document.querySelector('#u_ser_doc2')?.offsetParent !== null,
                        u_doc_ini2_visible: document.querySelector('#u_doc_ini2')?.offsetParent !== null,
                    })
                """)
                log(f"  Com e_doc_ebq=O: {json.dumps(vis_out)}")
                await ss(page, "06_tipo_outros", "Formulário com tipo Outros selecionado")
            except Exception as e:
                log(f"  AVISO: erro ao testar tipo documento — {e}")

        # ── 7. INSPECIONAR SEÇÃO DE ADICIONAIS ────────────────────────────
        log("\n=== 7. CHECKBOXES DE ADICIONAIS ===")
        adicionais = await page.evaluate("""
            () => {
                const ids = [
                    '#i_tar_dsc_bnf_itn', '#i_tar_adl_ocd', '#i_tar_adl_ica',
                    '#i_tar_adl_avr', '#i_tar_adl_pmf', '#i_tar_adl_lbr_pst',
                    '#i_tar_adl_rbo_prl_rcf', '#i_tar_adl_rbo_dpt_rcf', '#i_mov_itn'
                ];
                return ids.map(id => {
                    const el = document.querySelector(id);
                    if (!el) return {id, found: false};
                    return {
                        id,
                        found: true,
                        visible: el.offsetParent !== null,
                        disabled: el.disabled,
                        type: el.type
                    };
                });
            }
        """)
        log(f"  Adicionais: {json.dumps(adicionais, ensure_ascii=False, indent=2)}")

        # ── 8. INSPECIONAR SEÇÃO VALORES ──────────────────────────────────
        log("\n=== 8. CAMPOS DE VALOR ===")
        valores = await page.evaluate("""
            () => {
                const ids = [
                    '#v_is', '#v_is_cnn', '#v_fte', '#v_cml_pmo_vgm',
                    '#v_is_rcf', '#v_is_cnn_rcf', '#v_fte_rcf', '#v_cml_pmo_rcf'
                ];
                return ids.map(id => {
                    const el = document.querySelector(id);
                    if (!el) return {id, found: false};
                    return {id, found: true, disabled: el.disabled, visible: el.offsetParent !== null};
                });
            }
        """)
        log(f"  Campos de valor: {json.dumps(valores, ensure_ascii=False, indent=2)}")

        # ── 9. VERIFICAR EXISTÊNCIA DO BOTÃO E FORM ───────────────────────
        log("\n=== 9. BOTÃO ENVIAR E PROTOCOLO ===")
        btn_info = await page.evaluate("""
            () => {
                const btn = document.querySelector('#btEnviar');
                const pcl = document.querySelector('#u_pcl');
                return {
                    btEnviar_found: !!btn,
                    btEnviar_text: btn?.textContent?.trim(),
                    u_pcl_found: !!pcl,
                    frmAvb_found: !!document.querySelector('#frmAvb'),
                };
            }
        """)
        log(f"  Botão e form: {json.dumps(btn_info)}")

        # ── 10. TENTAR GRAVAR SEM DADOS — ver validação JS ─────────────────
        log("\n=== 10. VALIDAÇÃO JS — gravar sem dados ===")
        try:
            await page.click("#btEnviar")
            await page.wait_for_timeout(1500)
            page_text = await page.inner_text("body")
            # Capturar alert ou mensagem
            await ss(page, "07_gravar_sem_dados", "Tentativa de gravar sem dados — validação JS")
            # Verificar mensagens de erro visíveis
            msg_erros = await page.evaluate("""
                () => {
                    const els = document.querySelectorAll('.alert, .error, .msg-erro, [class*="error"], [class*="erro"]');
                    return Array.from(els).filter(e => e.offsetParent !== null)
                        .map(e => e.textContent.trim().substring(0, 100));
                }
            """)
            log(f"  Mensagens de erro visíveis: {msg_erros}")
        except Exception as e:
            log(f"  AVISO ao testar validação JS: {e}")

        # ── 11. CAPTURAR HTML COMPLETO DA SEÇÃO DE ADICIONAIS ────────────
        log("\n=== 11. HTML — seção adicionais ===")
        try:
            adl_html = await page.evaluate("""
                () => {
                    const el = document.querySelector('#mostraReferencial') || document.querySelector('.adicionais');
                    return el ? el.innerHTML.substring(0, 2000) : 'seção #mostraReferencial não encontrada';
                }
            """)
            log(f"  HTML adicionais RCTR-C: {adl_html[:500]}")

            rcf_html = await page.evaluate("""
                () => {
                    const el = document.querySelector('#mostraReferencialRcf') || document.querySelector('.adicionais-rcf');
                    return el ? el.innerHTML.substring(0, 1000) : 'seção #mostraReferencialRcf não encontrada';
                }
            """)
            log(f"  HTML adicionais RC-DC: {rcf_html[:300]}")
        except Exception as e:
            log(f"  AVISO: {e}")

        # ── SALVAR LOG ────────────────────────────────────────────────────
        log_path = OUT_DIR / "verification_log.txt"
        log_path.write_text("\n".join(LOG), encoding="utf-8")
        log(f"\n=== FIM. Log salvo em: {log_path} ===")

        await browser.close()


async def _find_selector(page, selectors):
    for sel in selectors:
        try:
            el = await page.query_selector(sel)
            if el:
                return sel
        except Exception:
            pass
    return None


if __name__ == "__main__":
    asyncio.run(main())
