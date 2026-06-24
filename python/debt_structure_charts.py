"""Charts for the GFI debt-structure post.

The chart step is blocked until `debt_structure_build.py` says all validation
gates passed. Charts always read saved tables from `outputs/tables`.
"""

from __future__ import annotations

import shutil
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
FALL = "#D2463A"
SURFACE = "#ECE9E1"
AMBER = "#C77B30"
PURPLE = "#6D4AA6"
PAL = [ACCENT, FALL, RISE, AMBER, PURPLE, INK]

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
        "ytick.color": MUTED,
        "axes.edgecolor": HAIR,
        "axes.linewidth": 1.0,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
    }
)


def project_root() -> Path:
    path = Path.cwd().resolve()
    for candidate in [path, *path.parents]:
        if (candidate / "_quarto.yml").exists() and (candidate / "CroAIcon.Rproj").exists():
            return candidate
    raise RuntimeError("Cannot locate CroAIcon project root.")


ROOT = project_root()
TABLE_DIR = ROOT / "outputs" / "tables"
FIG_DIR = ROOT / "outputs" / "figures"
POST_DIR = ROOT / "posts" / "2026-06-zaduzenost-hrvatskih-firmi"
SRC = "Izvor: FINA GFI (db_afs), izracun AI.econ"


def audit_passed() -> tuple[bool, str]:
    audit_path = TABLE_DIR / "debt_structure_audit.csv"
    if not audit_path.exists():
        return False, "missing audit table"
    audit = pd.read_csv(audit_path)
    row = audit[audit["rule"] == "go_no_go"]
    if row.empty:
        return False, "missing go_no_go row"
    ok = bool(row["passed"].iloc[0])
    if ok:
        return True, "passed"
    failed = audit[(audit["rule"] != "go_no_go") & (~audit["passed"].astype(bool))]
    return False, ", ".join(failed["rule"].tolist())


def titles(fig, ax, title: str, sub: str, src: str, tfs: float = 12.5) -> None:
    ax.text(0, 1.20, title, transform=ax.transAxes, fontsize=tfs, weight="bold", color=INK)
    ax.text(0, 1.07, sub, transform=ax.transAxes, fontsize=9, color=MUTED)
    ax.text(0, -0.17, src, transform=ax.transAxes, fontsize=8, color=MUTED)
    fig.subplots_adjust(top=0.80, bottom=0.14)


def spines(ax, which: str = "y") -> None:
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    for side in ["left", "bottom"]:
        ax.spines[side].set_color(HAIR)
    ax.tick_params(length=0)
    ax.set_axisbelow(True)
    ax.grid(axis=which, color=HAIR, lw=0.8, zorder=0)


def save_and_copy(fig, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / name
    fig.savefig(out, dpi=170, bbox_inches="tight")
    if POST_DIR.exists():
        shutil.copy2(out, POST_DIR / name)
    plt.close(fig)


def main() -> int:
    ok, reason = audit_passed()
    if not ok:
        print(f"BLOCKED. Charts not created because debt validation failed: {reason}")
        return 0

    yearly = pd.read_csv(TABLE_DIR / "debt_structure_yearly.csv")
    bins = pd.read_csv(TABLE_DIR / "debt_profitability_bins.csv")
    sector_size = pd.read_csv(TABLE_DIR / "debt_by_sector_size.csv")

    pct = FuncFormatter(lambda v, _: f"{100 * v:.0f}%")

    fig, ax = plt.subplots(figsize=(8.4, 4.7))
    ax.axvspan(2009, 2014, color=SURFACE, zorder=0)
    ax.plot(yearly["year"], yearly["agg_debt_to_revenue"], color=ACCENT, lw=2.4)
    ax.plot(yearly["year"], yearly["debt_to_revenue_median"], color=FALL, lw=2.2)
    ax.text(
        yearly["year"].iloc[-1] + 0.15,
        yearly["agg_debt_to_revenue"].iloc[-1],
        "agregat",
        color=ACCENT,
        fontsize=8.5,
        va="center",
    )
    ax.text(
        yearly["year"].iloc[-1] + 0.15,
        yearly["debt_to_revenue_median"].iloc[-1],
        "medijan",
        color=FALL,
        fontsize=8.5,
        va="center",
    )
    spines(ax)
    ax.yaxis.set_major_formatter(pct)
    ax.set_ylim(0, max(yearly["agg_debt_to_revenue"].max(), yearly["debt_to_revenue_median"].max()) * 1.15)
    ax.set_xlim(yearly["year"].min(), yearly["year"].max() + 2)
    titles(
        fig,
        ax,
        "Agregatni dug i tipicna firma pricaju razlicitu pricu",
        "financijski dug / prihod, agregat SUM/SUM vs. medijan firme",
        SRC,
    )
    save_and_copy(fig, "debt_1_dynamics.png")

    fig, ax = plt.subplots(figsize=(8.4, 4.7))
    ax.stackplot(
        yearly["year"],
        yearly["lt_fin_debt"] / yearly["financial_debt"],
        yearly["st_fin_debt"] / yearly["financial_debt"],
        colors=[ACCENT, AMBER],
        alpha=0.92,
    )
    spines(ax)
    ax.yaxis.set_major_formatter(pct)
    ax.set_ylim(0, 1)
    ax.text(2021.8, 0.86, "kratkorocni", color=PAPER, fontsize=9, weight="bold")
    ax.text(2011.0, 0.35, "dugorocni", color=PAPER, fontsize=9, weight="bold")
    titles(
        fig,
        ax,
        "Financijski dug je vecinom dugorocan",
        "udio dugorocnog i kratkorocnog financijskog duga",
        SRC,
    )
    save_and_copy(fig, "debt_2_maturity.png")

    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    ax.bar(
        bins["profitability_bin"].astype(str),
        bins["median_debt_to_revenue"],
        color=[FALL, AMBER, MUTED, RISE, ACCENT][: len(bins)],
        zorder=3,
    )
    spines(ax)
    ax.yaxis.set_major_formatter(pct)
    titles(
        fig,
        ax,
        "Dug se skuplja na rubovima profitabilnosti",
        "medijan financijskog duga / prihoda po kvintilu neto marze, zadnja godina",
        SRC,
    )
    save_and_copy(fig, "debt_3_profitability.png")

    latest = sector_size.groupby(["sector_name"], as_index=False).agg(
        revenue=("revenue", "sum"),
        debt=("financial_debt", "sum"),
        n=("n_firms", "sum"),
    )
    latest["ratio"] = latest["debt"] / latest["revenue"]
    latest = latest[latest["n"] >= 100].sort_values("ratio").tail(12)
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.barh(latest["sector_name"], latest["ratio"], color=ACCENT, zorder=3)
    spines(ax, which="x")
    ax.xaxis.set_major_formatter(pct)
    titles(
        fig,
        ax,
        "Dug je koncentriran u nekoliko sektora",
        "financijski dug / prihod po sektoru, zadnja godina",
        SRC,
    )
    fig.subplots_adjust(left=0.24, top=0.80, bottom=0.14)
    save_and_copy(fig, "debt_4_sector_size.png")

    print("OK. Debt charts created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
