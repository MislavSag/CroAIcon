"""Charts combining Eurostat output prices with GFI margin changes."""

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

POST_SLUG = "2026-06-rast-marzi-po-sektorima"
MIN_REVENUE_2024_M = 500
OUTPUT_FILE = "price_margin_candidates_bars.png"
SRC = "Izvor: Eurostat (sts_inpp_m, sts_sepp_q), FINA GFI, izračun AI.econ"

SHORT_LABELS = {
    "50": "Vodeni prijevoz",
    "55": "Smještaj",
    "35": "Energetika",
    "56": "Hrana i piće",
    "79": "Putničke agencije",
    "702": "Savjetovanje u upravljanju",
    "23": "Nemetalni minerali",
    "52": "Skladištenje i prijevoz",
    "73": "Promidžba i istraživanje tržišta",
    "49": "Kopneni prijevoz",
    "68": "Nekretnine",
    "10": "Prehrambeni proizvodi",
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


def format_label(row: pd.Series) -> str:
    code = str(row["match_code"])
    name = SHORT_LABELS.get(code, str(row["activity_name"]))
    wrapped = textwrap.fill(name, width=34)
    return f"{code} {wrapped}"


def load_candidates() -> pd.DataFrame:
    df = pd.read_csv(TABLE_DIR / "price_margin_winners_2021_2024.csv")
    candidates = df[
        (df["candidate"])
        & (df["match_level"] != "section")
        & (df["revenue_2024_m"] >= MIN_REVENUE_2024_M)
        & (df["price_growth_pct"] > 0)
        & (df["margin_change_pp"] > 0)
        & (df["net_result_change_m"] > 0)
    ].copy()
    return candidates.sort_values("price_growth_pct", ascending=False).head(10)


def save_price_margin_candidate_chart() -> None:
    df = load_candidates()
    df["label"] = df.apply(format_label, axis=1)
    df = df.sort_values("price_growth_pct", ascending=True).copy()
    highlight = set(df.sort_values("price_growth_pct", ascending=False).head(2)["match_code"].astype(str))
    colors = [ACCENT if str(code) in highlight else RISE for code in df["match_code"]]

    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    ax.barh(df["label"], df["price_growth_pct"], color=colors, height=0.64, zorder=3)
    ax.axvline(0, color=HAIR, lw=1)
    ax.grid(axis="x", color=HAIR, lw=0.8, zorder=0)
    ax.set_axisbelow(True)

    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(HAIR)
    ax.tick_params(length=0)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f}%"))
    ax.set_xlim(0, max(110, df["price_growth_pct"].max() + 8))

    for y_pos, (_, row) in enumerate(df.iterrows()):
        price = row["price_growth_pct"]
        ax.text(price + 1.4, y_pos, f"+{price:.0f}%", va="center", ha="left", fontsize=8.5)

    ax.text(
        0,
        1.17,
        "Cijene najviše rastu u prijevozu i smještaju",
        transform=ax.transAxes,
        fontsize=12.5,
        weight="bold",
        color=INK,
    )
    ax.text(
        0,
        1.07,
        "detaljne djelatnosti s rastom output-cijena, neto marže i neto rezultata, 2021. do 2024.",
        transform=ax.transAxes,
        fontsize=9,
        color=MUTED,
    )
    ax.text(0, -0.16, SRC, transform=ax.transAxes, fontsize=8, color=MUTED)
    fig.subplots_adjust(top=0.80, bottom=0.16, left=0.35, right=0.96)

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    POST_DIR.mkdir(parents=True, exist_ok=True)
    for output in [FIG_DIR / OUTPUT_FILE, POST_DIR / OUTPUT_FILE]:
        fig.savefig(output, dpi=170, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    setup_style()
    save_price_margin_candidate_chart()
    print(f"OK - saved {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
