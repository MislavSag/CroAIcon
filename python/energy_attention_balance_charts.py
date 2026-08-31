"""Render the four house-style charts for the energy media/sector post."""

from __future__ import annotations

import shutil
from pathlib import Path

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PAPER = "#F7F7F4"
INK = "#18181B"
MUTED = "#71717A"
HAIR = "#E2E2DD"
ACCENT = "#2348E5"
ORANGE = "#C65A1E"
GREEN = "#1C8F5A"
LIGHT_BLUE = "#9EB0F4"
STATE = "#2348E5"
PRIVATE = "#C98500"

POST_SLUG = "2026-08-energetika-izmedu-naslova-i-bilance"


def project_root() -> Path:
    current = Path.cwd().resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "_quarto.yml").exists() and (candidate / "CroAIcon.Rproj").exists():
            return candidate
    raise RuntimeError("Cannot locate the CroAIcon project root.")


ROOT = project_root()
TABLE_DIR = ROOT / "outputs" / "tables"
FIG_DIR = ROOT / "outputs" / "figures"
POST_IMAGE_DIR = ROOT / "posts" / POST_SLUG / "images"
SOURCE_MEDIA = "Izvor: EnergoKlima; izračun AI.econ"
SOURCE_EIZ = "Izvor: EIZ, Sektorske analize 123 (2025.), str. 13; izračun AI.econ"
SOURCE_COMBINED = "Izvor: EIZ, FINA GFI, EnergoKlima; izračun AI.econ"


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
            "axes.linewidth": 0.8,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
        }
    )


def title(fig: plt.Figure, headline: str, subtitle: str) -> None:
    fig.text(0.06, 0.965, headline, ha="left", va="top", fontsize=17, fontweight="bold")
    fig.text(0.06, 0.91, subtitle, ha="left", va="top", fontsize=9.5, color=MUTED)


def source(fig: plt.Figure, text: str) -> None:
    fig.text(0.06, 0.025, text, ha="left", va="bottom", fontsize=7.6, color=MUTED)


def save(fig: plt.Figure, filename: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    POST_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / filename
    fig.savefig(out, dpi=220, bbox_inches="tight", facecolor=PAPER)
    shutil.copy2(out, POST_IMAGE_DIR / filename)
    plt.close(fig)


def media_attention() -> None:
    df = pd.read_csv(TABLE_DIR / "energy_media_monthly.csv")
    df["date"] = pd.to_datetime(df["month"] + "-01")
    shown = df[df.month.between("2021-01", "2023-12")].copy()
    fig, ax = plt.subplots(figsize=(10.2, 5.5))
    fig.subplots_adjust(left=0.075, right=0.975, top=0.79, bottom=0.14)
    title(
        fig,
        "Kriza 2022. pretvara energetiku u svakodnevnu temu",
        "Mjesečni udio objava o energetici i klimi, od siječnja 2021. do prosinca 2023.",
    )

    ax.plot(
        shown.date,
        shown.media_share_pct,
        color=ACCENT,
        lw=2.2,
        marker="o",
        ms=2.8,
    )

    peak = shown.loc[shown.media_share_pct.idxmax()]
    ax.scatter([peak.date], [peak.media_share_pct], s=58, color=ORANGE, zorder=5)
    ax.annotate(
        f"rujan 2022.\n{peak.media_share_pct:.2f}%",
        xy=(peak.date, peak.media_share_pct),
        xytext=(24, 5),
        textcoords="offset points",
        fontsize=9,
        fontweight="bold",
        color=ORANGE,
        va="bottom",
    )

    ax.set_ylim(0, 3.25)
    ax.set_ylabel("udio medijske produkcije")
    ax.yaxis.set_major_formatter(lambda value, _: f"{value:.1f}%".replace(".", ","))
    ax.set_xlim(shown.date.min() - pd.Timedelta(days=15), shown.date.max() + pd.Timedelta(days=15))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(axis="y", color=HAIR, lw=0.8)
    ax.tick_params(length=0)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(HAIR)
    source(fig, SOURCE_MEDIA)
    save(fig, "energy_media_attention.png")


def topic_shift() -> None:
    raw = pd.read_csv(TABLE_DIR / "energy_media_topic_shift.csv")
    wide = raw.pivot(index="topic", columns="year", values="corpus_share_pct")
    order = [
        "Cijene energije",
        "Sigurnost opskrbe i LNG",
        "EU politika i NECP",
        "Obnova i dizalice topline",
        "Sunčana energija",
        "Elektromobilnost",
    ]
    wide = wide.loc[order].iloc[::-1]
    fig, ax = plt.subplots(figsize=(10.2, 5.7))
    fig.subplots_adjust(left=0.29, right=0.96, top=0.79, bottom=0.16)
    title(
        fig,
        "Cijene i LNG gube polovicu udjela. Obnova i solar rastu",
        "Udio energetskih objava posvećen pojedinoj temi, 2022. i 2023.",
    )

    for y_pos, (label, row) in enumerate(wide.iterrows()):
        v22, v23 = row[2022], row[2023]
        color = ORANGE if v23 < v22 else GREEN
        ax.plot([v22, v23], [y_pos, y_pos], color=HAIR, lw=5, solid_capstyle="round")
        ax.scatter(v22, y_pos, s=52, color=MUTED, zorder=3)
        ax.scatter(v23, y_pos, s=66, color=color, zorder=4)
        ax.text(v22, y_pos + 0.19, f"{v22:.1f}".replace(".", ","), ha="center", fontsize=8, color=MUTED)
        ax.text(v23, y_pos - 0.26, f"{v23:.1f}".replace(".", ","), ha="center", fontsize=8.5, color=color, fontweight="bold")

    ax.set_yticks(range(len(wide)), labels=wide.index)
    ax.set_xlim(0, 30)
    ax.set_xlabel("udio energetskih objava")
    ax.xaxis.set_major_formatter(lambda value, _: f"{value:.0f}%")
    ax.grid(axis="x", color=HAIR, lw=0.8)
    ax.tick_params(length=0)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(HAIR)
    ax.text(0.0, 1.035, "● 2022.", transform=ax.transAxes, color=MUTED, fontsize=8.5)
    ax.text(0.12, 1.035, "● 2023. rast", transform=ax.transAxes, color=GREEN, fontsize=8.5)
    ax.text(0.29, 1.035, "● 2023. pad", transform=ax.transAxes, color=ORANGE, fontsize=8.5)
    source(fig, SOURCE_MEDIA)
    save(fig, "energy_topic_shift.png")


def renewable_mix() -> None:
    physical = pd.read_csv(TABLE_DIR / "energy_physical_2023.csv").set_index("metric")
    mix = [
        ("Hidro", physical.loc["renewable_mix_hydro", "value"], ACCENT),
        ("Vjetar", physical.loc["renewable_mix_wind", "value"], LIGHT_BLUE),
        ("Biomasa", physical.loc["renewable_mix_biomass", "value"], GREEN),
        ("Sunce", physical.loc["renewable_mix_solar", "value"], ORANGE),
        ("Ostalo", physical.loc["renewable_mix_other", "value"], "#B9B9B2"),
    ]
    renewable_share = physical.loc["renewable_electricity_share", "value"]
    fig, ax = plt.subplots(figsize=(10.2, 4.3))
    fig.subplots_adjust(left=0.06, right=0.96, top=0.72, bottom=0.2)
    title(
        fig,
        "Hidro nosi 63% obnovljive struje, sunce 4%",
        f"Obnovljivi izvori čine {renewable_share:.1f}% bruto potrošnje električne energije u 2023.",
    )

    left = 0.0
    for label, value, color in mix:
        ax.barh([0], [value], left=left, height=0.48, color=color)
        if value >= 6:
            ax.text(left + value / 2, 0, f"{label}\n{value:.0f}%", ha="center", va="center", fontsize=9, color=PAPER if label in {"Hidro", "Biomasa"} else INK, fontweight="bold")
        else:
            ax.annotate(
                f"{label} {value:.0f}%",
                xy=(left + value / 2, 0.24),
                xytext=(left + value / 2, 0.64 if label == "Sunce" else -0.62),
                ha="center",
                va="center",
                fontsize=8.5,
                color=color if label == "Sunce" else MUTED,
                arrowprops=dict(arrowstyle="-", color=color, lw=0.8),
            )
        left += value
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.9, 0.9)
    ax.set_yticks([])
    ax.set_xticks([0, 25, 50, 75, 100], labels=["0%", "25%", "50%", "75%", "100%"])
    ax.tick_params(length=0)
    ax.grid(False)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(HAIR)
    source(fig, SOURCE_EIZ)
    save(fig, "energy_renewable_mix.png")


def revenue_media_ownership() -> None:
    df = pd.read_csv(TABLE_DIR / "energy_revenue_media_ownership.csv")
    fig, ax = plt.subplots(figsize=(10.2, 4.8))
    fig.subplots_adjust(left=0.06, right=0.96, top=0.72, bottom=0.25)
    title(
        fig,
        "Privatne tvrtke nose 43% prihoda, ali 9% ekskluzivne vidljivosti",
        "Deset najvećih tvrtki u električnoj energiji i plinu, 2023.",
    )

    labels = ["Prihod", "Medijske objave"]
    y = np.array([1, 0])
    state = df.state_pct.to_numpy()
    private = df.private_pct.to_numpy()
    ax.barh(y, state, color=STATE, height=0.48)
    ax.barh(y, private, left=state, color=PRIVATE, height=0.48)
    for i in range(2):
        ax.text(state[i] / 2, y[i], f"državne\n{state[i]:.1f}%".replace(".", ","), ha="center", va="center", color=PAPER, fontsize=9, fontweight="bold")
        ax.text(state[i] + private[i] / 2, y[i], f"privatne\n{private[i]:.1f}%".replace(".", ","), ha="center", va="center", color=INK, fontsize=9, fontweight="bold")
    ax.set_yticks(y, labels=labels)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100], labels=["0%", "25%", "50%", "75%", "100%"])
    ax.tick_params(length=0)
    ax.grid(False)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(HAIR)
    source(fig, SOURCE_COMBINED)
    save(fig, "energy_revenue_media_ownership.png")


def main() -> None:
    setup_style()
    media_attention()
    topic_shift()
    renewable_mix()
    revenue_media_ownership()
    print(f"wrote 4 charts to {FIG_DIR} and {POST_IMAGE_DIR}")


if __name__ == "__main__":
    main()
