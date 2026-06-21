# Charts for "Zagreb knjizi profit, ostatak zemlje radi". Reads outputs/tables/zagreb_profit_shares.csv.
import pandas as pd, os
import matplotlib as mpl, matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

PAPER="#F7F7F4"; INK="#18181B"; MUTED="#71717A"; HAIR="#E6E6E1"
ACCENT="#2348E5"; RISE="#1C8F5A"; FALL="#D2463A"; SURFACE="#ECE9E1"; AMBER="#C77B30"
mpl.rcParams.update({"font.family":"monospace","font.monospace":["DejaVu Sans Mono"],
    "figure.facecolor":PAPER,"axes.facecolor":PAPER,"savefig.facecolor":PAPER,
    "text.color":INK,"axes.labelcolor":INK,"xtick.color":MUTED,"ytick.color":MUTED,
    "axes.edgecolor":HAIR,"axes.linewidth":1.0,"xtick.labelsize":9,"ytick.labelsize":9})
OUT=r"C:\Users\lsikic\projects\CroAIcon\outputs\figures"; os.makedirs(OUT,exist_ok=True)
df=pd.read_csv(r"C:\Users\lsikic\projects\CroAIcon\outputs\tables\zagreb_profit_shares.csv")
SRC="Izvor: FINA GFI (db_afs), izracun AI.econ"

def titles(fig,ax,title,sub,src,tfs=12.5):
    ax.text(0,1.20,title,transform=ax.transAxes,fontsize=tfs,weight="bold",color=INK)
    ax.text(0,1.07,sub,transform=ax.transAxes,fontsize=9,color=MUTED)
    ax.text(0,-0.17,src,transform=ax.transAxes,fontsize=8,color=MUTED)
    fig.subplots_adjust(top=0.80,bottom=0.14)
def spines(ax,which="y"):
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    for s in ["left","bottom"]: ax.spines[s].set_color(HAIR)
    ax.tick_params(length=0); ax.set_axisbelow(True); ax.grid(axis=which,color=HAIR,lw=0.8,zorder=0)

a=df[(df["sample"]=="all") & (df["year"]>=2008)].sort_values("year")

# ---- Chart 1: three share lines, 2008-2024 (the gap = headquarters effect) ----
fig,ax=plt.subplots(figsize=(8.4,4.7))
ax.axvspan(2009,2014,color=SURFACE,zorder=0)
ax.plot(a.year,a.profit_share,color=ACCENT,lw=2.6,zorder=4)               # profit
ax.plot(a.year,a.rev_share,color=AMBER,lw=1.8,ls=(0,(4,2)),zorder=3)      # revenue (faint, dashed)
ax.plot(a.year,a.emp_share,color=INK,lw=2.2,zorder=3)                     # jobs
# shade the profit-over-jobs gap
ax.fill_between(a.year,a.emp_share,a.profit_share,where=a.profit_share>=a.emp_share,
                color=ACCENT,alpha=0.08,zorder=1)
spines(ax); ax.set_xlim(2008,2026.4); ax.set_ylim(30,75)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}%"))
def lab(y,c,t): ax.text(2024.3,y,t,color=c,fontsize=8.5,va="center")
lab(a.profit_share.iloc[-1]+2.5,ACCENT,"dobit")
lab(a.rev_share.iloc[-1],AMBER,"prihod")
lab(a.emp_share.iloc[-1]-1.5,INK,"zaposleni")
titles(fig,ax,"Zagreb knjizi pola dobiti, a radi trecinu posla",
       "udio Grada Zagreba u ukupnoj dobiti, prihodu i zaposlenosti (%), 2008.-2024.",
       SRC+"  ·  siva traka = recesija 2009.-2014.  ·  2024. preliminarno")
fig.savefig(OUT+r"\zagreb_1_shares.png",dpi=170,bbox_inches="tight"); plt.close(fig)

# ---- Chart 2: 2023 staircase, Zagreb share by measure ----
r=a[a.year==2023].iloc[0]
labels=["Zaposleni","Poslovni prihod","Dobit"]
vals=[r.emp_share,r.rev_share,r.profit_share]
cols=[INK,AMBER,ACCENT]
fig,ax=plt.subplots(figsize=(8.2,3.7))
ax.barh(range(3),vals,color=cols,height=0.62,zorder=3)
for i,v in enumerate(vals):
    ax.text(v+1,i,f"{v:.0f}%",va="center",ha="left",fontsize=11,weight="bold",color=INK)
ax.set_yticks(range(3)); ax.set_yticklabels(labels,fontsize=10,color=INK)
ax.invert_yaxis()
for s in ["top","right","left"]: ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(HAIR); ax.tick_params(length=0)
ax.grid(axis="x",color=HAIR,lw=0.8,zorder=0); ax.set_axisbelow(True)
ax.xaxis.set_major_formatter(FuncFormatter(lambda v,_:f"{v:.0f}%")); ax.set_xlim(0,80)
ax.axvline(50,color=MUTED,lw=0.9,ls=(0,(2,2)),zorder=2)
titles(fig,ax,"Stepenice sjedista: sto je veca mjera, to veci Zagreb (2023.)",
       "udio Grada Zagreba: od radnih mjesta, preko prihoda, do dobiti",SRC,tfs=12)
fig.subplots_adjust(left=0.22,top=0.78,bottom=0.16)
fig.savefig(OUT+r"\zagreb_2_staircase.png",dpi=170,bbox_inches="tight"); plt.close(fig)
print("OK — 2 charts in",OUT)
