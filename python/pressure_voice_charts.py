"""Tourism and exploratory mention charts. Pressure C2/C3 still await labels."""
from __future__ import annotations
import json
import re
import shutil
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
PALETTE=dict(re.findall(r'(\w+)\s*=\s*"(#[A-Fa-f0-9]{6})"',(ROOT/"R/house_style.R").read_text(encoding="utf-8")))
OUT=ROOT/"outputs/figures"
POST=ROOT/"posts/2026-10-pritisak-bez-glasa"


def hr(v,digits=1):return f"{v:.{digits}f}".replace(".",",")


def attention_chart():
    f=json.loads((ROOT/"outputs/facts/pressure_voice_attention.json").read_text(encoding="utf-8"))
    if not f["preliminary_draft_measure_allowed"]:raise SystemExit("Exploratory mentions unavailable")
    d=pd.read_csv(ROOT/"outputs/tables/pressure_voice_attention_groups.csv")
    d=d[d.variant.eq("main_strict_no_repeated")].set_index("group").loc[["G2","G1","G3"]]
    fig,ax=plt.subplots(figsize=(8.4,4.7))
    fig.subplots_adjust(left=.24,right=.93,top=.70,bottom=.24)
    y=list(range(3))
    ax.barh([x-.16 for x in y],d.nights_share_pct,height=.27,color=PALETTE["muted"])
    ax.barh([x+.16 for x in y],d.mention_share_pct,height=.27,color=PALETTE["accent"])
    ax.set_yticks(y,["Dvanaest malih\ndestinacija","Split i Dubrovnik","Ostalih devet\npromatranih mjesta"],fontsize=8)
    ax.invert_yaxis();ax.set_xlim(0,65);ax.set_xticks([0,10,20,30,40,50,60],[f"{x}%" for x in [0,10,20,30,40,50,60]])
    ax.tick_params(length=0,labelsize=8);ax.set_axisbelow(True);ax.grid(axis="x",color=PALETTE["hair"],lw=.7)
    for spine in ax.spines.values():spine.set_visible(False)
    for i,r in enumerate(d.itertuples()):
        for offset,value in [(-.16,r.nights_share_pct),(.16,r.mention_share_pct)]:
            ax.text(value+.8,i+offset,hr(value)+"%",va="center",fontsize=9)
    fig.text(.04,.945,f"Dvanaest malih destinacija. {f['g2_nights_share_pct']:.0f}% noćenja, {f['g2_mention_share_pct']:.0f}% spominjanja",fontsize=11,weight="bold")
    fig.text(.04,.887,f"Udio u noćenjima i spominjanjima · {f['frame_units']} destinacije · kolovoz {f['year']}.",fontsize=8,color=PALETTE["muted"])
    fig.text(.24,.79,"■ Noćenja",fontsize=9,color=PALETTE["muted"])
    fig.text(.48,.79,"■ Medijska spominjanja",fontsize=9,color=PALETTE["accent"])
    fig.text(.04,.14,"Spominjanje · naziv mjesta uz riječi o turizmu i smještaju.",fontsize=7,color=PALETTE["muted"])
    fig.text(.04,.098,"Svako se mjesto broji jednom po članku.",fontsize=7,color=PALETTE["muted"])
    fig.text(.04,.055,"Izvori · DZS, komercijalna noćenja; Determ, tekstovi na web portalima.",fontsize=7,color=PALETTE["muted"])
    name="pressure_voice_02_attention.png";fig.savefig(OUT/name,dpi=170);plt.close(fig);shutil.copyfile(OUT/name,POST/name)


def main():
    facts=json.loads((ROOT/"outputs/facts/pressure_voice.json").read_text(encoding="utf-8"))
    if not facts["g0_passed"]:raise SystemExit("C1 needs G0")
    m=pd.read_csv(ROOT/"outputs/tables/pressure_voice_municipality.csv")
    d=m[m.group.isin(["G1","G2"])].sort_values("aug_tourists_per_resident_2025",ascending=False)
    mpl.rcParams.update({"font.family":"DejaVu Sans Mono","font.size":9,"text.color":PALETTE["ink"],
                         "axes.facecolor":PALETTE["paper"],"figure.facecolor":PALETTE["paper"],"savefig.facecolor":PALETTE["paper"]})
    fig,ax=plt.subplots(figsize=(8.4,4.7))
    fig.subplots_adjust(left=.22,right=.94,top=.77,bottom=.16)
    bars=ax.barh(range(len(d)),d.aug_tourists_per_resident_2025,height=.65,
                 color=[PALETTE["accent"] if x=="G2" else PALETTE["muted"] for x in d.group])
    labels=d.display_name.tolist()
    ax.set_yticks(range(len(d)),labels,fontsize=8);ax.invert_yaxis();ax.set_xlim(0,24)
    ax.set_xticks([0,5,10,15,20]);ax.tick_params(length=0,labelsize=8)
    ax.set_axisbelow(True);ax.grid(axis="x",color=PALETTE["hair"],lw=.7)
    for spine in ax.spines.values():spine.set_visible(False)
    for bar,r in zip(bars,d.itertuples()):
        ax.text(bar.get_width()+.23,bar.get_y()+bar.get_height()/2,hr(bar.get_width(),2 if r.display_name=="Split" else 1),va="center",fontsize=8)
    fig.text(.04,.945,"Male sredine imaju najviše gostiju po stanovniku",fontsize=12,weight="bold",ha="left")
    fig.text(.04,.89,f"Turisti po stanovniku na prosječan dan u kolovozu {facts['year']}.",fontsize=9,color=PALETTE["muted"])
    fig.text(.04,.847,"Cijelo administrativno područje grada ili općine",fontsize=8,color=PALETTE["muted"])
    fig.text(.04,.075,f"Plavo · {facts['g2_n_units']} mjesta s najmanje {facts['group_threshold']} godišnjih noćenja po stanovniku.",fontsize=7,color=PALETTE["muted"])
    fig.text(.04,.04,"Izvor · DZS, komercijalna noćenja i stanovništvo prema popisu.",fontsize=7,color=PALETTE["muted"])
    OUT.mkdir(parents=True,exist_ok=True);POST.mkdir(parents=True,exist_ok=True)
    name="pressure_voice_01_august.png";fig.savefig(OUT/name,dpi=170);plt.close(fig);shutil.copyfile(OUT/name,POST/name)
    attention_chart()
    print("C1 and exploratory mention comparison rendered. Pressure C2/C3 still await human validation.")


if __name__=="__main__":main()
