"""House-style figures for annual history and the latest matched calendar period."""
from __future__ import annotations
import json
import shutil

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pressure_voice_charts import PALETTE, ROOT, OUT, POST, hr


def finish(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=190)
    plt.close(fig)
    shutil.copyfile(OUT / name, POST / name)


def bars(ax, table, labels, limit=65):
    y = np.arange(len(table))
    for offset, field, color in [(-.17, "nights_share_pct", PALETTE["muted"]), (.17, "mention_share_pct", PALETTE["accent"])]:
        ax.barh(y + offset, table[field], height=.28, color=color)
        for i, value in enumerate(table[field]):
            ax.text(value + .8, i + offset, hr(value) + "%", va="center", fontsize=8)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, limit)
    ticks = list(range(0, limit, 10))
    ax.set_xticks(ticks, [f"{tick}%" for tick in ticks])
    ax.tick_params(length=0, labelsize=8)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color=PALETTE["hair"], linewidth=.6)
    for spine in ax.spines.values():
        spine.set_visible(False)


def main():
    f = json.loads((ROOT / "outputs/facts/pressure_voice_history.json").read_text(encoding="utf-8"))
    groups = pd.read_csv(ROOT / "outputs/tables/pressure_voice_history_groups.csv", dtype={"period": str})
    groups = groups[groups.variant.eq("main")]
    mpl.rcParams.update({"font.family": "DejaVu Sans Mono", "font.size": 9, "text.color": PALETTE["ink"],
        "axes.facecolor": PALETTE["paper"], "figure.facecolor": PALETTE["paper"], "savefig.facecolor": PALETTE["paper"]})
    annual = groups[groups.period.isin([str(y) for y in f["annual_years"]])]
    fig, axes = plt.subplots(1, 2, figsize=(9, 5.4))
    fig.subplots_adjust(left=.08, right=.96, top=.69, bottom=.17, wspace=.23)
    for ax, group, title in zip(axes, ["G2", "G1"], ["Dvanaest malih destinacija", "Split i Dubrovnik"]):
        subset = annual[annual.group.eq(group)].sort_values("period")
        bars(ax, subset, [str(y) + "." for y in subset.period], limit=65)
        ax.set_title(title, loc="left", fontsize=9, fontweight="bold", pad=14)
    title = "Mala mjesta imaju veći udio noćenja nego spominjanja" if f["annual_g2_direction_consistent"] else "Noćenja i medijska pažnja kroz pet godina"
    fig.text(.035, .94, title, fontsize=11, weight="bold")
    fig.text(.035, .885, f"Pune godine · ista {f['annual_frame_n']} mjesta · {f['start_year']}. do {f['end_year']}.", fontsize=9, color=PALETTE["muted"])
    fig.text(.08, .80, "■ Udio noćenja", fontsize=9, color=PALETTE["muted"])
    fig.text(.43, .80, "■ Udio medijskih spominjanja", fontsize=9, color=PALETTE["accent"])
    fig.text(.035, .09, "Svaka godina uspoređuje noćenja i spominjanja istih mjesta.", fontsize=7, color=PALETTE["muted"])
    fig.text(.035, .047, "Izvori · DZS, komercijalni smještaj; Determ, turističke teme na web portalima.", fontsize=7, color=PALETTE["muted"])
    finish(fig, "pressure_voice_history_01_years.png")

    units = pd.read_csv(ROOT / "outputs/tables/pressure_voice_history_latest_annual.csv")
    d = units[units.group.isin(["G1", "G2"])].sort_values("nights_per_resident", ascending=False)
    fig, ax = plt.subplots(figsize=(8.4, 5.5))
    fig.subplots_adjust(left=.22, right=.96, top=.76, bottom=.15)
    ax.barh(range(len(d)), d.nights_per_resident, height=.65, color=[PALETTE["accent"] if g == "G2" else PALETTE["muted"] for g in d.group])
    ax.set_yticks(range(len(d)), d.display_name, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, 2700)
    ax.set_xticks([0, 500, 1000, 1500, 2000, 2500], ["0", "500", "1.000", "1.500", "2.000", "2.500"])
    ax.tick_params(length=0, labelsize=8)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color=PALETTE["hair"], linewidth=.6)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for y, value in enumerate(d.nights_per_resident):
        ax.text(value + 28, y, f"{value:,.0f}".replace(",", "."), va="center", fontsize=8)
    fig.text(.035, .94, "Funtana prednjači po noćenjima na stanovnika", fontsize=11, weight="bold")
    fig.text(.035, .885, f"Godišnja noćenja po stanovniku · {f['end_year']}.", fontsize=9, color=PALETTE["muted"])
    fig.text(.035, .84, "Cijelo područje grada ili općine", fontsize=8, color=PALETTE["muted"])
    fig.text(.035, .08, f"Plavo · {f['high_intensity_n']} mjesta s najmanje {f['annual_group_threshold']} noćenja po stanovniku.", fontsize=7, color=PALETTE["muted"])
    fig.text(.035, .04, "Izvor · DZS, komercijalna noćenja i stanovništvo prema popisu.", fontsize=7, color=PALETTE["muted"])
    finish(fig, "pressure_voice_history_02_intensity.png")

    ytd = groups[groups.period.str.endswith("_ytd") & groups.group.eq("G1")].sort_values("period")
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    fig.subplots_adjust(left=.12, right=.96, top=.66, bottom=.23)
    bars(ax, ytd, [period[:4] + "." for period in ytd.period], limit=75)
    title = "Split i Dubrovnik privlače veći udio spominjanja" if ytd.mention_share_pct.gt(ytd.nights_share_pct).all() else "Split i Dubrovnik na početku godine"
    fig.text(.035, .94, title, fontsize=11, weight="bold")
    fig.text(.035, .875, f"Od siječnja do svibnja · usporedba istih {f['ytd_frame_n']} mjesta", fontsize=9, color=PALETTE["muted"])
    fig.text(.12, .76, "■ Udio noćenja", fontsize=9, color=PALETTE["muted"])
    fig.text(.44, .76, "■ Udio medijskih spominjanja", fontsize=9, color=PALETTE["accent"])
    fig.text(.035, .12, "Udjeli Splita i Dubrovnika u noćenjima i turističkim spominjanjima.", fontsize=7, color=PALETTE["muted"])
    fig.text(.035, .06, "Izvori · DZS, komercijalni smještaj; Determ, tekstovi na web portalima.", fontsize=7, color=PALETTE["muted"])
    finish(fig, "pressure_voice_history_03_recent.png")
    print("Three historical comparison charts saved.")


if __name__ == "__main__":
    main()
