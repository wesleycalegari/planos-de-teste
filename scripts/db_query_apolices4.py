"""
Queries finais: vigência das apólices, SGPs disponíveis, condições OCD.
"""
import pyodbc
from datetime import date

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
    for r in rows[:25]:
        print("  " + " | ".join(f"{str(v):<22}" for v in list(r)[:10]))
    if len(rows) > 25:
        print(f"  ... +{len(rows)-25} linhas")
    print(f"  Total: {len(rows)} linha(s)")
    return rows, cols

def main():
    conn = pyodbc.connect(CONN_STR, autocommit=True)
    print("Conexão OK. Data atual:", date.today())

    # 1. Apólices e_avb='M' vigentes hoje (2026-05-07)
    run(conn, """
        SELECT n.u_apo_pnc, n.c_org_prd, n.e_avb, n.c_rmo_rcf, n.u_apo_rcf,
               n.d_ini_vig_apo, n.d_fim_vig_apo, n.i_adl_ddr
        FROM tb_apo_nac_cit n
        WHERE n.c_rmo = 54 AND n.e_avb = 'M'
          AND n.d_fim_vig_apo >= '2026-05-07'
        ORDER BY n.u_apo_pnc
    """, "1. Apólices e_avb='M' ramo 54 VIGENTES HOJE")

    # 2. Apólices e_avb='A' vigentes hoje
    run(conn, """
        SELECT n.u_apo_pnc, n.c_org_prd, n.e_avb, n.c_rmo_rcf, n.u_apo_rcf,
               n.d_ini_vig_apo, n.d_fim_vig_apo, n.i_adl_ddr
        FROM tb_apo_nac_cit n
        WHERE n.c_rmo = 54 AND n.e_avb = 'A'
          AND n.d_fim_vig_apo >= '2026-05-07'
        ORDER BY n.u_apo_pnc
    """, "2. Apólices e_avb='A' ramo 54 VIGENTES HOJE")

    # 3. Apólices com RCF (c_rmo_rcf != 0) vigentes hoje
    run(conn, """
        SELECT n.u_apo_pnc, n.c_org_prd, n.e_avb, n.c_rmo_rcf, n.u_apo_rcf,
               n.d_ini_vig_apo, n.d_fim_vig_apo
        FROM tb_apo_nac_cit n
        WHERE n.c_rmo = 54 AND n.c_rmo_rcf != 0
          AND n.d_fim_vig_apo >= '2026-05-07'
        ORDER BY n.u_apo_pnc
    """, "3. Apólices com RCF vigentes hoje")

    # 4. SGPs disponíveis para apólice 10 (filial 1, ramo 54)
    run(conn, """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'tb_sgp_cit'
        ORDER BY ORDINAL_POSITION
    """, "4. Colunas tb_sgp_cit")

    # 5. SGP para apólice 10
    run(conn, """
        SELECT * FROM tb_sgp_cit
        WHERE c_rmo = 54 AND c_org_prd = 1 AND u_apo_pnc = 10
    """, "5. SGPs da apólice 10 ramo 54 filial 1")

    # 6. Colunas de tb_sgp_nac_cml_cit (condições OCD/DDR por SGP)
    run(conn, """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'tb_sgp_nac_cml_cit'
        ORDER BY ORDINAL_POSITION
    """, "6. Colunas tb_sgp_nac_cml_cit")

    # 7. Condições OCD do SGP 1 apólice 10
    run(conn, """
        SELECT * FROM tb_sgp_nac_cml_cit
        WHERE c_rmo = 54 AND c_org_prd = 1 AND u_apo_pnc = 10
    """, "7. Condições SGP apólice 10")

    # 8. SGPs da apólice 224466 (tem RCF)
    run(conn, """
        SELECT * FROM tb_sgp_cit
        WHERE c_rmo = 54 AND c_org_prd = 1 AND u_apo_pnc = 224466
    """, "8. SGPs apólice 224466 (tem RCF)")

    # 9. Condições OCD da apólice 224466 SGP
    run(conn, """
        SELECT * FROM tb_sgp_nac_cml_cit
        WHERE c_rmo = 54 AND c_org_prd = 1 AND u_apo_pnc = 224466
    """, "9. Condições SGP apólice 224466")

    # 10. SGP da apólice 555 (e_avb='A', filial 41)
    run(conn, """
        SELECT * FROM tb_sgp_cit
        WHERE c_rmo = 54 AND c_org_prd = 41 AND u_apo_pnc = 555
    """, "10. SGPs apólice 555 filial 41 (e_avb='A')")

    # 11. Apólice 106540011626 (e_avb='A' + RCF) - SGP
    run(conn, """
        SELECT * FROM tb_sgp_cit
        WHERE c_rmo = 54 AND c_org_prd = 1 AND u_apo_pnc = 106540011626
    """, "11. SGPs apólice 106540011626 (A + RCF)")

    # 12. Apólice e_avb='D', c_org_prd=1, vigente, OCD habilitado
    run(conn, """
        SELECT TOP 5
            s.u_apo_pnc, s.u_sgp, s.c_org_prd,
            s.i_cml_adl_ocd, s.f_cml_adl_ocd,
            s.i_cml_adl_ica, s.f_cml_adl_ica,
            n.e_avb, n.d_fim_vig_apo
        FROM tb_sgp_nac_cml_cit s
        JOIN tb_apo_nac_cit n ON n.u_apo_pnc = s.u_apo_pnc
            AND n.c_rmo = s.c_rmo AND n.c_org_prd = s.c_org_prd
        WHERE s.c_rmo = 54 AND s.c_org_prd = 1
          AND s.i_cml_adl_ocd = 'S'
          AND n.d_fim_vig_apo >= '2026-05-07'
        ORDER BY s.u_apo_pnc
    """, "12. Apólices filial 1 ramo 54 com OCD habilitado e vigentes")

    # 13. Apólice e_avb='D' c_org_prd=1 vigente com i_cml_adl_ica='S' (OCD+Içamento)
    run(conn, """
        SELECT TOP 5
            s.u_apo_pnc, s.u_sgp, s.c_org_prd,
            s.i_cml_adl_ocd, s.i_cml_adl_ica,
            n.e_avb, n.d_fim_vig_apo
        FROM tb_sgp_nac_cml_cit s
        JOIN tb_apo_nac_cit n ON n.u_apo_pnc = s.u_apo_pnc
            AND n.c_rmo = s.c_rmo AND n.c_org_prd = s.c_org_prd
        WHERE s.c_rmo = 54 AND s.c_org_prd = 1
          AND s.i_cml_adl_ica = 'S'
          AND n.d_fim_vig_apo >= '2026-05-07'
        ORDER BY s.u_apo_pnc
    """, "13. Apólices filial 1 ramo 54 com OCD+Içamento habilitado e vigentes")

    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    main()
