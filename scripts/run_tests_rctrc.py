"""
Execução automatizada dos CTs do plano RCTRC.
Valida os cenários diretamente no HML AXA via Playwright.
"""
import asyncio, json
from pathlib import Path
from datetime import date

BASE = "https://axa-hml-faturamento.nsseg.com.br/citnet"
OUT  = Path("c:/projetos/planos-de-teste/scripts/screenshots_rctrc/tests")
OUT.mkdir(exist_ok=True)

RESULTADOS = []

def ok(ct, desc):
    RESULTADOS.append({"ct": ct, "status": "PASSOU", "desc": desc})
    print(f"  [PASSOU] {ct}: {desc}")

def fail(ct, desc, detail=""):
    RESULTADOS.append({"ct": ct, "status": "FALHOU", "desc": desc, "detalhe": detail})
    print(f"  [FALHOU] {ct}: {desc}" + (f" — {detail}" if detail else ""))

def skip(ct, desc):
    RESULTADOS.append({"ct": ct, "status": "BLOQUEADO", "desc": desc})
    print(f"  [BLOQ]   {ct}: {desc}")


async def login(page):
    await page.goto(f"{BASE}/", wait_until="domcontentloaded")
    await page.wait_for_selector("#usuario", timeout=30000)
    await page.fill("#usuario", "interno")
    await page.fill("#senha", "11")
    await page.click("#btLogin1")
    await page.wait_for_load_state("networkidle")


async def goto_rctrc(page):
    await page.goto(f"{BASE}/AverbacaoNacional/AverbacaoRCTRC")
    await page.wait_for_load_state("networkidle")


async def selecionar_apolice(page, filial="1", apo="10", sgp="1", doc="C"):
    await page.select_option("#c_org_prd", filial)
    await page.wait_for_timeout(1500)
    await page.evaluate(f"""()=>{{
        const s=document.querySelector('#u_apo_pnc');
        s.value='{apo}';
        s.dispatchEvent(new Event('change',{{bubbles:true}}));
    }}""")
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(1500)
    await page.select_option("#u_sgp", sgp)
    await page.wait_for_timeout(500)
    if doc:
        await page.select_option("#e_doc_ebq", doc)
        await page.wait_for_timeout(400)


async def preencher_form_basico(page):
    """Preenche campos obrigatórios para uma gravação válida (CTE)."""
    hoje = date.today().strftime("%d/%m/%Y")
    # Chave CTE 44 dígitos
    await page.fill("#u_cnh_elt", "44444444444444444444444444444444444444444444")
    # Data saída = hoje
    await page.fill("#d_sda_vgm", hoje)
    # Placa
    await page.fill("#t_vei_tpr", "ABC1234")
    # Meio transporte T
    await page.select_option("#e_tr1", "T")
    await page.wait_for_timeout(300)
    # UF origem + município (injeção direta)
    await page.select_option("#n_ori", "SP")
    await page.wait_for_timeout(400)
    await page.evaluate("""()=>{
        document.querySelector('#c_cdd_ori').value='34401';
        document.querySelector('#t_cdd_ori').value='Osasco';
        document.querySelector('#c_cdd_ori').dispatchEvent(new Event('change',{bubbles:true}));
    }""")
    # UF destino + município
    await page.select_option("#n_dst", "RJ")
    await page.wait_for_timeout(400)
    await page.evaluate("""()=>{
        document.querySelector('#c_cdd_dst').value='32100';
        document.querySelector('#t_cdd_dst').value='Rio de Janeiro';
        document.querySelector('#c_cdd_dst').dispatchEvent(new Event('change',{bubbles:true}));
    }""")
    # Mercadoria (injeção direta)
    await page.evaluate("""()=>{
        document.querySelector('#c_mdr_irb').value='0000000001';
        document.querySelector('#t_mdr').value='DIVERSAS';
    }""")
    # IS RCTR-C
    await page.fill("#v_is", "10000")
    await page.wait_for_timeout(300)


async def close_all(page):
    await page.evaluate("""()=>{
        document.querySelectorAll('.modal.in,.modal-backdrop').forEach(m=>{
            m.classList.remove('in'); m.style.display='none';
        });
        document.body.classList.remove('modal-open');
    }""")
    await page.wait_for_timeout(300)


async def gravar(page):
    async with page.expect_response(
        lambda r: "/AverbacaoNacional/Gravar" in r.url and r.request.method == "POST",
        timeout=20000
    ) as resp_info:
        await page.click("#btEnviar")
    resp = await resp_info.value
    body = await resp.json()
    return body


async def main():
    from playwright.async_api import async_playwright

    async with async_playwright() as pw:
        br = await pw.chromium.launch(headless=True)
        ctx = await br.new_context(viewport={"width": 1366, "height": 900})
        page = await ctx.new_page()
        page.set_default_timeout(25000)

        print("\n=== Login ===")
        await login(page)
        print("  Login OK")

        # -----------------------------------------------
        print("\n=== CT-RCT-001: Carregamento do formulário ===")
        await goto_rctrc(page)
        try:
            # Verificar filial dropdown
            filiais = await page.evaluate("()=>document.querySelectorAll('#c_org_prd option').length")
            ufs = await page.evaluate("()=>document.querySelectorAll('#n_ori option').length")
            v_is = await page.evaluate("()=>document.querySelector('#v_is')?.value")
            btEnviar_dis = await page.evaluate("()=>document.querySelector('#btEnviar')?.disabled")
            await page.screenshot(path=str(OUT/"ct001_formulario.png"))

            assert filiais > 1, f"Filiais: {filiais}"
            assert ufs > 1, f"UFs: {ufs}"
            assert btEnviar_dis == True, f"btEnviar não está disabled"
            ok("CT-001", f"Formulário carregado: {filiais} filiais, {ufs} UFs, btEnviar=disabled")
        except Exception as e:
            fail("CT-001", "Erro no carregamento", str(e))

        # -----------------------------------------------
        print("\n=== CT-RCT-002: Carregamento de subgrupo ===")
        await goto_rctrc(page)
        try:
            await page.select_option("#c_org_prd", "1")
            await page.wait_for_timeout(1500)
            await page.evaluate("""()=>{
                const s=document.querySelector('#u_apo_pnc');
                s.value='10';
                s.dispatchEvent(new Event('change',{bubbles:true}));
            }""")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(1500)

            sgps = await page.evaluate("()=>document.querySelectorAll('#u_sgp option').length")
            tipo = await page.evaluate("()=>document.querySelector('#hdTipoApolice')?.value")
            btEnviar_dis = await page.evaluate("()=>document.querySelector('#btEnviar')?.disabled")
            await page.screenshot(path=str(OUT/"ct002_subgrupo.png"))

            assert sgps > 1, f"SGPs: {sgps}"
            ok("CT-002", f"Subgrupo carregado: {sgps} opções, hdTipoApolice={tipo}, btEnviar.disabled={btEnviar_dis}")
        except Exception as e:
            fail("CT-002", "Erro no carregamento de subgrupo", str(e))

        # -----------------------------------------------
        print("\n=== CT-RCT-003: Tipo CTE ===")
        try:
            await page.select_option("#u_sgp", "1")
            await page.wait_for_timeout(500)
            await page.select_option("#e_doc_ebq", "C")
            await page.wait_for_timeout(600)

            cte_visible = await page.evaluate("()=>document.querySelector('#u_cnh_elt')?.offsetParent !== null")
            outros_visible = await page.evaluate("()=>document.querySelector('#documentoOutros')?.style.display !== 'none'")
            await page.screenshot(path=str(OUT/"ct003_tipo_cte.png"))

            assert cte_visible, "#u_cnh_elt não visível"
            ok("CT-003", f"CTE selecionado: #u_cnh_elt visível={cte_visible}, #documentoOutros={outros_visible}")
        except Exception as e:
            fail("CT-003", "Erro ao selecionar tipo CTE", str(e))

        # -----------------------------------------------
        print("\n=== CT-RCT-004: Tipo Outros ===")
        try:
            await page.select_option("#e_doc_ebq", "O")
            await page.wait_for_timeout(600)

            serie_visible = await page.evaluate("()=>document.querySelector('#u_ser_doc2')?.offsetParent !== null")
            cte_visible = await page.evaluate("()=>document.querySelector('#u_cnh_elt')?.offsetParent !== null")
            await page.screenshot(path=str(OUT/"ct004_tipo_outros.png"))

            assert serie_visible, "#u_ser_doc2 não visível"
            assert not cte_visible, "#u_cnh_elt ainda visível"
            ok("CT-004", f"Outros selecionado: #u_ser_doc2 visível={serie_visible}, #u_cnh_elt visível={cte_visible}")
        except Exception as e:
            fail("CT-004", "Erro ao selecionar tipo Outros", str(e))

        # -----------------------------------------------
        print("\n=== CT-RCT-005: Happy path — gravação CTE ===")
        await goto_rctrc(page)
        await close_all(page)
        protocolo_ct005 = None
        try:
            await selecionar_apolice(page, "1", "10", "1", "C")
            await preencher_form_basico(page)
            await page.screenshot(path=str(OUT/"ct005_antes_gravar.png"))

            body = await gravar(page)
            partes = (body.get("lista") or "").split("|")
            status = partes[0] if partes else ""
            protocolo = partes[1] if len(partes) > 1 else ""
            await page.screenshot(path=str(OUT/"ct005_apos_gravar.png"))

            assert body.get("codigo") == 0, f"codigo={body.get('codigo')}"
            assert status == "OK", f"status={status}, lista={body.get('lista')}"
            protocolo_ct005 = protocolo
            ok("CT-005", f"Gravação OK: protocolo={protocolo}, lista={body.get('lista')}")
        except Exception as e:
            fail("CT-005", "Erro na gravação happy path", str(e))
            await page.screenshot(path=str(OUT/"ct005_erro.png"))

        # -----------------------------------------------
        print("\n=== CT-RCT-006: RCF vinculado — apólice 224466 ===")
        await goto_rctrc(page)
        await close_all(page)
        try:
            await selecionar_apolice(page, "1", "224466", "1", "C")
            await preencher_form_basico(page)
            # Verificar que campo RC-DC está visível
            rcf_visible = await page.evaluate("()=>document.querySelector('#v_is_rcf')?.offsetParent !== null")
            await page.fill("#v_is_rcf", "5000")
            await page.wait_for_timeout(300)
            await page.screenshot(path=str(OUT/"ct006_rcf_preenchido.png"))

            body = await gravar(page)
            partes = (body.get("lista") or "").split("|")
            status = partes[0] if partes else ""
            await page.screenshot(path=str(OUT/"ct006_apos_gravar.png"))

            assert body.get("codigo") == 0, f"codigo={body.get('codigo')}"
            assert status == "OK", f"status={status}, lista={body.get('lista')}"
            ok("CT-006", f"Gravação RCF OK: rcf_visible={rcf_visible}, lista={body.get('lista')}")
        except Exception as e:
            fail("CT-006", "Erro na gravação com RCF", str(e))
            await page.screenshot(path=str(OUT/"ct006_erro.png"))

        # -----------------------------------------------
        print("\n=== CT-RCT-010: OCD + OCD/Içamento simultâneos ===")
        await goto_rctrc(page)
        await close_all(page)
        try:
            await selecionar_apolice(page, "1", "10", "1", "C")
            await preencher_form_basico(page)
            # Verificar visibilidade dos adicionais
            ocd_visible = await page.evaluate("()=>document.querySelector('#i_tar_adl_ocd')?.offsetParent !== null")
            ica_visible = await page.evaluate("()=>document.querySelector('#i_tar_adl_ica')?.offsetParent !== null")
            assert ocd_visible and ica_visible, f"Checkboxes: ocd={ocd_visible}, ica={ica_visible}"
            # Marcar ambos
            await page.evaluate("""()=>{
                document.querySelector('#i_tar_adl_ocd').checked = true;
                document.querySelector('#i_tar_adl_ica').checked = true;
            }""")
            await page.screenshot(path=str(OUT/"ct010_ambos_marcados.png"))

            body = await gravar(page)
            lista = body.get("lista") or ""
            await page.screenshot(path=str(OUT/"ct010_apos_gravar.png"))

            # Deve retornar erro de negócio
            assert body.get("codigo") == 0
            assert lista.startswith("Erro|") or "simultaneamente" in lista.lower() or "OCD" in lista, \
                f"Esperado bloqueio OCD, obteve: {lista}"
            ok("CT-010", f"Bloqueio OCD confirmado: {lista[:80]}")
        except Exception as e:
            fail("CT-010", "Erro no teste OCD+ICA", str(e))
            await page.screenshot(path=str(OUT/"ct010_erro.png"))

        # -----------------------------------------------
        print("\n=== CT-RCT-014: VS vazio — bloqueio ===")
        await goto_rctrc(page)
        await close_all(page)
        try:
            await selecionar_apolice(page, "1", "10", "1", "C")
            await preencher_form_basico(page)
            # Zerar IS
            await page.fill("#v_is", "0")
            await page.fill("#v_is_cnn", "0") if await page.evaluate("()=>!!document.querySelector('#v_is_cnn')") else None
            await page.wait_for_timeout(300)
            await page.screenshot(path=str(OUT/"ct014_is_vazio.png"))

            body = await gravar(page)
            lista = body.get("lista") or ""
            await page.screenshot(path=str(OUT/"ct014_apos_gravar.png"))

            assert body.get("codigo") == 0
            assert lista.startswith("Erro|") or "Valor Segurado" in lista, f"Esperado bloqueio IS, obteve: {lista}"
            ok("CT-014", f"Bloqueio IS vazio confirmado: {lista[:80]}")
        except Exception as e:
            fail("CT-014", "Erro no teste IS vazio", str(e))
            await page.screenshot(path=str(OUT/"ct014_erro.png"))

        # -----------------------------------------------
        print("\n=== CT-RCT-016: Data saída anterior — bloqueio CTE ===")
        await goto_rctrc(page)
        await close_all(page)
        try:
            await selecionar_apolice(page, "1", "10", "1", "C")
            await preencher_form_basico(page)
            # Data anterior: usar 01/01/2020
            await page.fill("#d_sda_vgm", "01/01/2020")
            await page.wait_for_timeout(300)
            await page.screenshot(path=str(OUT/"ct016_data_anterior.png"))

            body = await gravar(page)
            lista = body.get("lista") or ""
            await page.screenshot(path=str(OUT/"ct016_apos_gravar.png"))

            assert body.get("codigo") == 0
            assert lista.startswith("Erro|") or "data" in lista.lower() or "saida" in lista.lower(), \
                f"Esperado bloqueio data, obteve: {lista}"
            ok("CT-016", f"Bloqueio data anterior confirmado: {lista[:80]}")
        except Exception as e:
            fail("CT-016", "Erro no teste data anterior", str(e))
            await page.screenshot(path=str(OUT/"ct016_erro.png"))

        # -----------------------------------------------
        print("\n=== CT-RCT-017: Município origem ausente — bloqueio ===")
        await goto_rctrc(page)
        await close_all(page)
        try:
            await selecionar_apolice(page, "1", "10", "1", "C")
            await preencher_form_basico(page)
            # Remover município origem
            await page.evaluate("""()=>{
                document.querySelector('#c_cdd_ori').value='0';
                document.querySelector('#t_cdd_ori').value='';
            }""")
            await page.wait_for_timeout(200)
            await page.screenshot(path=str(OUT/"ct017_sem_municipio.png"))

            body = await gravar(page)
            lista = body.get("lista") or ""
            await page.screenshot(path=str(OUT/"ct017_apos_gravar.png"))

            assert body.get("codigo") == 0
            assert lista.startswith("Erro|") or "Munic" in lista or "Origin" in lista.lower(), \
                f"Esperado bloqueio município, obteve: {lista}"
            ok("CT-017", f"Bloqueio município origem confirmado: {lista[:80]}")
        except Exception as e:
            fail("CT-017", "Erro no teste município ausente", str(e))
            await page.screenshot(path=str(OUT/"ct017_erro.png"))

        # -----------------------------------------------
        print("\n=== CT-RCT-019: Rodo-Fluvial sem transbordo — bloqueio ===")
        await goto_rctrc(page)
        await close_all(page)
        try:
            await selecionar_apolice(page, "1", "10", "1", "C")
            await preencher_form_basico(page)
            # UF origem = AM (fluvial)
            await page.select_option("#n_ori", "AM")
            await page.wait_for_timeout(400)
            await page.evaluate("""()=>{
                document.querySelector('#c_cdd_ori').value='0';
                document.querySelector('#t_cdd_ori').value='';
            }""")
            # Ativar fluvial
            await page.select_option("#e_tr1", "F")
            await page.wait_for_timeout(600)
            # NÃO preencher transbordo
            await page.screenshot(path=str(OUT/"ct019_fluvial_sem_transbordo.png"))

            body = await gravar(page)
            lista = body.get("lista") or ""
            await page.screenshot(path=str(OUT/"ct019_apos_gravar.png"))

            assert body.get("codigo") == 0
            assert lista.startswith("Erro|") or "transbordo" in lista.lower() or "Transbordo" in lista or "Estado" in lista, \
                f"Esperado bloqueio transbordo, obteve: {lista}"
            ok("CT-019", f"Bloqueio transbordo confirmado: {lista[:80]}")
        except Exception as e:
            fail("CT-019", "Erro no teste Rodo-Fluvial sem transbordo", str(e))
            await page.screenshot(path=str(OUT/"ct019_erro.png"))

        # -----------------------------------------------
        print("\n=== CT-RCT-020: Rodo-Fluvial em UF não fluvial — bloqueio ===")
        await goto_rctrc(page)
        await close_all(page)
        try:
            await selecionar_apolice(page, "1", "10", "1", "C")
            await preencher_form_basico(page)
            # UF origem = SP (NÃO fluvial) e ativar fluvial
            await page.select_option("#n_ori", "SP")
            await page.wait_for_timeout(400)
            await page.evaluate("""()=>{
                document.querySelector('#c_cdd_ori').value='34401';
                document.querySelector('#t_cdd_ori').value='Osasco';
            }""")
            await page.select_option("#e_tr1", "F")
            await page.wait_for_timeout(600)
            # Preencher transbordo (para não cair no CT-019)
            await page.evaluate("""()=>{
                const s = document.querySelector('#s_uf_bld');
                if(s) s.value = 'Porto Alegre';
                const n = document.querySelector('#n_bld');
                if(n) n.value = 'RS';
            }""")
            await page.screenshot(path=str(OUT/"ct020_uf_nao_fluvial.png"))

            body = await gravar(page)
            lista = body.get("lista") or ""
            await page.screenshot(path=str(OUT/"ct020_apos_gravar.png"))

            assert body.get("codigo") == 0
            assert lista.startswith("Erro|") or "fluvial" in lista.lower() or "percurso" in lista.lower(), \
                f"Esperado bloqueio fluvial, obteve: {lista}"
            ok("CT-020", f"Bloqueio Rodo-Fluvial UF inválida confirmado: {lista[:80]}")
        except Exception as e:
            fail("CT-020", "Erro no teste Rodo-Fluvial UF inválida", str(e))
            await page.screenshot(path=str(OUT/"ct020_erro.png"))

        # -----------------------------------------------
        print("\n=== CT-RCT-021 (BLOQUEADO): DDR tipo S ===")
        skip("CT-021", "BLOQUEADO: tb_cit_net_ddr_tom vazia, i_adl_ddr='N' em todas as apólices")

        print("\n=== CT-RCT-022 (BLOQUEADO): DDR tipo E ===")
        skip("CT-022", "BLOQUEADO: e_tip_opc='E' não existe em HML AXA")

        print("\n=== CT-RCT-018 (BLOQUEADO): CNPJ embarcador ausente ===")
        skip("CT-018", "BLOQUEADO: AXA dispensa CNPJ embarcador — executar em HML KOVR/MITSUI")

        # -----------------------------------------------
        print("\n=== CT-RCT-023: Gravar sem subgrupo — bloqueio JS ===")
        await goto_rctrc(page)
        await close_all(page)
        try:
            await page.select_option("#c_org_prd", "1")
            await page.wait_for_timeout(1500)
            await page.evaluate("""()=>{
                const s=document.querySelector('#u_apo_pnc');
                s.value='10';
                s.dispatchEvent(new Event('change',{bubbles:true}));
            }""")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(1500)
            # NÃO selecionar subgrupo (manter u_sgp = 0)
            await page.evaluate("()=>document.querySelector('#u_sgp').value='0'")
            await page.select_option("#e_doc_ebq", "C")
            await preencher_form_basico(page)

            # Tentar gravar — JS deve bloquear (sem disparar AJAX)
            # Usar timeout curto pois AJAX não deve ser disparado
            gravacao_disparada = False
            try:
                async with page.expect_response(
                    lambda r: "/AverbacaoNacional/Gravar" in r.url,
                    timeout=4000
                ) as resp_info:
                    await page.click("#btEnviar")
                gravacao_disparada = True
                body = await (await resp_info.value).json()
                lista = body.get("lista", "")
                # Se disparou AJAX, o server deve bloquear por subgrupo
                if lista.startswith("Erro|") or "subgrupo" in lista.lower() or "sgp" in lista.lower():
                    ok("CT-023", f"Bloqueio por subgrupo (server): {lista[:80]}")
                else:
                    fail("CT-023", f"AJAX disparado mas sem bloqueio esperado: {lista[:80]}")
            except Exception:
                # TimeoutError = AJAX não foi disparado (JS bloqueou) = comportamento correto
                if not gravacao_disparada:
                    await page.screenshot(path=str(OUT/"ct023_sem_ajax.png"))
                    ok("CT-023", "AJAX não disparado — validação JS bloqueou (correto)")
        except Exception as e:
            fail("CT-023", "Erro no teste sem subgrupo", str(e))
            await page.screenshot(path=str(OUT/"ct023_erro.png"))

        # -----------------------------------------------
        print("\n=== CT-RCT-027: Imprimir após gravação ===")
        if protocolo_ct005:
            await goto_rctrc(page)
            await close_all(page)
            try:
                await selecionar_apolice(page, "1", "10", "1", "C")
                await preencher_form_basico(page)
                body = await gravar(page)
                partes = (body.get("lista") or "").split("|")
                if partes[0] == "OK" and len(partes) > 1 and partes[1]:
                    btImprimir_dis_before = await page.evaluate(
                        "()=>document.querySelector('#btImprimir')?.disabled"
                    )
                    await page.screenshot(path=str(OUT/"ct027_apos_gravar.png"))
                    assert btImprimir_dis_before == False, f"btImprimir ainda disabled após gravação"
                    ok("CT-027", f"btImprimir habilitado após gravação (protocolo={partes[1]})")
                else:
                    fail("CT-027", f"Gravação falhou para o teste de impressão: {body.get('lista')}")
            except Exception as e:
                fail("CT-027", "Erro no teste de impressão", str(e))
                await page.screenshot(path=str(OUT/"ct027_erro.png"))
        else:
            skip("CT-027", "CT-005 não gravou protocolo — CT-027 dependente")

        await br.close()

    # Relatório final
    print("\n" + "="*70)
    print("RESULTADO FINAL DOS TESTES RCTRC")
    print("="*70)
    passou = [r for r in RESULTADOS if r["status"] == "PASSOU"]
    falhou = [r for r in RESULTADOS if r["status"] == "FALHOU"]
    bloq   = [r for r in RESULTADOS if r["status"] == "BLOQUEADO"]
    print(f"  PASSOU:    {len(passou)}")
    print(f"  FALHOU:    {len(falhou)}")
    print(f"  BLOQUEADO: {len(bloq)}")
    if falhou:
        print("\n  FALHAS:")
        for r in falhou:
            print(f"    {r['ct']}: {r['desc']} — {r.get('detalhe','')}")

    # Salvar resultado
    (OUT/"resultado_testes.json").write_text(
        json.dumps(RESULTADOS, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nResultados salvos em: {OUT}/resultado_testes.json")


asyncio.run(main())
