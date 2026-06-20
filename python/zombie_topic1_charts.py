import pandas as pd, numpy as np, os
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

PAPER="#F7F7F4"; INK="#18181B"; MUTED="#71717A"; HAIR="#E6E6E1"
ACCENT="#2348E5"; RISE="#1C8F5A"; FALL="#D2463A"; SURFACE="#ECE9E1"
mpl.rcParams.update({
    "font.family":"monospace", "font.monospace":["DejaVu Sans Mono"],
    "figure.facecolor":PAPER, "axes.facecolor":PAPER, "savefig.facecolor":PAPER,
    "text.color":INK, "axes.labelcolor":INK, "xtick.color":MUTED, "ytick.color":MUTED,
    "axes.edgecolor":HAIR, "axes.linewidth":1.0, "xtick.labelsize":9, "ytick.labelsize":9,
})
out=r"C:\Users\lsikic\projects\CroAIcon\outputs\figures"; os.makedirs(out,exist_ok=True)
yr=pd.read_csv(r"C:\Users\lsikic\projects\CroAIcon\outputs\zombie_yearly.csv"); yr=yr[yr.reportyear>=2004]
ys=yr.set_index("reportyear")
pct=FuncFormatter(lambda v,_:f"{v:.0f}%")
SRC="Izvor: FINA GFI (db_afs), izračun AI.econ"

def titles(fig,ax,title,sub,src,tfs=12.5):
    ax.text(0,1.20,title,transform=ax.transAxes,fontsize=tfs,weight="bold",color=INK)
    ax.text(0,1.07,sub,transform=ax.transAxes,fontsize=9,color=MUTED)
    ax.text(0,-0.17,src,transform=ax.transAxes,fontsize=8,color=MUTED)
    fig.subplots_adjust(top=0.80,bottom=0.14)

def spines(ax,xaxis=False):
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    for s in ["left","bottom"]: ax.spines[s].set_color(HAIR)
    ax.tick_params(length=0); ax.set_axisbelow(True)
    ax.grid(axis="x" if xaxis else "y",color=HAIR,lw=0.8,zorder=0)

# ---- Chart 1 ----
fig,ax=plt.subplots(figsize=(8.2,4.6))
ax.axvspan(2009,2014,color=SURFACE,zorder=0)
ax.plot(yr.reportyear,yr.zombie_share,color=ACCENT,lw=2.4,zorder=3)
ax.scatter([2012],[ys.loc[2012,"zombie_share"]],color=ACCENT,zorder=4,s=22)
spines(ax); ax.yaxis.set_major_formatter(pct)
ax.set_yticks([0,1,2,3]); ax.set_ylim(0,3.7); ax.set_xlim(2004,2024)
ax.set_xticks([2005,2008,2011,2014,2017,2020,2023]); ax.set_xticklabels(["2005","2008","2011","2014","2017","2020","2023"])
ax.text(2011.5,3.5,"Recesija 2009.–2014.",ha="center",va="top",fontsize=8.5,color=MUTED)
ax.annotate(f"vrhunac {ys.loc[2012,'zombie_share']:.1f}%",(2012,ys.loc[2012,"zombie_share"]),
            (2013.4,3.45),fontsize=8.5,color=INK,arrowprops=dict(arrowstyle="-",color=MUTED,lw=0.8))
ax.annotate(f"{ys.loc[2008,'zombie_share']:.1f}%",(2008,ys.loc[2008,"zombie_share"]),
            (2005.4,1.15),fontsize=8.5,color=MUTED)
titles(fig,ax,"Udio zombi-firmi u Hrvatskoj se udvostručio u dugoj recesiji",
       "% nefinancijskih poduzeća koja su zombiji (OECD/ICR: starost ≥10 g., ICR<1 tri godine zaredom)",
       SRC+"  ·  N≈50–150 tis. poduzeća/god.")
fig.savefig(out+r"\zombie_1_timeseries.png",dpi=170,bbox_inches="tight"); plt.close(fig)

# ---- Chart 2 ----
fig,ax=plt.subplots(figsize=(8.2,4.6))
ax.axvspan(2009,2014,color=SURFACE,zorder=0)
ax.plot(yr.reportyear,yr.zombie_share,color=ACCENT,lw=2.4,zorder=3)
ax.plot(yr.reportyear,yr.emp_share,color=FALL,lw=2.4,zorder=3)
spines(ax); ax.yaxis.set_major_formatter(pct)
ax.set_yticks([0,1,2,3,4,5]); ax.set_ylim(0,5.3); ax.set_xlim(2004,2025)
ax.set_xticks([2005,2008,2011,2014,2017,2020,2023]); ax.set_xticklabels(["2005","2008","2011","2014","2017","2020","2023"])
ax.text(2024.2,ys.loc[2024,"emp_share"],"udio\nzaposlenih",color=FALL,fontsize=8.5,va="center")
ax.text(2024.2,ys.loc[2024,"zombie_share"]-0.1,"udio\nfirmi",color=ACCENT,fontsize=8.5,va="center")
titles(fig,ax,"Zombiji drže više radnih mjesta nego što ih je samih",
       "udio zombija među nefinancijskim firmama vs. udio zaposlenih u njima",
       SRC+"  ·  zaposleni = employeecounteop")
fig.savefig(out+r"\zombie_2_employment.png",dpi=170,bbox_inches="tight"); plt.close(fig)

# ---- Chart 3 ----
sec=pd.read_csv(r"C:\Users\lsikic\projects\CroAIcon\outputs\zombie_by_sector_year.csv")
names={'A':'Poljoprivreda','C':'Prerađivačka ind.','F':'Građevinarstvo','G':'Trgovina','H':'Prijevoz i skladišt.',
 'I':'Smještaj i ugostit.','J':'Informacije i komun.','L':'Poslovanje nekretn.','M':'Stručne djelatnosti',
 'N':'Administrativne usl.','Q':'Zdravstvo','R':'Umjetnost i rekreac.','S':'Ostale uslužne'}
pk=sec[sec.reportyear.between(2012,2015)].groupby('nacerev21').agg(n=('n','sum'),nz=('nz','sum'))
pk['share']=100*pk.nz/pk.n; pk=pk[(pk.n>8000)&pk.index.isin(names)].sort_values('share')
lab=[names[i] for i in pk.index]; colors=[ACCENT if i in ('G','C','H') else MUTED for i in pk.index]
fig,ax=plt.subplots(figsize=(8.4,4.9))
ax.barh(lab,pk.share,color=colors,zorder=3,height=0.64)
for y,s in enumerate(pk.share): ax.text(s+0.07,y,f"{s:.1f}%",va="center",fontsize=8.5,color=INK)
spines(ax,xaxis=True); ax.spines["left"].set_visible(False)
ax.xaxis.set_major_formatter(pct); ax.set_xlim(0,5.3); ax.set_xticks([0,1,2,3,4,5])
titles(fig,ax,"Zombiji se gnijezde u trgovini i industriji, ne u nekretninama",
       "udio zombi-firmi po djelatnosti, prosjek vrhunca recesije 2012.–2015.",
       SRC+"  ·  NKD 2007. područja, >8 tis. firmi-god.",tfs=11.5)
fig.subplots_adjust(left=0.21,top=0.80,bottom=0.14)
fig.savefig(out+r"\zombie_3_sector.png",dpi=170,bbox_inches="tight"); plt.close(fig)
print("OK; charts in",out)
