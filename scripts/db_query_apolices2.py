"""
Queries focadas para encontrar apólices ramo 54 com configurações específicas.
"""
import pyodbc, json

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
    print("Conectando ao banco AXA HML...")
    conn = pyodbc.connect(CONN_STR, autocommit=True)
    print("Conexão OK.")

    # 1. Colunas completas de tb_apo_nac_cit (parte 2 - de 20 em diante)
    run(conn, """
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'tb_apo_nac_cit'
        ORDER BY ORDINAL_POSITION
        OFFSET 20 ROWS FETCH NEXT 50 ROWS ONLY
    """, "1. Colunas tb_apo_nac_cit (21-70)")

    # 2. Colunas com 'ddr', 'tip', 'stp' em tb_apo_nac_cit
    run(conn, """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'tb_apo_nac_cit'
          AND (COLUMN_NAME LIKE '%ddr%' OR COLUMN_NAME LIKE '%tip%'
               OR COLUMN_NAME LIKE '%stp%' OR COLUMN_NAME LIKE '%hd%'
               OR COLUMN_NAME LIKE '%est%' OR COLUMN_NAME LIKE '%avb%'
               OR COLUMN_NAME LIKE '%blq%')
        ORDER BY ORDINAL_POSITION
    """, "2. Colunas especiais em tb_apo_nac_cit")

    # 3. Amostra tb_apo_nac_cit ramo 54 - campos principais
    run(conn, """
        SELECT TOP 10
            n.u_apo_pnc, n.c_rmo, n.c_org_prd,
            n.e_rmo_apo, n.e_avb,
            n.c_rmo_rcf, n.u_apo_rcf,
            n.d_ini_vig_apo, n.d_fim_vig_apo
        FROM tb_apo_nac_cit n
        WHERE n.c_rmo = 54
        ORDER BY n.u_apo_pnc
    """, "3. Amostra ramo 54 (e_rmo_apo, rcf)")

    # 4. Distintos valores de e_rmo_apo no ramo 54
    run(conn, """
        SELECT e_rmo_apo, COUNT(*) as qtd
        FROM tb_apo_nac_cit
        WHERE c_rmo = 54
        GROUP BY e_rmo_apo
        ORDER BY qtd DESC
    """, "4. Valores distintos de e_rmo_apo (ramo 54)")

    # 5. Apólice tipo A ramo 54 (se e_rmo_apo = 'A')
    run(conn, """
        SELECT TOP 10
            n.u_apo_pnc, n.c_rmo, n.c_org_prd, n.e_rmo_apo, n.e_avb,
            n.c_rmo_rcf, n.u_apo_rcf,
            n.i_trp_trr_cit, n.i_trp_mar_cit, n.i_trp_aer_cit, n.i_trp_flu_cit
        FROM tb_apo_nac_cit n
        WHERE n.c_rmo = 54 AND n.e_rmo_apo = 'A'
        ORDER BY n.u_apo_pnc
    """, "5. Apólices tipo A ramo 54")

    # 6. Apólice tipo M ramo 54
    run(conn, """
        SELECT TOP 10
            n.u_apo_pnc, n.c_rmo, n.c_org_prd, n.e_rmo_apo, n.e_avb,
            n.c_rmo_rcf, n.u_apo_rcf
        FROM tb_apo_nac_cit n
        WHERE n.c_rmo = 54 AND n.e_rmo_apo = 'M'
        ORDER BY n.u_apo_pnc
    """, "6. Apólices tipo M ramo 54")

    # 7. Apólice com RCF vinculado (u_apo_rcf != 0 ou não nulo)
    run(conn, """
        SELECT TOP 10
            n.u_apo_pnc, n.c_rmo, n.c_org_prd, n.e_rmo_apo, n.e_avb,
            n.c_rmo_rcf, n.u_apo_rcf,
            n.f_bsc_grl_rcf, n.f_bsc_epf_rcf
        FROM tb_apo_nac_cit n
        WHERE n.c_rmo = 54
          AND n.u_apo_rcf IS NOT NULL
          AND n.u_apo_rcf != 0
        ORDER BY n.u_apo_pnc
    """, "7. Apólices ramo 54 COM RCF vinculado")

    # 8. Apólice com DDR habilitado
    run(conn, """
        SELECT DISTINCT d.u_apo_pnc, d.c_rmo, d.c_org_prd, d.i_opr_ddr, d.i_sit,
                        d.u_cnpj_cpf, d.i_tpi_cnpj_cpf, d.d_ini_vig_ddr, d.d_fim_vig_ddr
        FROM tb_cit_net_ddr_tom d
        WHERE d.c_rmo = 54
        ORDER BY d.u_apo_pnc
    """, "8. DDR configurado ramo 54")

    # 9. Verificar se há coluna de tipo apólice em tb_apo_cit (os 20 restantes)
    run(conn, """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'tb_apo_cit'
        ORDER BY ORDINAL_POSITION
        OFFSET 20 ROWS
    """, "9. Colunas tb_apo_cit (de 21 em diante)")

    # 10. Verificar tb_adt_cme_cit ou tb_adi_cme_cit (adicionais, condições)
    run(conn, """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'tb_adi_cme_cit'
        ORDER BY ORDINAL_POSITION
    """, "10. Colunas tb_adi_cme_cit (condições comerciais/adicionais)")

    # 11. Amostra de adicionais para ramo 54
    run(conn, """
        SELECT TOP 20 * FROM tb_adi_cme_cit
        WHERE c_rmo = 54
    """, "11. Amostra tb_adi_cme_cit ramo 54")

    # 12. Buscar tabela com campo 'stp' (estipulante DDR)
    run(conn, """
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE COLUMN_NAME LIKE '%stp%' OR COLUMN_NAME LIKE 'e_stp%'
          OR COLUMN_NAME LIKE '%estip%'
        ORDER BY TABLE_NAME, COLUMN_NAME
    """, "12. Colunas estipulante/stp")

    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    main()
