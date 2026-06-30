"""Charts for the sector net-margin growth post."""

from __future__ import annotations

import textwrap
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

MIN_REVENUE_2024_SECTION = 1_000_000_000
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

DETAIL_CHARTS = {
    "nkd2": {
        "table": "sector_margin_growth_nkd2_2021_2024.csv",
        "file": "sector_margin_growth_nkd2_bars.png",
        "title": "Na dvije znamenke vode upravljanje i klađenje",
        "subtitle": "promjena agregatne neto marže po NKD odjeljcima, 2021. do 2024. (postotni bodovi)",
        "top_n": 8,
        "label_width": 38,
        "left": 0.43,
    },
    "nkd3": {
        "table": "sector_margin_growth_nkd3_2021_2024.csv",
        "file": "sector_margin_growth_nkd3_bars.png",
        "title": "Na tri znamenke vodi električna oprema",
        "subtitle": "promjena agregatne neto marže po NKD skupinama, 2021. do 2024. (postotni bodovi)",
        "top_n": 8,
        "label_width": 42,
        "left": 0.47,
    },
    "nkd4": {
        "table": "sector_margin_growth_nkd4_2021_2024.csv",
        "file": "sector_margin_growth_nkd4_bars.png",
        "title": "Na četiri znamenke vode elektromotori",
        "subtitle": "promjena agregatne neto marže po NKD razredima, 2021. do 2024. (postotni bodovi)",
        "top_n": 8,
        "label_width": 42,
        "left": 0.47,
    },
}


def project_root() -> Path:
    path = Path.cwd().resolve()
    for candidate in [path, *path.parents]:
        if (candidate / "_quarto.yml").exists() and (candidate / "CroAIcon.Rproj").exists():
            return candidate
    raise RuntimeError("Cannot locate CroAIcon project root.")


ROOT = project_root()
TABLE_DIR = ROOT / "outputs" / "tables"
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
            "ytick.labelsize": 8.5,
        }
    )


def titles(
    fig: plt.Figure,
    ax: plt.Axes,
    title: str,
    subtitle: str,
    *,
    left: float,
    bottom: float,
) -> None:
    ax.text(0, 1.17, title, transform=ax.transAxes, fontsize=12.5, weight="bold", color=INK)
    ax.text(0, 1.07, subtitle, transform=ax.transAxes, fontsize=9, color=MUTED)
    ax.text(0, -0.16, SRC, transform=ax.transAxes, fontsize=8, color=MUTED)
    fig.subplots_adjust(top=0.80, bottom=bottom, left=left, right=0.96)


def draw_rank_chart(
    df: pd.DataFrame,
    *,
    labels: pd.Series,
    highlight_key: str,
    key_col: str,
    output_file: str,
    title: str,
    subtitle: str,
    left: float,
    bottom: float = 0.15,
) -> None:
    df = df.sort_values("margin_change_pp", ascending=True).copy()
    colors = [ACCENT if str(value) == str(highlight_key) else RISE for value in df[key_col]]

    fig, ax = plt.subplots(figsize=(8.8, 5.2))
    ax.barh(labels.loc[df.index], df["margin_change_pp"], color=colors, height=0.64, zorder=3)
    ax.axvline(0, color=HAIR, lw=1)
    ax.grid(axis="x", color=HAIR, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(HAIR)
    ax.tick_params(length=0)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:+.0f}"))
    ax.set_xlim(0, max(8.4, df["margin_change_pp"].max() + 1.0))

    for y_pos, value in enumerate(df["margin_change_pp"]):
        ax.text(value + 0.12, y_pos, f"+{value:.1f} p.b.", va="center", ha="left", fontsize=8.5)

    titles(fig, ax, title, subtitle, left=left, bottom=bottom)

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    POST_DIR.mkdir(parents=True, exist_ok=True)
    for output in [FIG_DIR / output_file, POST_DIR / output_file]:
        fig.savefig(output, dpi=170, bbox_inches="tight")
    plt.close(fig)


def save_section_chart() -> None:
    df = pd.read_csv(TABLE_DIR / "sector_margin_growth_2021_2024.csv")
    df = df[df["included_main"]].copy()
    df = df[df["revenue_2024"] >= MIN_REVENUE_2024_SECTION].copy()
    df["label"] = df["sector"].map(SECTOR_LABELS).fillna(df["sector_name"])
    df = df.sort_values("margin_change_pp", ascending=False).head(10)
    labels = df["label"]
    draw_rank_chart(
        df,
        labels=labels,
        highlight_key="R",
        key_col="sector",
        output_file="sector_margin_growth_bars.png",
        title="Najveći skok marže sjedi u rekreaciji",
        subtitle="promjena agregatne neto marže po sektoru, 2021. do 2024. (postotni bodovi)",
        left=0.30,
    )


def save_detail_chart(level_key: str) -> None:
    cfg = DETAIL_CHARTS[level_key]
    df = pd.read_csv(TABLE_DIR / cfg["table"])
    df = df[df["included_chart"]].copy()
    df = df.sort_values("margin_change_pp", ascending=False).head(cfg["top_n"])
    df["label"] = (
        df["nkd_code"].astype(str)
        + " "
        + df["nkd_name"].astype(str).map(lambda value: textwrap.fill(value.strip(), cfg["label_width"]))
    )
    highlight_key = str(df.iloc[0]["nkd_code"])
    labels = df["label"]
    draw_rank_chart(
        df,
        labels=labels,
        highlight_key=highlight_key,
        key_col="nkd_code",
        output_file=cfg["file"],
        title=cfg["title"],
        subtitle=cfg["subtitle"],
        left=cfg["left"],
        bottom=0.17,
    )


def main() -> None:
    setup_style()
    save_section_chart()
    for level_key in DETAIL_CHARTS:
        save_detail_chart(level_key)
    print("OK - saved sector and detailed NKD margin-growth charts")


if __name__ == "__main__":
    main()
