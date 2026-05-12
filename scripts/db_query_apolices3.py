"""
Queries focadas: e_avb, RCF real, DDR, SGP, tipos disponíveis para os CTs.
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
    for r in rows[:30]:
        print("  " + " | ".join(f"{str(v):<22}" for v in list(r)[:10]))
    if len(rows) > 30:
        print(f"  ... +{len(rows)-30} linhas")
    print(f"  Total: {len(rows)} linha(s)")
    return rows, cols

def main():
    conn = pyodbc.connect(CONN_STR, autocommit=True)
    print("Conexão OK.")

    # 1. Distribuição e_avb ramo 54
    run(conn, """
        SELECT e_avb, e_rmo_apo, COUNT(*) as qtd
        FROM tb_apo_nac_cit
        WHERE c_rmo = 54
        GROUP BY e_avb, e_rmo_apo
        ORDER BY qtd DESC
    """, "1. Distribuição e_avb + e_rmo_apo ramo 54")

    # 2. Apólices ramo 54 com e_avb = 'A' (Automática)
    run(conn, """
        SELECT n.u_apo_pnc, n.c_org_prd, n.e_avb, n.c_rmo_rcf, n.u_apo_rcf,
               n.d_ini_vig_apo, n.d_fim_vig_apo, n.i_adl_ddr, n.i_cbr_agr_ddr
        FROM tb_apo_nac_cit n
        WHERE n.c_rmo = 54 AND n.e_avb = 'A'
        ORDER BY n.u_apo_pnc
    """, "2. Apólices e_avb='A' ramo 54")

    # 3. Apólices ramo 54 com e_avb = 'M' (Manual)
    run(conn, """
        SELECT n.u_apo_pnc, n.c_org_prd, n.e_avb, n.c_rmo_rcf, n.u_apo_rcf,
               n.d_ini_vig_apo, n.d_fim_vig_apo, n.i_adl_ddr, n.i_cbr_agr_ddr
        FROM tb_apo_nac_cit n
        WHERE n.c_rmo = 54 AND n.e_avb = 'M'
        ORDER BY n.u_apo_pnc
    """, "3. Apólices e_avb='M' ramo 54")

    # 4. Apólice 10 detalhada (a que usamos nos testes)
    run(conn, """
        SELECT n.u_apo_pnc, n.c_org_prd, n.e_avb, n.e_rmo_apo,
               n.c_rmo_rcf, n.u_apo_rcf,
               n.i_adl_ddr, n.f_adl_ddr, n.i_cbr_agr_ddr,
               n.i_trp_trr_cit, n.i_trp_mar_cit, n.i_trp_flu_cit,
               n.d_ini_vig_apo, n.d_fim_vig_apo
        FROM tb_apo_nac_cit n
        WHERE n.c_rmo = 54 AND n.c_org_prd = 1 AND n.u_apo_pnc = 10
    """, "4. Apólice 10 filial 1 - detalhes completos")

    # 5. Verificar SGPs disponíveis para apólice 10
    run(conn, """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME LIKE '%sgp%' OR TABLE_NAME LIKE '%sub%'
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """, "5. Tabelas com 'sgp'/'sub'")

    # 6. Apólice com c_rmo_rcf != 0 (RCF real vinculado)
    run(conn, """
        SELECT TOP 20 n.u_apo_pnc, n.c_org_prd, n.e_avb, n.c_rmo_rcf, n.u_apo_rcf,
               n.f_bsc_grl_rcf, n.f_bsc_epf_rcf
        FROM tb_apo_nac_cit n
        WHERE n.c_rmo = 54 AND n.c_rmo_rcf != 0
        ORDER BY n.u_apo_pnc
    """, "6. Apólices ramo 54 com c_rmo_rcf != 0")

    # 7. Verificar o que c_rmo_rcf=0 mas u_apo_rcf != 0 significa
    #    Buscar nas colunas restantes de tb_apo_nac_cit (offset 70)
    run(conn, """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'tb_apo_nac_cit'
        ORDER BY ORDINAL_POSITION
        OFFSET 70 ROWS FETCH NEXT 70 ROWS ONLY
    """, "7. Colunas tb_apo_nac_cit (71-140)")

    # 8. Apólice com DDR (i_adl_ddr != ' ' ou 'N')
    run(conn, """
        SELECT TOP 10 n.u_apo_pnc, n.c_org_prd, n.e_avb, n.i_adl_ddr,
               n.f_adl_ddr, n.i_cbr_agr_ddr
        FROM tb_apo_nac_cit n
        WHERE n.c_rmo = 54
          AND n.i_adl_ddr IS NOT NULL AND n.i_adl_ddr NOT IN ('', 'N', ' ')
        ORDER BY n.u_apo_pnc
    """, "8. Apólices ramo 54 com DDR habilitado (i_adl_ddr)")

    # 9. Verificar tb_cit_net_ddr_tom: todos os ramos disponíveis
    run(conn, """
        SELECT c_rmo, COUNT(*) as qtd
        FROM tb_cit_net_ddr_tom
        GROUP BY c_rmo
        ORDER BY qtd DESC
    """, "9. DDR - ramos disponíveis no banco")

    # 10. Apólice com e_avb='D' + u_apo_rcf para entender campo
    run(conn, """
        SELECT TOP 5 n.u_apo_pnc, n.c_org_prd, n.e_avb, n.c_rmo_rcf,
               n.u_apo_rcf, n.f_bsc_grl_rcf
        FROM tb_apo_nac_cit n
        WHERE n.c_rmo = 54 AND n.c_org_prd = 1 AND n.e_avb = 'D'
        ORDER BY n.u_apo_pnc
    """, "10. Amostra e_avb='D' ramo 54 filial 1")

    # 11. Verificar se há apólice SGP/subgrupo em tb_apo_nac_cit
    run(conn, """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'tb_apo_nac_cit'
          AND (COLUMN_NAME LIKE '%sgp%' OR COLUMN_NAME LIKE '%sub%'
               OR COLUMN_NAME LIKE '%grp%' OR COLUMN_NAME LIKE '%grup%')
        ORDER BY ORDINAL_POSITION
    """, "11. Colunas sgp/sub/grp em tb_apo_nac_cit")

    # 12. Verificar tabela que controla SGP/subapólice
    run(conn, """
        SELECT name FROM sys.tables
        WHERE name LIKE '%sgp%' OR name LIKE '%sub_apo%'
        ORDER BY name
    """, "12. Tabelas SGP")

    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    main()
