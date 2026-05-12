"""Verifica TB_CIT_NET_PARAM_GERAL."""
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
    print("  " + " | ".join(f"{c:<30}" for c in cols[:6]))
    print("  " + "-"*100)
    for r in rows[:30]:
        print("  " + " | ".join(f"{str(v):<30}" for v in list(r)[:6]))
    print(f"  Total: {len(rows)} linha(s)")

def main():
    conn = pyodbc.connect(CONN_STR, autocommit=True)
    run(conn, "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'TB_CIT_NET_PARAM_GERAL' ORDER BY ORDINAL_POSITION", "Colunas TB_CIT_NET_PARAM_GERAL")
    run(conn, "SELECT TOP 50 * FROM TB_CIT_NET_PARAM_GERAL", "Valores TB_CIT_NET_PARAM_GERAL")

    # Verificar SGP apólice 10 condições - busca com todos os campos
    run(conn, """
        SELECT s.u_apo_pnc, s.u_sgp, s.e_trp, s.e_cnd_cml,
               s.i_cml_adl_ocd, s.f_cml_adl_ocd,
               s.i_cml_adl_ica, s.f_cml_adl_ica, s.f_cml_bsc
        FROM tb_sgp_nac_cml_cit s
        WHERE s.c_rmo = 54 AND s.c_org_prd = 1 AND s.u_apo_pnc = 11092222
    """, "Condições SGP apólice 11092222 OCD=S")

    # Apólice 5022026 (e_avb='M') - SGP
    run(conn, "SELECT * FROM tb_sgp_cit WHERE c_rmo = 54 AND u_apo_pnc = 5022026", "SGP apólice 5022026 (tipo M)")

    # Verificar se apólice 224466 SGP condições têm OCD
    run(conn, """
        SELECT s.u_apo_pnc, s.u_sgp, s.e_trp, s.e_cnd_cml,
               s.i_cml_adl_ocd, s.f_cml_adl_ocd,
               s.i_cml_adl_ica, s.f_cml_adl_ica, s.f_cml_bsc,
               s.v_is_ini, s.v_is_fim
        FROM tb_sgp_nac_cml_cit s
        WHERE s.c_rmo = 54 AND s.c_org_prd = 1 AND s.u_apo_pnc = 224466
    """, "Condições SGP apólice 224466 (tem RCF)")

    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    main()
