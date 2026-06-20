import pymysql, pandas as pd, os
creds={}
for line in open(r"C:\Users\lsikic\projects\CroAIcon\.env",encoding="utf-8"):
    line=line.strip()
    if line and not line.startswith("#") and "=" in line:
        k,v=line.split("=",1); creds[k.strip()]=v.strip()
conn=pymysql.connect(host=creds["GFI_DB_HOST"],port=int(creds["GFI_DB_PORT"]),
    user=creds["GFI_DB_USER"],password=creds["GFI_DB_PASSWORD"],database=creds["GFI_DB_NAME"],
    connect_timeout=15,read_timeout=300); cur=conn.cursor()

rows=[]
for Y in range(2002,2025):
    cur.execute("""SELECT nacerev21, COUNT(*) n_firms,
                          SUM(COALESCE(employeecounteop,0)) emp_sum,
                          SUM(CASE WHEN employeecounteop>0 THEN 1 ELSE 0 END) n_with_emp
                   FROM db_afs WHERE reportyear=%s GROUP BY nacerev21""",(Y,))
    for sec,n,emp,nw in cur.fetchall():
        rows.append((Y, sec, int(n), float(emp or 0), int(nw or 0)))
conn.close()
df=pd.DataFrame(rows,columns=["year","sector","n_firms","emp_sum","n_with_emp"])
# keep real NACE sections (single uppercase letter)
df=df[df.sector.notna() & df.sector.str.match(r"^[A-U]$", na=False)]

names={'A':'Poljoprivreda','B':'Rudarstvo','C':'Prerađivačka ind.','D':'Energetika','E':'Vodoopskrba',
 'F':'Građevinarstvo','G':'Trgovina','H':'Prijevoz i skladišt.','I':'Smještaj i ugostit.',
 'J':'Informacije i komun.','K':'Financije i osig.','L':'Poslovanje nekretn.','M':'Stručne djelatnosti',
 'N':'Administrativne usl.','O':'Javna uprava','P':'Obrazovanje','Q':'Zdravstvo','R':'Umjetnost i rekreac.',
 'S':'Ostale uslužne','T':'Kućanstva','U':'Eksteritorijalne'}
df["sector_name"]=df.sector.map(names).fillna(df.sector)

out=r"C:\Users\lsikic\projects\CroAIcon\outputs\tables"; os.makedirs(out,exist_ok=True)
df.to_csv(out+r"\sectors_firms_employment.csv",index=False,encoding="utf-8-sig")

tot=df.groupby("year").agg(firms=("n_firms","sum"),emp=("emp_sum","sum"),
                            firms_emp=("n_with_emp","sum")).reset_index()
pd.set_option("display.width",150)
print("=== TOTALS BY YEAR ===")
print(tot.assign(emp=tot.emp.round(0)).to_string(index=False))
print("\n=== FIRMS by sector: 2008 vs 2024 (top by 2024) ===")
piv=df.pivot_table(index="sector_name",columns="year",values="n_firms",aggfunc="sum")
print(piv[[2008,2014,2024]].sort_values(2024,ascending=False).head(14).astype("Int64").to_string())
print("\n=== EMPLOYMENT by sector: 2008 vs 2024 (top by 2024) ===")
pe=df.pivot_table(index="sector_name",columns="year",values="emp_sum",aggfunc="sum")
print(pe[[2008,2014,2024]].sort_values(2024,ascending=False).head(14).round(0).astype("Int64").to_string())
print("\nsaved sectors_firms_employment.csv  | DONE")
