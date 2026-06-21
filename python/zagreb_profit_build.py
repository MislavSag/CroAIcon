# Zagreb headquarters effect: county shares of profit, jobs and revenue, 2002-2024.
# Source: FINA GFI (db_afs). Profit uses the blessed view logic (b184/b197 - b185/b198), NOT b183 (dead).
# Single full-table pass: conditional sums for Zagreb/RH x all-sectors/excl-K, grouped by year.
import pymysql, pandas as pd, os

creds = {}
for line in open(r"C:\Users\lsikic\projects\CroAIcon\.env", encoding="utf-8"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1); creds[k.strip()] = v.strip()
conn = pymysql.connect(host=creds["GFI_DB_HOST"], port=int(creds["GFI_DB_PORT"]),
    user=creds["GFI_DB_USER"], password=creds["GFI_DB_PASSWORD"], database=creds["GFI_DB_NAME"],
    connect_timeout=15, read_timeout=900); cur = conn.cursor()

ZG = 21  # Grad Zagreb (ref_county.code)
NR = "(COALESCE(NULLIF(b184,0),NULLIF(b197,0),0) - COALESCE(NULLIF(b185,0),NULLIF(b198,0),0))"  # signed net result
POS = f"CASE WHEN {NR}>0 THEN {NR} ELSE 0 END"            # positive-profit pool contribution
ISZG = f"countyid={ZG}"
NOTK = "(nacerev21<>'K' OR nacerev21 IS NULL)"            # exclude financials

SEL = f"""SELECT %(y)s AS reportyear,
    SUM({POS})                                            AS profit_rh,
    SUM(CASE WHEN {ISZG} THEN {POS} ELSE 0 END)           AS profit_zg,
    SUM({POS} * ({NOTK}))                                 AS profit_rh_k,
    SUM(CASE WHEN {ISZG} THEN {POS}*({NOTK}) ELSE 0 END)  AS profit_zg_k,
    SUM(COALESCE(employeecounteop,0))                                          AS emp_rh,
    SUM(CASE WHEN {ISZG} THEN COALESCE(employeecounteop,0) ELSE 0 END)         AS emp_zg,
    SUM(COALESCE(employeecounteop,0)*({NOTK}))                                 AS emp_rh_k,
    SUM(CASE WHEN {ISZG} THEN COALESCE(employeecounteop,0)*({NOTK}) ELSE 0 END) AS emp_zg_k,
    SUM(COALESCE(b125,0))                                                      AS rev_rh,
    SUM(CASE WHEN {ISZG} THEN COALESCE(b125,0) ELSE 0 END)                     AS rev_zg,
    SUM(COALESCE(b125,0)*({NOTK}))                                             AS rev_rh_k,
    SUM(CASE WHEN {ISZG} THEN COALESCE(b125,0)*({NOTK}) ELSE 0 END)            AS rev_zg_k,
    COUNT(*) AS n_rh, SUM({ISZG}) AS n_zg
  FROM db_afs WHERE reportyear=%(y)s"""
recs = []
for Y in range(2002, 2025):
    cur.execute(SEL, {"y": Y})
    recs.append([float(x or 0) for x in cur.fetchall()[0]])
    print(f"  year {Y} done", flush=True)
cols = [d[0] for d in cur.description]
raw = pd.DataFrame(recs, columns=cols)
conn.close()

def block(sample, pr, pz, er, ez, rr, rz):
    sh = lambda a, b: (100 * b / a).where(a != 0)
    d = pd.DataFrame({"sample": sample, "year": raw.reportyear.astype(int),
        "profit_share": sh(raw[pr], raw[pz]), "emp_share": sh(raw[er], raw[ez]),
        "rev_share": sh(raw[rr], raw[rz])})
    d["conc_index"] = (raw[pz] / raw[pr]) / (raw[ez] / raw[er])
    for c in (pr, pz, er, ez, rr, rz):
        d[c.replace("_k", "") if c.endswith("_k") else c] = raw[c]
    return d

df = pd.concat([
    block("all",    "profit_rh",   "profit_zg",   "emp_rh",   "emp_zg",   "rev_rh",   "rev_zg"),
    block("excl_k", "profit_rh_k", "profit_zg_k", "emp_rh_k", "emp_zg_k", "rev_rh_k", "rev_zg_k"),
], ignore_index=True)

out = r"C:\Users\lsikic\projects\CroAIcon\outputs\tables"; os.makedirs(out, exist_ok=True)
df.to_csv(out + r"\zagreb_profit_shares.csv", index=False, encoding="utf-8-sig")

pd.set_option("display.width", 160)
a = df[df["sample"] == "all"].set_index("year")
print("=== Zagreb share, ALL sectors (%) ===")
print(a[["emp_share", "rev_share", "profit_share", "conc_index"]].round(1).to_string())
k = df[df["sample"] == "excl_k"].set_index("year")
print("\n=== all vs excl-K, key years ===")
for Y in (2008, 2014, 2019, 2023, 2024):
    print(f"{Y}: ALL jobs={a.loc[Y,'emp_share']:.1f} rev={a.loc[Y,'rev_share']:.1f} profit={a.loc[Y,'profit_share']:.1f} "
          f"| exK jobs={k.loc[Y,'emp_share']:.1f} rev={k.loc[Y,'rev_share']:.1f} profit={k.loc[Y,'profit_share']:.1f}")
print("\nsaved zagreb_profit_shares.csv  | DONE")
