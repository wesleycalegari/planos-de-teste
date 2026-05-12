"""
Queries SELECT-ONLY para encontrar apólices ramo 54 com configurações específicas
para validação dos cenários do plano de teste RCTRC.
"""
import pyodbc, json, textwrap

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
    print("  " + " | ".join(f"{c:<25}" for c in cols[:8]))
    print("  " + "-"*min(len(cols)*27, 120))
    for r in rows[:20]:
        print("  " + " | ".join(f"{str(v):<25}" for v in list(r)[:8]))
    if len(rows) > 20:
        print(f"  ... +{len(rows)-20} linhas")
    print(f"  Total: {len(rows)} linha(s)")
    return rows, cols

def main():
    print("Conectando ao banco AXA HML...")
    conn = pyodbc.connect(CONN_STR, autocommit=True)
    print("Conexão OK.")

    # 1. Todas as colunas de tb_apo_cit
    run(conn, """
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'tb_apo_cit'
        ORDER BY ORDINAL_POSITION
    """, "1. Colunas tb_apo_cit")

    # 2. Todas as colunas de tb_apo_nac_cit
    run(conn, """
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'tb_apo_nac_cit'
        ORDER BY ORDINAL_POSITION
    """, "2. Colunas tb_apo_nac_cit")

    # 3. Colunas de tb_cit_net_ddr_tom (DDR)
    run(conn, """
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'tb_cit_net_ddr_tom'
        ORDER BY ORDINAL_POSITION
    """, "3. Colunas tb_cit_net_ddr_tom")

    # 4. Amostra de tb_apo_cit ramo 54
    run(conn, """
        SELECT TOP 5 u_apo_pnc, c_rmo, c_org_prd, *
        FROM tb_apo_cit
        WHERE c_rmo = 54
        ORDER BY u_apo_pnc
    """, "4. Amostra tb_apo_cit ramo 54 (colunas relevantes)")

    # 5. Ver colunas que contenham 'tip' ou 'tipo' ou 'hdl' ou 'hd_' para tipo apólice
    run(conn, """
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME IN ('tb_apo_cit','tb_apo_nac_cit')
          AND (COLUMN_NAME LIKE '%tip%' OR COLUMN_NAME LIKE '%hd%'
               OR COLUMN_NAME LIKE '%rcf%' OR COLUMN_NAME LIKE '%ddr%'
               OR COLUMN_NAME LIKE '%stp%' OR COLUMN_NAME LIKE '%est%')
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """, "5. Colunas com 'tip','hd','rcf','ddr','stp','est'")

    # 6. Amostra de tb_apo_nac_cit ramo 54
    run(conn, """
        SELECT TOP 5 * FROM tb_apo_nac_cit
        WHERE c_rmo = 54
        ORDER BY u_apo_pnc
    """, "6. Amostra tb_apo_nac_cit ramo 54")

    # 7. Buscar colunas com 'rcf' em qualquer tabela
    run(conn, """
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE COLUMN_NAME LIKE '%rcf%'
          OR COLUMN_NAME LIKE '%rfc%'
        ORDER BY TABLE_NAME, COLUMN_NAME
    """, "7. Colunas com 'rcf'/'rfc'")

    # 8. Buscar colunas com 'ddr' em qualquer tabela
    run(conn, """
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE COLUMN_NAME LIKE '%ddr%'
        ORDER BY TABLE_NAME, COLUMN_NAME
    """, "8. Colunas com 'ddr'")

    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    main()
