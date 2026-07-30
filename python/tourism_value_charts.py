"""Charts for the tourism value post.

Reads the tables written by python/tourism_value_build.py and draws six figures in house
style. Refuses to draw anything if the build's validation gate failed, the same guard
python/debt_structure_charts.py uses.

Figures land in outputs/figures/ and are copied into the post directory.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

# --------------------------------------------------------------------------------------
# house style. Mirrors R/house_style.R; see _workflow/chart-playbook.md for the roles.
# --------------------------------------------------------------------------------------

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

mpl.rcParams.update({
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
})

SRC_BOTH = "Izvor: DZS (turizam) i FINA GFI (db_afs). Izračun AI.econ"
SRC_DZS = "Izvor: DZS, statistika turizma. Izračun AI.econ"


def project_root() -> Path:
    path = Path.cwd().resolve()
    for candidate in [path, *path.parents]:
        if (candidate / "_quarto.yml").exists() and (candidate / "CroAIcon.Rproj").exists():
            return candidate
    raise RuntimeError("Cannot locate CroAIcon project root.")


ROOT = project_root()
TABLE_DIR = ROOT / "outputs" / "tables"
FIG_DIR = ROOT / "outputs" / "figures"
POST_DIR = ROOT / "posts" / "2026-07-noc-bez-cijene"


def hr(value: float, digits: int = 0) -> str:
    """Croatian number formatting. Period for thousands, comma for decimals."""
    raw = f"{float(value):,.{digits}f}"
    return raw.replace(",", "X").replace(".", ",").replace("X", ".")


def titles(fig, ax, title: str, sub: str, src: str, tfs: float = 12.5) -> None:
    ax.set_title("")
    fig.text(0.02, 1.20, title, transform=ax.transAxes, fontsize=tfs,
             fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.02, 1.07, sub, transform=ax.transAxes, fontsize=9,
             color=MUTED, ha="left", va="top")
    fig.text(0.02, -0.17, src, transform=ax.transAxes, fontsize=7.5,
             color=MUTED, ha="left", va="top")
    fig.subplots_adjust(top=0.80, bottom=0.14)


def spines(ax, which: str = "y") -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_visible(which == "y")
    ax.spines["bottom"].set_color(HAIR)
    ax.tick_params(length=0)
    if which == "y":
        ax.grid(axis="y", color=HAIR, linewidth=0.6)
    else:
        ax.grid(axis="x", color=HAIR, linewidth=0.6)
    ax.set_axisbelow(True)


def save_and_copy(fig, name: str) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    POST_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / name
    fig.savefig(out, dpi=170, bbox_inches="tight")
    shutil.copyfile(out, POST_DIR / name)
    plt.close(fig)
    print(f"   {name}")


def audit_passed() -> tuple[bool, str]:
    path = TABLE_DIR / "tourism_validation.csv"
    if not path.exists():
        return False, "tourism_validation.csv missing, run the build first"
    checks = pd.read_csv(path, encoding="utf-8-sig")
    row = checks[checks["rule"] == "go_no_go"]
    if row.empty:
        return False, "no go_no_go row in the validation table"
    ok = bool(row["passed"].iloc[0])
    return ok, str(row["detail"].iloc[0])


def read(name: str) -> pd.DataFrame:
    return pd.read_csv(TABLE_DIR / name, encoding="utf-8-sig")


# --------------------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------------------

def fig_national() -> None:
    """One night, over time. Nominal against real, so inflation cannot carry the story."""
    d = read("tourism_eur_per_night_national.csv")
    base_year = int(d["real_base_year"].dropna().iloc[0])

    fig, ax = plt.subplots(figsize=(8.4, 4.7))
    ax.plot(d["year"], d["eur_per_night"], color=ACCENT, linewidth=2.4,
            marker="o", markersize=3.5, label="Nominalno")
    real = d.dropna(subset=["eur_per_night_real"])
    ax.plot(real["year"], real["eur_per_night_real"], color=MUTED, linewidth=1.6,
            linestyle="--", label=f"U cijenama {base_year}.")

    last = d.iloc[-1]
    ax.annotate(f"{hr(last['eur_per_night'], 1)} EUR",
                xy=(last["year"], last["eur_per_night"]),
                xytext=(-6, 12), textcoords="offset points",
                fontsize=10, fontweight="bold", color=ACCENT, ha="right")
    first = d.iloc[0]
    ax.annotate(f"{hr(first['eur_per_night'], 1)} EUR",
                xy=(first["year"], first["eur_per_night"]),
                xytext=(4, -16), textcoords="offset points",
                fontsize=9, color=MUTED)

    ax.set_ylim(0, max(d["eur_per_night"]) * 1.25)
    # always label the final year. The lede number sits on it.
    ticks = sorted(set(list(d["year"])[::2]) | {int(d["year"].iloc[-1])})
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{y}." for y in ticks])
    ax.yaxis.set_major_formatter(lambda v, _: hr(v))
    spines(ax)
    leg = ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    for text in leg.get_texts():
        text.set_color(MUTED)
    titles(fig, ax,
           "Od turističke noći u poduzeća uđe oko 40 eura",
           "Prihod smještajnih društava po ostvarenom noćenju, u eurima. "
           f"Realna serija u cijenama {base_year}.",
           SRC_BOTH)
    save_and_copy(fig, "tourism_1_eur_per_night.png")


def fig_models() -> None:
    """The heart of it. Half the nights, almost none of the money.

    This chart used to plot company revenue per night per accommodation type, which put
    4 EUR against the rooms-and-apartments row. That quotient divides the revenue of 1.691
    companies by 46,6 million nights that mostly belong to households, and DZS publishes no
    operator split, so it measures nothing and is gone from the post. What survives is the
    finding itself: two distributions, nights and company revenue, that do not line up.
    Both are percentages of a whole, both computed inside a single population."""
    d = read("tourism_value_by_model.csv").sort_values("nights_share_pct")

    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    pos = range(len(d))
    height = 0.36
    nights = ax.barh([p + height / 2 for p in pos], d["nights_share_pct"],
                     height=height, color=MUTED, label="udio u noćenjima")
    revenue = ax.barh([p - height / 2 for p in pos], d["revenue_share_pct"],
                      height=height, color=ACCENT, label="udio u prihodu društava")

    for bars, values in ((nights, d["nights_share_pct"]), (revenue, d["revenue_share_pct"])):
        for bar, value in zip(bars, values):
            ax.text(bar.get_width() + 1.2, bar.get_y() + bar.get_height() / 2,
                    f"{hr(value, 1)}%", va="center", fontsize=9.5,
                    fontweight="bold", color=INK)

    ax.set_yticks(list(pos))
    ax.set_yticklabels(d["label"])
    ax.set_xlim(0, max(d["revenue_share_pct"].max(), d["nights_share_pct"].max()) * 1.14)
    ax.xaxis.set_major_formatter(lambda v, _: f"{hr(v)}%")
    spines(ax, which="x")
    ax.tick_params(axis="y", labelsize=10)
    leg = ax.legend(frameon=False, fontsize=8.5, loc="lower right")
    for text in leg.get_texts():
        text.set_color(MUTED)
    titles(fig, ax,
           "Hoteli nose 27% noćenja i 88% prihoda, apartmani 50% i 5%",
           "Udio u ostvarenim noćenjima i u prihodu trgovačkih društava, prema vrsti "
           "smještaja, 2024.\nDvije raspodjele, ne cijena. Noćenja broji DZS, prihod "
           "financijski izvještaji.",
           SRC_BOTH)
    save_and_copy(fig, "tourism_2_po_vrsti_smjestaja.png")


def fig_bed_use() -> None:
    """The same finding with none of the population problem. Nights and beds are both
    counted by DZS at the object, so this comparison needs no company accounts and cannot
    be argued with on coverage grounds."""
    d = read("tourism_value_by_model.csv").sort_values("nights_per_bed")

    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    colors = [RISE if v > 120 else FALL if v < 70 else MUTED for v in d["nights_per_bed"]]
    labels = [f"{row.label}\n{hr(row.beds/1000, 0)} tis. postelja" for row in d.itertuples()]
    bars = ax.barh(labels, d["nights_per_bed"], color=colors, height=0.6)

    for bar, value in zip(bars, d["nights_per_bed"]):
        ax.text(bar.get_width() + 2.5, bar.get_y() + bar.get_height() / 2,
                f"{hr(value, 0)} noći", va="center", fontsize=10.5,
                fontweight="bold", color=INK)

    ax.set_xlim(0, max(d["nights_per_bed"]) * 1.24)
    ax.xaxis.set_major_formatter(lambda v, _: hr(v))
    spines(ax, which="x")
    ax.tick_params(axis="y", labelsize=10)
    # `privatni` prejudices ownership, which this table does not record. It counts beds by
    # the kind of object, not by who runs it.
    titles(fig, ax,
           "Hotelski krevet radi 148 noći godišnje, krevet u apartmanu 64",
           "Broj ostvarenih noćenja po postelji, prema vrsti smještaja, 2024. "
           "Računato samo iz\nstatistike turizma, bez ijednog podatka o prihodu.",
           SRC_DZS)
    save_and_copy(fig, "tourism_10_iskoristenost_postelja.png")


def fig_counties() -> None:
    """Where a night pays best. Coastal counties, with Zagreb as the contrast."""
    d = read("tourism_eur_per_night_by_county.csv")
    # Zagreb is city-break tourism at ~5x the best coastal county. Left in, it compresses
    # all seven coastal bars into the left fifth of the panel and the spread this chart
    # exists to show disappears. It belongs in the prose as a contrast.
    d = d[d["is_coastal"]].sort_values("eur_per_night")

    fig, ax = plt.subplots(figsize=(8.4, 4.5))
    colors = [RISE if v >= 40 else FALL if v <= 23 else MUTED for v in d["eur_per_night"]]
    bars = ax.barh(d["label"], d["eur_per_night"], color=colors, height=0.66)

    for bar, value in zip(bars, d["eur_per_night"]):
        ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height() / 2,
                f"{hr(value, 1)}", va="center", fontsize=9.5,
                fontweight="bold", color=INK)

    ax.set_xlim(0, max(d["eur_per_night"]) * 1.16)
    ax.xaxis.set_major_formatter(lambda v, _: hr(v))
    spines(ax, which="x")
    ax.tick_params(axis="y", labelsize=9.5)
    # the scope belongs in the bold title, not only the grey subtitle. Shared as a bare
    # PNG this chart would otherwise read as a national ranking, and Zagreb is off it.
    titles(fig, ax,
           "Istra od noći naplati dvostruko više od Like",
           "Prihod smještajnih firmi po noćenju, eura, jadranske županije, 2024. "
           "Grad Zagreb (196,4 eura) nije prikazan zbog razmjera.",
           SRC_BOTH)
    save_and_copy(fig, "tourism_3_po_zupanijama.png")


def fig_season() -> None:
    """Two months carry the year."""
    d = read("tourism_seasonality_national.csv")
    last = d[d["year"] == d["year"].max()].iloc[0]
    months = [str(m) for m in range(1, 13)]
    values = [float(last[m]) for m in months]
    labels = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]

    fig, ax = plt.subplots(figsize=(8.4, 4.5))
    colors = [FALL if i in (6, 7) else MUTED for i in range(12)]
    bars = ax.bar(labels, values, color=colors, width=0.68)

    peak = values[6] + values[7]
    ax.annotate(f"srpanj + kolovoz = {hr(peak, 1)}%",
                xy=(6.5, max(values) * 1.02), xytext=(0, 18),
                textcoords="offset points", ha="center",
                fontsize=10, fontweight="bold", color=FALL)

    for i in (6, 7):
        ax.text(i, values[i] + 0.6, f"{hr(values[i], 1)}", ha="center",
                fontsize=9, fontweight="bold", color=INK)

    ax.set_ylim(0, max(values) * 1.30)
    ax.yaxis.set_major_formatter(lambda v, _: f"{hr(v)}%")
    spines(ax)
    ax.tick_params(axis="x", labelsize=9.5)
    titles(fig, ax,
           "Dva mjeseca nose više od polovice godine",
           f"Udio pojedinog mjeseca u ukupnim noćenjima, {int(last['year'])}.",
           SRC_DZS)
    save_and_copy(fig, "tourism_4_sezonalnost.png")


def fig_domestic() -> None:
    """Croatians were never on their own coast."""
    d = read("tourism_domestic_share.csv")

    fig, ax = plt.subplots(figsize=(8.4, 4.5))
    ax.plot(d["year"], d["domestic_share_pct"], color=ACCENT, linewidth=2.4,
            marker="o", markersize=3.2)
    ax.axhline(10, color=HAIR, linewidth=1.0, zorder=0)

    covid = d[d["year"] == 2020]
    if not covid.empty:
        ax.annotate("2020.", xy=(2020, float(covid["domestic_share_pct"].iloc[0])),
                    xytext=(0, 10), textcoords="offset points", ha="center",
                    fontsize=8.5, color=MUTED)

    for idx in (0, len(d) - 1):
        row = d.iloc[idx]
        ax.annotate(f"{hr(row['domestic_share_pct'], 1)}%",
                    xy=(row["year"], row["domestic_share_pct"]),
                    xytext=(0, -18), textcoords="offset points", ha="center",
                    fontsize=9.5, fontweight="bold", color=ACCENT)

    ax.set_ylim(0, max(d["domestic_share_pct"]) * 1.35)
    ax.yaxis.set_major_formatter(lambda v, _: f"{hr(v)}%")
    ticks = sorted(set(list(d["year"])[::3]) | {int(d["year"].iloc[-1])})
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{int(y)}." for y in ticks])
    spines(ax)
    titles(fig, ax,
           "Devet od deset noćenja u Hrvatskoj nije hrvatsko",
           "Udio domaćih gostiju u ukupnim noćenjima. Skok 2020. je zatvorena granica.",
           SRC_DZS)
    save_and_copy(fig, "tourism_5_domaci_gosti.png")


def fig_marina() -> None:
    """The one place the statistics office publishes money."""
    d = read("tourism_marina_per_berth.csv")
    d = d[d["place"] != "Republika Hrvatska"].copy()
    d["label"] = d["place"].str.replace(" županija", "", regex=False)
    d = d.sort_values("eur_per_berth")

    fig, ax = plt.subplots(figsize=(8.4, 4.5))
    colors = [RISE if v >= 15000 else FALL if v <= 7000 else MUTED
              for v in d["eur_per_berth"]]
    bars = ax.barh(d["label"], d["eur_per_berth"], color=colors, height=0.64)

    for bar, value in zip(bars, d["eur_per_berth"]):
        ax.text(bar.get_width() + 350, bar.get_y() + bar.get_height() / 2,
                f"{hr(value)}", va="center", fontsize=9.5,
                fontweight="bold", color=INK)

    ax.set_xlim(0, max(d["eur_per_berth"]) * 1.18)
    ax.xaxis.set_major_formatter(lambda v, _: hr(v))
    spines(ax, which="x")
    ax.tick_params(axis="y", labelsize=9.5)
    year = int(d["year"].iloc[0])
    titles(fig, ax,
           "Split od veza naplati tri i pol puta više od Istre",
           f"Prihod marina po vezu, eura, {year}.",
           SRC_DZS)
    save_and_copy(fig, "tourism_6_vez.png")


def fig_hnb_gap() -> None:
    """Where the money a foreign guest leaves actually lands. The accommodation company
    books a quarter of it, and that quarter has not moved since 2019."""
    d = read("tourism_hnb_gap.csv").sort_values("year")

    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    labels = [f"{int(y)}." for y in d["year"]]
    # "Sve ostalo" is the biggest slice and the point of the chart, so it cannot be drawn
    # in SURFACE, which the playbook reserves for bands behind the data and which sits a
    # few RGB points off the page colour. MUTED is the role for a context series.
    parts = [
        ("accommodation_per_foreign_night", "Smještajne firme", ACCENT),
        ("food_per_foreign_night", "Ugostiteljstvo", AMBER),
        ("rest_per_foreign_night", "Sve ostalo", MUTED),
    ]

    shares = d["accommodation_share_pct"].tolist()
    left = [0.0] * len(d)
    for column, name, color in parts:
        values = d[column].tolist()
        ax.barh(labels, values, left=left, color=color, height=0.5, label=name)
        for i, (value, start) in enumerate(zip(values, left)):
            # the thin segments cannot hold a label; only annotate what fits
            if value <= 12:
                continue
            # The share is the finding in the title, so it rides inside the accommodation
            # segment rather than being left for the reader to divide 44 by 176. Outside
            # the bar it would collide with the subtitle.
            text = (f"{hr(value, 0)}\n{hr(shares[i], 0)}%"
                    if column == "accommodation_per_foreign_night" else f"{hr(value, 0)}")
            ax.text(start + value / 2, i, text, va="center", ha="center",
                    fontsize=10, fontweight="bold", color=PAPER, linespacing=1.35)
        left = [a + b for a, b in zip(left, values)]

    for i, total in enumerate(left):
        ax.text(total + 3, i, f"ukupno {hr(total, 0)} EUR", va="center",
                fontsize=9.5, fontweight="bold", color=INK)

    ax.set_xlim(0, max(left) * 1.24)
    ax.xaxis.set_major_formatter(lambda v, _: hr(v))
    spines(ax, which="x")
    ax.tick_params(axis="y", labelsize=10)
    leg = ax.legend(frameon=False, fontsize=8.5, loc="lower right",
                    ncol=3, bbox_to_anchor=(1.0, -0.30))
    for text in leg.get_texts():
        text.set_color(MUTED)
    titles(fig, ax,
           "Gost ostavi 176 eura po noći. Smještaju pripadne četvrtina.",
           "Devizni prihodi od stranih gostiju po stranom noćenju, eura, prema tome tko ih "
           "naplati.\nUdio smještaja je gornja granica jer prihod firmi uključuje i domaće goste.",
           "Izvor: HNB (devizni prihodi), DZS (noćenja) i FINA GFI. Izračun AI.econ")
    save_and_copy(fig, "tourism_7_hnb_jaz.png")


def fig_stay_length() -> None:
    """More guests, shorter stays. The headline count grows on arrivals, not on demand
    per guest."""
    d = read("tourism_stay_length.csv")

    fig, ax = plt.subplots(figsize=(8.4, 4.5))
    series = [("strani", "Strani gosti", ACCENT), ("ukupno", "Ukupno", MUTED)]
    for column, name, color in series:
        ax.plot(d["year"], d[column], color=color, linewidth=2.2,
                marker="o", markersize=3.2, label=name)

    for column, color in (("strani", ACCENT),):
        for idx, offset in ((0, 14), (len(d) - 1, 14)):
            row = d.iloc[idx]
            ax.annotate(f"{hr(row[column], 2)}", xy=(row["year"], row[column]),
                        xytext=(0, offset), textcoords="offset points", ha="center",
                        fontsize=9.5, fontweight="bold", color=color)

    # 2020 and 2021 are closed borders. Long stays that year are a lockdown artefact and
    # the reader has to be told, or the dip reads as a trend break.
    ax.annotate("zatvorene granice", xy=(2020, float(d.loc[d["year"] == 2020, "strani"].iloc[0])),
                xytext=(0, 12), textcoords="offset points", ha="center",
                fontsize=8, color=MUTED)

    ax.set_ylim(0, max(d["strani"]) * 1.32)
    ax.yaxis.set_major_formatter(lambda v, _: hr(v, 1))
    ticks = sorted(set(list(d["year"])[::2]) | {int(d["year"].iloc[-1])})
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{int(y)}." for y in ticks])
    spines(ax)
    leg = ax.legend(frameon=False, fontsize=8.5, loc="lower left")
    for text in leg.get_texts():
        text.set_color(MUTED)
    titles(fig, ax,
           "Gostiju je sve više, a svaki ostaje sve kraće",
           "Prosječan broj noćenja po dolasku turista.",
           SRC_DZS)
    save_and_copy(fig, "tourism_8_nocenja_po_dolasku.png")


def fig_type_mix() -> None:
    """Is Croatia leaving the cheap model? Measured from the 2021 trough the hotel share is
    rising, which is the usual reading. Measured from 2019 it is still short. The mix is
    recovering, not changing, and the chart has to show both anchors or it flatters."""
    d = read("tourism_type_share_panel.csv")
    d = d[d["residency"] == "total"].sort_values("year")

    fig, ax = plt.subplots(figsize=(8.4, 4.5))
    series = [
        ("share_sobe", "Sobe i apartmani", MUTED),
        ("share_hoteli", "Hoteli", ACCENT),
        ("share_kampovi", "Kampovi", AMBER),
    ]
    for column, name, color in series:
        width = 2.4 if column == "share_hoteli" else 1.6
        ax.plot(d["year"], d[column], color=color, linewidth=width,
                marker="o", markersize=3.0, label=name)

    first = d.iloc[0]
    trough = d[d["year"] == 2021].iloc[0]
    last = d.iloc[-1]
    # the pre-pandemic level is the honest benchmark, so draw it rather than describe it
    ax.axhline(float(first["share_hoteli"]), color=ACCENT, linewidth=0.9,
               linestyle=":", zorder=0)
    for row, offset in ((first, 12), (trough, -18), (last, -20)):
        ax.annotate(f"{hr(row['share_hoteli'], 1)}%",
                    xy=(row["year"], row["share_hoteli"]),
                    xytext=(0, offset), textcoords="offset points", ha="center",
                    fontsize=9.5, fontweight="bold", color=ACCENT)

    ax.set_ylim(0, max(d["share_sobe"]) * 1.30)
    ax.yaxis.set_major_formatter(lambda v, _: f"{hr(v)}%")
    ax.set_xticks(list(d["year"]))
    ax.set_xticklabels([f"{int(y)}." for y in d["year"]])
    spines(ax)
    leg = ax.legend(frameon=False, fontsize=8.5, loc="center right")
    for text in leg.get_texts():
        text.set_color(MUTED)
    titles(fig, ax,
           "Hoteli se šest godina vraćaju na svoj stari udio",
           "Udio vrste smještaja u ukupnim noćenjima. Točkasta linija je razina iz 2019. "
           "Pad 2020.\ni 2021. je pandemija, kada su hoteli bili zatvoreni, a apartmani nisu.",
           SRC_DZS)
    save_and_copy(fig, "tourism_9_udio_hotela.png")


def main() -> None:
    ok, detail = audit_passed()
    if not ok:
        raise SystemExit(f"BLOCKED. Charts not created because validation failed: {detail}")
    print(f"validation gate: {detail}\n\ndrawing ...")
    fig_national()
    fig_models()
    fig_counties()
    fig_season()
    fig_domestic()
    fig_marina()
    fig_hnb_gap()
    fig_stay_length()
    fig_type_mix()
    fig_bed_use()
    print(f"\nwritten to {FIG_DIR} and copied to {POST_DIR}")


if __name__ == "__main__":
    main()
