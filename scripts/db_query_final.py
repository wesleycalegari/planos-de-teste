"""
Queries finais: e_tip_opc (DDR), apólice ramo 21, detalhes 224466 e 11092222.
"""
import pyodbc

CONN_STR = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=smt-hom-citweb.database.windows.net;"
    "DATABASE=smt-hom-citweb-axa;"
    "UID=administrador;"
    "PWD=oashohchui7ooJ5i;"
    "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)

def run(conn, sql, label=""):
    print(f"\n{'='*70}")
    print(f"[{label}]")
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    print("  " + " | ".join(f"{c:<22}" for c in cols[:10]))
    print("  " + "-"*110)
    for r in rows[:20]:
        print("  " + " | ".join(f"{str(v):<22}" for v in list(r)[:10]))
    if len(rows) > 20:
        print(f"  ... +{len(rows)-20} linhas")
    print(f"  Total: {len(rows)} linha(s)")
    return rows, cols

def main():
    conn = pyodbc.connect(CONN_STR, autocommit=True)
    print("Conexão OK.")

    # 1. Distribuição e_tip_opc ramo 54 (DDR)
    run(conn, """
        SELECT e_tip_opc, COUNT(*) as qtd
        FROM tb_apo_nac_cit
        WHERE c_rmo = 54
        GROUP BY e_tip_opc
        ORDER BY qtd DESC
    """, "1. e_tip_opc distribuição ramo 54")

    # 2. Apólice com e_tip_opc S, T ou P vigente
    run(conn, """
        SELECT n.u_apo_pnc, n.c_org_prd, n.e_avb, n.e_tip_opc,
               n.c_rmo_rcf, n.u_apo_rcf, n.d_fim_vig_apo
        FROM tb_apo_nac_cit n
        WHERE n.c_rmo = 54
          AND n.e_tip_opc IN ('S','T','P')
          AND n.d_fim_vig_apo >= '2026-05-07'
        ORDER BY n.u_apo_pnc
    """, "2. Apólices DDR tipo S/T/P vigentes")

    # 3. Apólice com e_tip_opc E vigente (DDR Estipulação normal)
    run(conn, """
        SELECT n.u_apo_pnc, n.c_org_prd, n.e_avb, n.e_tip_opc,
               n.c_rmo_rcf, n.u_apo_rcf, n.d_fim_vig_apo
        FROM tb_apo_nac_cit n
        WHERE n.c_rmo = 54
          AND n.e_tip_opc = 'E'
          AND n.d_fim_vig_apo >= '2026-05-07'
        ORDER BY n.u_apo_pnc
    """, "3. Apólices DDR tipo E vigentes")

    # 4. Apólice 10 - e_tip_opc
    run(conn, """
        SELECT u_apo_pnc, c_org_prd, e_tip_opc, e_avb, i_adl_ddr, i_cbr_agr_ddr
        FROM tb_apo_nac_cit
        WHERE c_rmo = 54 AND c_org_prd = 1 AND u_apo_pnc = 10
    """, "4. Apólice 10 - e_tip_opc")

    # 5. Apólice 224466 - e_tip_opc (tem RCF)
    run(conn, """
        SELECT u_apo_pnc, c_org_prd, e_tip_opc, e_avb, c_rmo_rcf, u_apo_rcf,
               i_adl_ddr, d_fim_vig_apo
        FROM tb_apo_nac_cit
        WHERE c_rmo = 54 AND c_org_prd = 1 AND u_apo_pnc = 224466
    """, "5. Apólice 224466 - detalhes DDR/RCF")

    # 6. Apólice 11092222 - OCD habilitado - verificar e_tip_opc e SGP
    run(conn, """
        SELECT u_apo_pnc, c_org_prd, e_tip_opc, e_avb, c_rmo_rcf, u_apo_rcf,
               i_adl_ddr, d_fim_vig_apo
        FROM tb_apo_nac_cit
        WHERE c_rmo = 54 AND c_org_prd = 1 AND u_apo_pnc = 11092222
    """, "6. Apólice 11092222 - detalhes")

    # 7. SGP da apólice 11092222
    run(conn, """
        SELECT * FROM tb_sgp_cit
        WHERE c_rmo = 54 AND c_org_prd = 1 AND u_apo_pnc = 11092222
    """, "7. SGPs da apólice 11092222")

    # 8. Ramo 21 - apólice vigente filial 1
    run(conn, """
        SELECT TOP 5 n.u_apo_pnc, n.c_org_prd, n.e_avb, n.d_ini_vig_apo, n.d_fim_vig_apo
        FROM tb_apo_nac_cit n
        WHERE n.c_rmo = 21
          AND n.c_org_prd = 1
          AND n.d_fim_vig_apo >= '2026-05-07'
        ORDER BY n.u_apo_pnc
    """, "8. Apólices ramo 21 filial 1 vigentes")

    # 9. Verificar Ind_Premio_Zerado_Conversor (configuração global)
    run(conn, """
        SELECT name FROM sys.tables
        WHERE name LIKE '%conversor%' OR name LIKE '%cnv%' OR name LIKE '%param%'
           OR name LIKE '%config%' OR name LIKE '%cfg%' OR name LIKE '%ind%'
        ORDER BY name
    """, "9. Tabelas de configuração global")

    # 10. Verificar apólice 224466 SGP condições completas (i_cml_adl_ocd, etc.)
    run(conn, """
        SELECT s.u_apo_pnc, s.u_sgp, s.e_trp, s.i_cml_adl_ocd, s.f_cml_adl_ocd,
               s.i_cml_adl_ica, s.f_cml_adl_ica, s.i_cml_adl_rbo, s.f_cml_bsc,
               s.e_cnd_cml
        FROM tb_sgp_nac_cml_cit s
        WHERE s.c_rmo = 54 AND s.c_org_prd = 1 AND s.u_apo_pnc = 224466
    """, "10. Condições comerciais apólice 224466")

    # 11. Verificar se AXA é seguradora específica - qual c_seg para ramo 54 filial 1
    run(conn, """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'tb_apo_nac_cit'
          AND (COLUMN_NAME LIKE '%seg%' OR COLUMN_NAME LIKE '%cia%' OR COLUMN_NAME LIKE '%ins%')
        ORDER BY ORDINAL_POSITION
    """, "11. Colunas seguradora em tb_apo_nac_cit")

    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    main()
