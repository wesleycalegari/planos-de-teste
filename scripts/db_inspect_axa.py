"""
Inspeção SELECT-ONLY no banco AXA HML para validar massas de dados do plano RCTRC.
Objetivo: encontrar apólices ramo 54 com configurações específicas (tipo A/M, RCF, DDR).
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
    print(textwrap.fill(sql.strip(), 120, subsequent_indent="  "))
    print("-"*70)
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    print("  " + " | ".join(f"{c:<20}" for c in cols))
    print("  " + "-"*min(len(cols)*23, 120))
    for r in rows[:30]:
        print("  " + " | ".join(f"{str(v):<20}" for v in r))
    if len(rows) > 30:
        print(f"  ... +{len(rows)-30} linhas")
    print(f"  Total: {len(rows)} linha(s)")
    return rows, cols

def main():
    print("Conectando ao banco AXA HML...")
    conn = pyodbc.connect(CONN_STR, autocommit=True)
    print("Conexão OK.\n")

    # 1. Descobrir tabelas relacionadas a apólice
    run(conn, """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
          AND TABLE_NAME LIKE '%apo%'
        ORDER BY TABLE_NAME
    """, "1. Tabelas com 'apo'")

    # 2. Descobrir tabelas com colunas relacionadas a ramo/tipo
    run(conn, """
        SELECT DISTINCT t.TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES t
        JOIN INFORMATION_SCHEMA.COLUMNS c ON c.TABLE_NAME = t.TABLE_NAME
        WHERE c.COLUMN_NAME LIKE '%rmo%' OR c.COLUMN_NAME LIKE '%ramo%'
          AND t.TABLE_TYPE = 'BASE TABLE'
        ORDER BY t.TABLE_NAME
    """, "2. Tabelas com coluna 'rmo'/'ramo'")

    # 3. Procurar tabela principal de apolice
    for tbl in ['apolice', 'Apolice', 'tb_apolice', 'TbApolice', 'apol', 'u_apolice']:
        try:
            run(conn, f"SELECT TOP 1 * FROM [{tbl}]", f"3. Amostra {tbl}")
        except:
            pass

    # 4. Buscar tabela via sys.tables
    run(conn, """
        SELECT name FROM sys.tables
        WHERE name LIKE '%apol%' OR name LIKE '%apo%'
        ORDER BY name
    """, "4. sys.tables com 'apol'/'apo'")

    # 5. Colunas da tabela mais provável
    run(conn, """
        SELECT c.TABLE_NAME, c.COLUMN_NAME, c.DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS c
        WHERE c.TABLE_NAME IN (
            SELECT name FROM sys.tables WHERE name LIKE '%apol%' OR name LIKE '%apo%'
        )
        ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION
    """, "5. Colunas das tabelas 'apol'")

    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    main()
