"""Charts for the sector net-margin growth post."""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


PAPER = "#F7F7F4"
INK = "#18181B"
MUTED = "#71717A"
HAIR = "#E6E6E1"
ACCENT = "#2348E5"
RISE = "#1C8F5A"
SURFACE = "#ECE9E1"

MIN_REVENUE_2024 = 1_000_000_000
POST_SLUG = "2026-06-rast-marzi-po-sektorima"

SECTOR_LABELS = {
    "R": "Umjetnost i rekreacija",
    "M": "Stručne djelatnosti",
    "E": "Vodoopskrba",
    "L": "Nekretnine",
    "H": "Prijevoz i skladištenje",
    "J": "Informacije i komunikacije",
    "D": "Energetika",
    "I": "Smještaj i ugostiteljstvo",
    "F": "Građevinarstvo",
    "G": "Trgovina",
    "C": "Prerađivačka industrija",
    "A": "Poljoprivreda",
    "N": "Administrativne usluge",
    "Q": "Zdravstvo",
    "S": "Ostale usluge",
}


def project_root() -> Path:
    path = Path.cwd().resolve()
    for candidate in [path, *path.parents]:
        if (candidate / "_quarto.yml").exists() and (candidate / "CroAIcon.Rproj").exists():
            return candidate
    raise RuntimeError("Cannot locate CroAIcon project root.")


ROOT = project_root()
TABLE = ROOT / "outputs" / "tables" / "sector_margin_growth_2021_2024.csv"
FIG_DIR = ROOT / "outputs" / "figures"
POST_DIR = ROOT / "posts" / POST_SLUG
SRC = "Izvor: FINA GFI, izračun AI.econ"


def setup_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "monospace",
            "font.monospace": ["DejaVu Sans Mono"],
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "savefig.facecolor": PAPER,
            "text.color": INK,
            "axes.labelcolor": INK,
            "xtick.color": MUTED,
            "ytick.color": INK,
            "axes.edgecolor": HAIR,
            "axes.linewidth": 1.0,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
        }
    )


def titles(fig: plt.Figure, ax: plt.Axes, title: str, subtitle: str) -> None:
    ax.text(0, 1.17, title, transform=ax.transAxes, fontsize=12.5, weight="bold", color=INK)
    ax.text(0, 1.07, subtitle, transform=ax.transAxes, fontsize=9, color=MUTED)
    ax.text(0, -0.16, SRC, transform=ax.transAxes, fontsize=8, color=MUTED)
    fig.subplots_adjust(top=0.80, bottom=0.15, left=0.30, right=0.96)


def save_margin_growth_chart() -> None:
    df = pd.read_csv(TABLE)
    df = df[df["included_main"]].copy()
    df = df[df["revenue_2024"] >= MIN_REVENUE_2024].copy()
    df["label"] = df["sector"].map(SECTOR_LABELS).fillna(df["sector_name"])
    df = df.sort_values("margin_change_pp", ascending=False).head(10)
    df = df.sort_values("margin_change_pp", ascending=True)

    colors = [ACCENT if sector == "R" else RISE for sector in df["sector"]]

    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.barh(df["label"], df["margin_change_pp"], color=colors, height=0.64, zorder=3)
    ax.axvline(0, color=HAIR, lw=1)
    ax.grid(axis="x", color=HAIR, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(HAIR)
    ax.tick_params(length=0)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:+.0f}"))
    ax.set_xlim(0, max(8.4, df["margin_change_pp"].max() + 0.9))

    for y_pos, value in enumerate(df["margin_change_pp"]):
        ax.text(value + 0.12, y_pos, f"+{value:.1f} p.b.", va="center", ha="left", fontsize=8.5)

    titles(
        fig,
        ax,
        "Najveći skok marže sjedi u rekreaciji",
        "promjena agregatne neto marže po sektoru, 2021. do 2024. (postotni bodovi)",
    )

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    POST_DIR.mkdir(parents=True, exist_ok=True)
    for output in [
        FIG_DIR / "sector_margin_growth_bars.png",
        POST_DIR / "sector_margin_growth_bars.png",
    ]:
        fig.savefig(output, dpi=170, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    setup_style()
    save_margin_growth_chart()
    print("OK - saved sector_margin_growth_bars.png")


if __name__ == "__main__":
    main()
