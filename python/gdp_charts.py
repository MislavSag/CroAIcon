"""Render the long-run GDP post charts in the house (matplotlib) style.

Same look as the live posts (python/sectors_charts.py): DejaVu Sans Mono, paper
background, title and subtitle in the top margin, hairline y-grid, source line
below. Reads the data tables written by scripts/update_gdp.R and writes the seven
PNGs straight into the draft folder.

  Run after the data build (scripts/update_gdp.R):
      uv run --extra charts python python/gdp_charts.py
"""

import os
import shutil

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# --- house palette (mirrors R/house_style.R and python/sectors_charts.py) ------
PAPER = "#F7F7F4"; INK = "#18181B"; MUTED = "#71717A"; HAIR = "#E6E6E1"
ACCENT = "#2348E5"; RISE = "#1C8F5A"; FALL = "#D2463A"
SURFACE = "#ECE9E1"; AMBER = "#C77B30"; PURPLE = "#6D4AA6"

mpl.rcParams.update({
    "font.family": "monospace", "font.monospace": ["DejaVu Sans Mono"],
    "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
    "text.color": INK, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": HAIR, "axes.linewidth": 1.0, "xtick.labelsize": 9, "ytick.labelsize": 9,
})

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAB = os.path.join(ROOT, "outputs", "tables")
FIG = os.path.join(ROOT, "outputs", "figures")
DRAFT = os.path.join(ROOT, "drafts", "2026-06-hrvatski-rast-dugi-niz")
os.makedirs(FIG, exist_ok=True)


def table(name):
    return pd.read_csv(os.path.join(TAB, name))


def titles(fig, ax, title, sub, src, tfs=12.5, top=0.80, bottom=0.14):
    ax.text(0, 1.20, title, transform=ax.transAxes, fontsize=tfs, weight="bold", color=INK)
    ax.text(0, 1.07, sub, transform=ax.transAxes, fontsize=9, color=MUTED)
    ax.text(0, -0.17, src, transform=ax.transAxes, fontsize=8, color=MUTED)
    fig.subplots_adjust(top=top, bottom=bottom)


def spines(ax, which="y"):
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(HAIR)
    ax.tick_params(length=0)
    ax.set_axisbelow(True)
    ax.grid(axis=which, color=HAIR, lw=0.8, zorder=0)


def save(fig, canonical, numbered):
    fig.savefig(os.path.join(FIG, canonical), dpi=170, bbox_inches="tight")
    plt.close(fig)
    if os.path.isdir(DRAFT):
        shutil.copyfile(os.path.join(FIG, canonical), os.path.join(DRAFT, numbered))


def pct_hr(v, decimals=0):
    """Croatian percent label: minus spelled, comma decimal, no stray dash."""
    sign = "plus " if v >= 0 else "minus "
    body = f"{abs(v):.{decimals}f}".replace(".", ",")
    return f"{sign}{body}%"


# --- load the series ----------------------------------------------------------
long = table("gdp_long.csv")
ribbon = table("gdp_ribbon.csv") if os.path.exists(os.path.join(TAB, "gdp_ribbon.csv")) else None
anchors = table("gdp_anchors.csv")
bars = table("gdp_growth_bars.csv")
raw_long = table("gdp_raw_long.csv") if os.path.exists(os.path.join(TAB, "gdp_raw_long.csv")) else None

ann_all = long[long.granularity == "annual"][["year", "index"]]
bench = long[long.granularity == "benchmark"][["year", "index"]]
YR_MAX = int(long.year.max())


def annual_grid(y0, y1):
    """Annual index on a complete year grid so unobserved gaps (wars) break the line."""
    a = ann_all[(ann_all.year >= y0) & (ann_all.year <= y1)]
    grid = pd.DataFrame({"year": range(int(y0), int(y1) + 1)})
    return grid.merge(a, on="year", how="left")


def idx_at(y):
    s = long[long.year == y]["index"]
    return float(s.iloc[0]) if len(s) else np.nan


WAR_GAPS = [(1914, 1919), (1940, 1946)]
RECON = (1990, 1995)


# ============================================================================ #
# 1. Hero: the whole arc, uncertainty drawn in.
# ============================================================================ #
def hero():
    YMAX = 158.0
    fig, ax = plt.subplots(figsize=(8.6, 5.0))

    for a, b in WAR_GAPS:
        ax.axvspan(a, b, color=SURFACE, zorder=0)

    if ribbon is not None and len(ribbon):
        ax.fill_between(ribbon.year, ribbon.lo, ribbon.hi, color=ACCENT, alpha=0.18, zorder=1)

    ax.axhline(100, color=HAIR, lw=1, zorder=1)

    # pre-1910 decadal benchmarks: dashed connector + hollow circles
    first_ann = ann_all.nsmallest(1, "year")
    dash = pd.concat([bench, first_ann]).sort_values("year")
    ax.plot(dash.year, dash["index"], color=ACCENT, lw=1.2, ls=(0, (2, 2)), zorder=2)
    ax.scatter(bench.year, bench["index"], s=34, facecolor=PAPER, edgecolor=ACCENT,
               linewidths=1.2, zorder=4)

    ann = annual_grid(int(ann_all.year.min()), YR_MAX)
    soft = ann[ann.year <= 1951]
    firm = ann[ann.year >= 1952].copy()
    firm.loc[firm.year.between(*RECON), "index"] = np.nan
    recon = long[(long.year >= RECON[0]) & (long.year <= RECON[1])][["year", "index"]]

    ax.plot(soft.year, soft["index"], color=ACCENT, lw=1.6, zorder=3)
    ax.plot(firm.year, firm["index"], color=ACCENT, lw=2.4, zorder=3)
    ax.plot(recon.year, recon["index"], color=AMBER, lw=2.2, ls=(0, (4, 2)), zorder=3)

    # in-place flags for each soft spot
    def lab(x, y, t, c, ha="center"):
        ax.text(x, y * YMAX, t, color=c, fontsize=7.6, ha=ha, va="center", linespacing=0.95)

    lab(1885, 0.135, "desetljetne\nprocjene", MUTED)
    lab(1927, 0.30, "raspon procjena\n(izvori se razilaze)", ACCENT)
    ax.plot([1927, 1927], [0.225 * YMAX, 0.12 * YMAX], color=ACCENT, lw=0.6, zorder=2)
    for a, b in WAR_GAPS:
        lab((a + b) / 2, 0.96, "rat\n(rupa)", MUTED)
    lab(1948.5, 0.235, "samo\nTica", AMBER, ha="right")
    ax.plot([1950, 1950], [0.165 * YMAX, 0.135 * YMAX], color=AMBER, lw=0.6, zorder=2)
    lab(1997, 0.30, "rekonstruirano\n1991.–1995.", AMBER, ha="left")

    spines(ax)
    ax.set_xlim(1866, 2028)
    ax.set_ylim(0, YMAX)
    ax.set_yticks([0, 50, 100, 150])
    ax.set_xticks(range(1880, 2021, 20))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}"))
    titles(fig, ax,
           "Hrvatski BDP po stanovniku, 1870. do 2025.",
           "spojeni indeks, 2015. = 100  ·  oblik je siguran, dubine nisu  ·  nesigurnost je ucrtana u graf",
           "Izvor: Eurostat, Maddison 2023, Tica (2004) / Good 1994  ·  pojas = raspon ranih procjena, sive rupe = ratne godine bez podataka")
    save(fig, "gdp_long_index.png", "gdp_1_long_index.png")


# ============================================================================ #
# 2. Growth by era: horizontal bars.
# ============================================================================ #
def growth_bars():
    d = bars.iloc[::-1].reset_index(drop=True)  # chronological order top-to-bottom
    colors = [RISE if p else FALL for p in d.positive]
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    ax.barh(d.era, d.cagr, color=colors, height=0.62, zorder=3)
    for y, v in enumerate(d.cagr):
        ax.text(v + (0.25 if v >= 0 else -0.25), y, pct_hr(v, 1),
                va="center", ha="left" if v >= 0 else "right", fontsize=8.5, color=INK)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(HAIR)
    ax.tick_params(length=0)
    ax.axvline(0, color=INK, lw=1)
    ax.grid(axis="x", color=HAIR, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.set_xlim(-9.5, 7.5)
    ax.set_xticks([])
    titles(fig, ax,
           "Najbrži rast pod socijalizmom, dva razdoblja pada",
           "prosječni godišnji realni rast BDP-a po stanovniku, po razdoblju",
           "Izvor: spojeni niz (Eurostat, Maddison, Tica)  ·  zeleno rast, crveno pad",
           tfs=12)
    fig.subplots_adjust(left=0.16)
    save(fig, "gdp_growth_eras.png", "gdp_2_growth_eras.png")


# ============================================================================ #
# helper for the simple zoom charts (prewar, socialism, crisis2)
# ============================================================================ #
def zoom(y0, y1, canonical, numbered, title, sub, src, bands=(),
         band_labels=(), benchmarks=False, with_ribbon=False):
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    for a, b in bands:
        ax.axvspan(a, b, color=SURFACE, zorder=0)
    for bl in band_labels:
        x, t = bl[0], bl[1]
        yy = bl[2] if len(bl) > 2 else 0.97
        ax.text(x, yy, t, transform=ax.get_xaxis_transform(), ha="center", va="top",
                fontsize=7.6, color=MUTED, linespacing=0.95)

    if with_ribbon and ribbon is not None:
        r = ribbon[(ribbon.year >= y0) & (ribbon.year <= y1)]
        ax.fill_between(r.year, r.lo, r.hi, color=ACCENT, alpha=0.18, zorder=1)

    if benchmarks:
        b = bench[(bench.year >= y0) & (bench.year <= y1)]
        first_ann = ann_all[ann_all.year >= y0].nsmallest(1, "year")
        dash = pd.concat([b, first_ann]).sort_values("year")
        ax.plot(dash.year, dash["index"], color=ACCENT, lw=1.2, ls=(0, (2, 2)), zorder=2)
        ax.scatter(b.year, b["index"], s=30, facecolor=PAPER, edgecolor=ACCENT,
                   linewidths=1.1, zorder=4)

    ann = annual_grid(y0, y1)
    soft = ann[ann.year <= 1951]
    firm = ann[ann.year >= 1952]
    if len(soft):
        ax.plot(soft.year, soft["index"], color=ACCENT, lw=1.7, zorder=3)
    if len(firm):
        ax.plot(firm.year, firm["index"], color=ACCENT, lw=2.4, zorder=3)

    spines(ax)
    ax.set_xlim(y0 - (y1 - y0) * 0.02, y1 + (y1 - y0) * 0.03)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}"))
    titles(fig, ax, title, sub, src)
    save(fig, canonical, numbered)


# ============================================================================ #
# 5. The 1990s, depth uncertainty drawn in.
# ============================================================================ #
def crisis1():
    y0, y1, tr_year = 1984, 2003, 1993
    trough = idx_at(tr_year)
    fig, ax = plt.subplots(figsize=(7.6, 4.2))

    ax.axvspan(RECON[0], RECON[1], color=SURFACE, zorder=0)
    ax.text((RECON[0] + RECON[1]) / 2, 0.96, "rekonstruirano", transform=ax.get_xaxis_transform(),
            ha="center", va="top", fontsize=7.8, color=MUTED)

    # short faint guides off each candidate peak, so the three drop heights show
    for _, r in anchors.iterrows():
        ax.plot([r.peak_year, RECON[0]], [r.peak_index, r.peak_index],
                color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)

    ann = annual_grid(y0, y1)
    firm = ann.copy()
    firm.loc[firm.year.between(*RECON), "index"] = np.nan
    recon = long[(long.year >= RECON[0]) & (long.year <= RECON[1])][["year", "index"]]
    ax.plot(firm.year, firm["index"], color=ACCENT, lw=2.4, zorder=3)
    ax.plot(recon.year, recon["index"], color=AMBER, lw=2.3, ls=(0, (4, 2)), zorder=3)

    ax.scatter(anchors.peak_year, anchors.peak_index, s=36, facecolor=PAPER,
               edgecolor=ACCENT, linewidths=1.2, zorder=4)
    for _, r in anchors.iterrows():
        ax.annotate(str(int(r.peak_year)), (r.peak_year, r.peak_index),
                    textcoords="offset points", xytext=(0, 7), ha="center",
                    fontsize=7.6, color=MUTED)
    ax.scatter([tr_year], [trough], s=44, color=FALL, zorder=5)
    ax.text(tr_year, trough - 1.0, "dno 1993.", ha="center", va="top", fontsize=8.0, color=FALL)

    # depth stack in the open lower-left: the fall depends on the peak you pick
    A = {int(r.peak_year): r.fall_pct for _, r in anchors.iterrows()}
    ax.text(y0 + 0.3, 73.5, "pad od vrha do dna 1993.", fontsize=7.8, color=INK, weight="bold")
    ax.text(y0 + 0.3, 69.0, f"vrh 1986   {pct_hr(A[1986])}", fontsize=8.2, color=INK)
    ax.text(y0 + 0.3, 64.5, f"vrh 1989   {pct_hr(A[1989])}   (Miljković)", fontsize=8.2, color=INK)
    ax.text(y0 + 0.3, 60.0, f"vrh 1990   {pct_hr(A[1990])}", fontsize=8.2, color=INK)

    spines(ax)
    ax.set_xlim(y0 - 0.6, y1 + 0.6)
    ax.set_ylim(48, 92)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}"))
    titles(fig, ax,
           "Prva kriza, smjer siguran a dubina nije",
           "indeks BDP-a po stanovniku  ·  pad ovisi o tome gdje stavite vrh",
           "Spojeni indeks, 2015. = 100. Maddison, PWT i Svjetska banka dijele isti izvor, pa potvrđuju smjer, ne dubinu.")
    save(fig, "gdp_zoom_crisis1.png", "gdp_5_zoom_crisis1.png")


# ============================================================================ #
# 7. Raw multi-source panel: each series in its own unit/base year.
# ============================================================================ #
def raw_panels():
    if raw_long is None:
        return
    order = [
        "Eurostat (EUR, 1995+)", "Maddison (2011 int$, 1952+)",
        "PWT 10.01 (2017 US$, 1950+)", "World Bank (2015 US$, 1990+)",
        "Tica (indeks, 1910-1989)",
    ]
    present = [s for s in order if s in set(raw_long.source)]
    fig, axes = plt.subplots(3, 2, figsize=(8.4, 6.2))
    axes = axes.ravel()
    for ax, src in zip(axes, present):
        d = raw_long[raw_long.source == src].sort_values("year")
        ax.axvspan(1991, 1995, color=SURFACE, zorder=0)
        ax.plot(d.year, d.value, color=ACCENT, lw=1.9, zorder=3)
        for s in ["top", "right"]:
            ax.spines[s].set_visible(False)
        for s in ["left", "bottom"]:
            ax.spines[s].set_color(HAIR)
        ax.tick_params(length=0, labelsize=8)
        ax.set_axisbelow(True)
        ax.grid(axis="y", color=HAIR, lw=0.7, zorder=0)
        ax.set_title(src, fontsize=8.5, weight="bold", color=INK, loc="left", pad=4)
        ax.set_yticklabels([])
    for ax in axes[len(present):]:
        ax.set_visible(False)
    fig.suptitle("Isti oblik, više izvora", x=0.06, y=1.005, ha="left",
                 fontsize=12.5, weight="bold", color=INK)
    fig.text(0.06, 0.965, "svaki sirovi niz u vlastitoj jedinici i baznoj godini  ·  pad 1990-ih u svima",
             ha="left", fontsize=9, color=MUTED)
    fig.text(0.06, 0.01, "Izvor: Eurostat, Maddison 2023, PWT 10.01, Svjetska banka  ·  siva traka = 1991.–1995.",
             ha="left", fontsize=8, color=MUTED)
    fig.subplots_adjust(top=0.90, bottom=0.06, hspace=0.45, wspace=0.12)
    save(fig, "gdp_raw_panels.png", "gdp_7_raw_panels.png")


# ============================================================================ #
hero()
growth_bars()
zoom(1870, 1952, "gdp_zoom_prewar.png", "gdp_3_zoom_prewar.png",
     "Prije 1952. nisko, ravno, isprekidano",
     "indeks BDP-a po stanovniku  ·  desetljetne točke do 1910., ratne rupe",
     "Spojeni indeks, 2015. = 100. Pojas = raspon ranih procjena.",
     bands=WAR_GAPS, band_labels=[(1916.5, "rat\n(rupa)"), (1943, "rat\n(rupa)")],
     benchmarks=True, with_ribbon=True)
zoom(1949, 1986, "gdp_zoom_socialism.png", "gdp_4_zoom_socialism.png",
     "Socijalizam diže liniju, pa zastoj 1980-ih",
     "indeks BDP-a po stanovniku, 1949. do 1986.",
     "Spojeni indeks, 2015. = 100.",
     bands=[(1949, 1952), (1980, 1986)],
     band_labels=[(1950.5, "Informbiro"), (1983, "zastoj\n1980-ih", 0.42)])
crisis1()
zoom(2008, 2025, "gdp_zoom_crisis2.png", "gdp_6_zoom_crisis2.png",
     "Druga kriza pa COVID, plitko, dugo, pa uzlet",
     "indeks BDP-a po stanovniku, 2008. do 2025.",
     "Spojeni indeks, 2015. = 100.",
     bands=[(2009, 2014), (2019.5, 2020.5)],
     band_labels=[(2011.5, "financijska\nkriza"), (2020, "COVID")])
raw_panels()
print("OK -- 7 GDP charts ->", DRAFT)
