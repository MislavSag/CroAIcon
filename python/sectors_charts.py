import pandas as pd, numpy as np, os
import matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

PAPER="#F7F7F4"; INK="#18181B"; MUTED="#71717A"; HAIR="#E6E6E1"
ACCENT="#2348E5"; RISE="#1C8F5A"; FALL="#D2463A"; SURFACE="#ECE9E1"; AMBER="#C77B30"; PURPLE="#6D4AA6"
mpl.rcParams.update({"font.family":"monospace","font.monospace":["DejaVu Sans Mono"],
    "figure.facecolor":PAPER,"axes.facecolor":PAPER,"savefig.facecolor":PAPER,
    "text.color":INK,"axes.labelcolor":INK,"xtick.color":MUTED,"ytick.color":MUTED,
    "axes.edgecolor":HAIR,"axes.linewidth":1.0,"xtick.labelsize":9,"ytick.labelsize":9})
OUT=r"C:\Users\lsikic\projects\CroAIcon\outputs\figures"; os.makedirs(OUT,exist_ok=True)
df=pd.read_csv(r"C:\Users\lsikic\projects\CroAIcon\outputs\tables\sectors_firms_employment.csv")
SRC="Izvor: FINA GFI (db_afs), izračun AI.econ"

def titles(fig,ax,title,sub,src,tfs=12.5):
    ax.text(0,1.20,title,transform=ax.transAxes,fontsize=tfs,weight="bold",color=INK)
    ax.text(0,1.07,sub,transform=ax.transAxes,fontsize=9,color=MUTED)
    ax.text(0,-0.17,src,transform=ax.transAxes,fontsize=8,color=MUTED)
    fig.subplots_adjust(top=0.80,bottom=0.14)
def spines(ax,which="y"):
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    for s in ["left","bottom"]: ax.spines[s].set_color(HAIR)
    ax.tick_params(length=0); ax.set_axisbelow(True); ax.grid(axis=which,color=HAIR,lw=0.8,zorder=0)
def endlabels(ax,series_map,x=2024.25):
    items=sorted(((n,y,c) for n,(y,c) in series_map.items()),key=lambda t:t[1])
    lo,hi=ax.get_ylim(); gap=(hi-lo)*0.05; ys=[t[1] for t in items]
    for i in range(1,len(ys)):
        if ys[i]-ys[i-1]<gap: ys[i]=ys[i-1]+gap
    for (n,_,c),yy in zip(items,ys): ax.text(x,yy,n,color=c,fontsize=8,va="center")

tot=df.groupby("year").agg(firms=("n_firms","sum"),emp=("emp_sum","sum")).reset_index()

# ---- Chart 1: index 2008=100, firms vs employment ----
b=tot.set_index("year"); base=b.loc[2008]
fig,ax=plt.subplots(figsize=(8.2,4.6))
ax.axvspan(2009,2014,color=SURFACE,zorder=0)
ax.axhline(100,color=HAIR,lw=1)
ax.plot(b.index,100*b.firms/base.firms,color=ACCENT,lw=2.4,zorder=3)
ax.plot(b.index,100*b.emp/base.emp,color=FALL,lw=2.4,zorder=3)
spines(ax); ax.set_xlim(2002,2025.6)
ax.text(2024.4,100*b.firms.iloc[-1]/base.firms,"broj\nfirmi",color=ACCENT,fontsize=8.5,va="center")
ax.text(2024.4,100*b.emp.iloc[-1]/base.emp,"zaposleni",color=FALL,fontsize=8.5,va="center")
ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}"))
titles(fig,ax,"U recesiji su firme rasle, a radna mjesta nestajala",
       "indeks, 2008. = 100  ·  broj firmi vs. ukupan broj zaposlenih u GFI bazi",
       SRC+"  ·  siva traka = recesija 2009.–2014.")
fig.savefig(OUT+r"\sectors_1_index.png",dpi=170,bbox_inches="tight"); plt.close(fig)

# helper: top sectors by 2024 value of a column
def topsec(col,k=6):
    last=df[df.year==2024].groupby("sector_name")[col].sum().sort_values(ascending=False)
    return list(last.head(k).index)
PAL=[ACCENT,FALL,RISE,AMBER,PURPLE,INK]

# ---- Chart 2: firms by sector ----
secs=topsec("n_firms")
fig,ax=plt.subplots(figsize=(8.4,4.7))
ax.axvspan(2009,2014,color=SURFACE,zorder=0)
sm={}
for i,s in enumerate(secs):
    d=df[df.sector_name==s].sort_values("year")
    ax.plot(d.year,d.n_firms/1000,color=PAL[i],lw=2,zorder=3)
    sm[s]=(d.n_firms.iloc[-1]/1000,PAL[i])
spines(ax); ax.set_xlim(2002,2031); endlabels(ax,sm)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}k"))
titles(fig,ax,"Rast usluga: stručne djelatnosti i turizam vode po broju firmi",
       "broj firmi po djelatnosti (tisuće), 6 najvećih u 2024.",SRC)
fig.savefig(OUT+r"\sectors_2_firms.png",dpi=170,bbox_inches="tight"); plt.close(fig)

# ---- Chart 3: employment by sector ----
secs=topsec("emp_sum")
fig,ax=plt.subplots(figsize=(8.4,4.7))
ax.axvspan(2009,2014,color=SURFACE,zorder=0)
sm={}
for i,s in enumerate(secs):
    d=df[df.sector_name==s].sort_values("year")
    ax.plot(d.year,d.emp_sum/1000,color=PAL[i],lw=2,zorder=3)
    sm[s]=(d.emp_sum.iloc[-1]/1000,PAL[i])
spines(ax); ax.set_xlim(2002,2031); endlabels(ax,sm)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}k"))
titles(fig,ax,"Građevinarstvo se srušilo, turizam udvostručio (zaposleni)",
       "ukupan broj zaposlenih po djelatnosti (tisuće), 6 najvećih u 2024.",SRC)
fig.savefig(OUT+r"\sectors_3_employment.png",dpi=170,bbox_inches="tight"); plt.close(fig)

# ---- Chart 4: % change in employment 2008 -> 2024 by sector ----
p=df.pivot_table(index="sector_name",columns="year",values="emp_sum",aggfunc="sum")
p=p[(p[2008]>5000)]
chg=(100*(p[2024]/p[2008]-1)).sort_values()
colors=[RISE if v>=0 else FALL for v in chg]
fig,ax=plt.subplots(figsize=(8.4,5.0))
ax.barh(chg.index,chg.values,color=colors,zorder=3,height=0.66)
for y,v in enumerate(chg.values):
    ax.text(v+(2 if v>=0 else -2),y,f"{v:+.0f}%",va="center",ha="left" if v>=0 else "right",fontsize=8.5,color=INK)
for s in ["top","right","left"]: ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(HAIR); ax.tick_params(length=0); ax.axvline(0,color=INK,lw=1)
ax.grid(axis="x",color=HAIR,lw=0.8,zorder=0); ax.set_axisbelow(True)
ax.xaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:+.0f}%")); ax.set_xlim(-62,195)
ax.set_xticks([-40,-20,0,20,40,60,80,100,120,140,160])
titles(fig,ax,"Tko je dobio, a tko izgubio radna mjesta, 2008.–2024.",
       "promjena ukupnog broja zaposlenih po djelatnosti (%)",SRC,tfs=12)
fig.subplots_adjust(left=0.22,top=0.82,bottom=0.13)
fig.savefig(OUT+r"\sectors_4_change.png",dpi=170,bbox_inches="tight"); plt.close(fig)
print("OK — 4 charts in",OUT)
