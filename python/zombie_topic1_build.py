import pymysql, pymysql.cursors, pandas as pd, numpy as np, os

creds = {}
for line in open(r"C:\Users\lsikic\projects\CroAIcon\.env", encoding="utf-8"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1); creds[k.strip()] = v.strip()
conn = pymysql.connect(host=creds["GFI_DB_HOST"], port=int(creds["GFI_DB_PORT"]),
    user=creds["GFI_DB_USER"], password=creds["GFI_DB_PASSWORD"],
    database=creds["GFI_DB_NAME"], connect_timeout=15, read_timeout=300)

# --- 1. Founding years (streamed to dodge server timeouts) ---
ss = conn.cursor(pymysql.cursors.SSCursor)
ss.execute("SELECT oib, godina_osnivanja FROM subjekti_26012026 WHERE godina_osnivanja BETWEEN 1850 AND 2024")
founding = {}
for oib, gy in ss:
    if oib:
        founding[oib] = int(gy)
ss.close()
print(f"founding years loaded: {len(founding):,}")

# --- 2. Per-year narrow extract from db_afs ---
cols = ["subjecttaxnoid","reportyear","nacerev21","b125","b131","b166","b168","employeecounteop","foreigncontrol"]
cur = conn.cursor()
frames = []
for y in range(2002, 2025):
    cur.execute(f"SELECT {','.join(cols)} FROM db_afs WHERE reportyear=%s", (y,))
    rows = cur.fetchall()
    frames.append(pd.DataFrame(rows, columns=cols))
print("rows per year:", {f.reportyear.iloc[0]: len(f) for f in frames if len(f)})
conn.close()
df = pd.concat(frames, ignore_index=True)
for c in ["b125","b131","b166","b168","employeecounteop","foreigncontrol"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
df["reportyear"] = df.reportyear.astype(int)
df["subjecttaxnoid"] = df.subjecttaxnoid.astype(str)
print(f"\ntotal firm-years pulled: {len(df):,}")
print("NACE section (nacerev21) distribution:\n", df.nacerev21.value_counts(dropna=False).head(30))

# --- 3. Build zombie flag (OECD/ICR) ---
df = df.drop_duplicates(["subjecttaxnoid","reportyear"])
df["EBIT"] = df.b125 - df.b131
df["interest"] = df.b166.fillna(0) + df.b168.fillna(0)
df["icr_lt1"] = (df.interest > 0) & (df.EBIT < df.interest)

# require an operating P&L
df = df[df.b125.notna()]
# exclude finance/insurance (K), utilities (D,E)
df = df[~df.nacerev21.isin(["K","D","E"])]
df = df[df.nacerev21.notna() & (df.nacerev21 != "")]

# age via founding year
n_before = df.subjecttaxnoid.nunique()
df["fy"] = df.subjecttaxnoid.map(founding)
match = df.fy.notna().mean()
print(f"\nfounding-year match rate (firm-years): {match:.1%}")
df = df[df.fy.notna()].copy()
df["age"] = df.reportyear - df.fy
df = df[df.age.between(0, 200)]

# 3 consecutive years of ICR<1 (this year + prior two, consecutive)
df = df.sort_values(["subjecttaxnoid","reportyear"])
g = df.groupby("subjecttaxnoid", sort=False)
df["py"]  = g.reportyear.shift(1)
df["py2"] = g.reportyear.shift(2)
df["icr_l1"] = g.icr_lt1.shift(1)
df["icr_l2"] = g.icr_lt1.shift(2)
consec = (df.reportyear - df.py == 1) & (df.py - df.py2 == 1)
df["icr3"] = df.icr_lt1 & (df.icr_l1 == True) & (df.icr_l2 == True) & consec
df["zombie"] = df.icr3 & (df.age >= 10)
df["foreign"] = df.foreigncontrol > 50

# --- 4. Aggregate ---
out = r"C:\Users\lsikic\projects\CroAIcon\outputs"
os.makedirs(out, exist_ok=True)

yearly = df.groupby("reportyear").agg(
    n_firms=("zombie","size"), n_zombie=("zombie","sum"),
    emp_total=("employeecounteop","sum"),
).copy()
yearly["emp_zombie"] = df[df.zombie].groupby("reportyear")["employeecounteop"].sum()
yearly["emp_zombie"] = yearly["emp_zombie"].fillna(0)
yearly["zombie_share"] = 100*yearly.n_zombie/yearly.n_firms
yearly["emp_share"] = 100*yearly.emp_zombie/yearly.emp_total
yearly = yearly.reset_index()
yearly.to_csv(out + r"\zombie_yearly.csv", index=False, encoding="utf-8-sig")

sec = df.groupby(["reportyear","nacerev21"]).agg(n=("zombie","size"), nz=("zombie","sum"))
sec["share"] = 100*sec.nz/sec.n
sec = sec.reset_index()
sec.to_csv(out + r"\zombie_by_sector_year.csv", index=False, encoding="utf-8-sig")

own = df.groupby(["reportyear","foreign"]).agg(n=("zombie","size"), nz=("zombie","sum"))
own["share"] = 100*own.nz/own.n
own.reset_index().to_csv(out + r"\zombie_by_ownership_year.csv", index=False, encoding="utf-8-sig")

pd.set_option("display.width", 140)
print("\n===== YEARLY ZOMBIE SERIES =====")
print(yearly[["reportyear","n_firms","n_zombie","zombie_share","emp_share"]].to_string(
    index=False, formatters={"zombie_share":"{:.1f}".format, "emp_share":"{:.1f}".format}))
print("\nSaved: zombie_yearly.csv, zombie_by_sector_year.csv, zombie_by_ownership_year.csv")
print("DONE")
