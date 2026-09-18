"""LinkedIn carousel for the tourism post.

Ten 1080x1350 slides in house style, built from outputs/facts/tourism_value.json so
every figure on a slide is the same figure the post prints. Writes the PNGs and one
multipage PDF (the LinkedIn document post) to outputs/social/turizam-bez-nazivnika/.

Run: .venv/Scripts/python.exe python/tourism_carousel.py
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# --------------------------------------------------------------------------------------
# house style. Same roles as python/tourism_value_charts.py; see _workflow/chart-playbook.md
# --------------------------------------------------------------------------------------

PAPER = "#F7F7F4"
INK = "#18181B"
MUTED = "#71717A"
HAIR = "#E6E6E1"
ACCENT = "#2348E5"
RISE = "#1C8F5A"
FALL = "#D2463A"
SURFACE = "#ECE9E1"

mpl.rcParams.update({
    "font.family": "monospace",
    "font.monospace": ["DejaVu Sans Mono"],
    "figure.facecolor": PAPER,
    "savefig.facecolor": PAPER,
    "axes.facecolor": PAPER,
    "text.color": INK,
})

# 1080 x 1350 at dpi 100. LinkedIn's tallest allowed frame, so type can breathe.
W_IN, H_IN = 10.8, 13.5
DPI = 100

L = 0.085          # left margin, figure fraction
R = 0.915          # right margin
TOP_RULE = 0.945
FOOT_RULE = 0.072

KICKER, HEAD, BIG, BIGLAB, BODY, PUNCH, FOOT = 15.0, 32.0, 98.0, 18.0, 19.5, 23.0, 12.5

TOP = 0.825       # where a slide's headline or hero starts
GAP = 0.075       # breathing room between blocks

SLUG = "AI.econ  ·  Turizam bez nazivnika"
N_SLIDES = 10


def project_root() -> Path:
    path = Path.cwd().resolve()
    for candidate in [path, *path.parents]:
        if (candidate / "_quarto.yml").exists() and (candidate / "outputs").exists():
            return candidate
    raise RuntimeError("Cannot locate CroAIcon project root.")


ROOT = project_root()
OUT_DIR = ROOT / "outputs" / "social" / "turizam-bez-nazivnika"
FACTS = json.loads(
    (ROOT / "outputs" / "facts" / "tourism_value.json").read_text(encoding="utf-8")
)


def hr(value: float, digits: int = 0) -> str:
    """Croatian number formatting. Period for thousands, comma for decimals."""
    raw = f"{float(value):,.{digits}f}"
    return raw.replace(",", "X").replace(".", ",").replace("X", ".")


# --------------------------------------------------------------------------------------
# slide furniture
# --------------------------------------------------------------------------------------


def new_slide(number: int) -> plt.Figure:
    fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI)
    fig.lines.append(
        plt.Line2D([L, L + 0.075], [TOP_RULE, TOP_RULE], color=ACCENT, lw=5,
                   transform=fig.transFigure, solid_capstyle="butt")
    )
    fig.lines.append(
        plt.Line2D([L, R], [FOOT_RULE, FOOT_RULE], color=HAIR, lw=1.2,
                   transform=fig.transFigure)
    )
    fig.text(L, FOOT_RULE - 0.028, SLUG, fontsize=FOOT, color=MUTED, va="top")
    fig.text(R, FOOT_RULE - 0.028, f"{number:02d} / {N_SLIDES}", fontsize=FOOT,
             color=MUTED, va="top", ha="right")
    return fig


def wrapped(fig, y: float, text: str, size: float, width: int, color=INK,
            weight="normal", spacing: float = 1.45, x: float = L) -> float:
    """Draw wrapped monospace text top-down. Returns the y the block ended on.

    A blank line separates paragraphs, a single newline forces a break so a headline
    never leaves an orphan word on its own line.
    """
    lines: list[str] = []
    for para in text.split("\n\n"):
        if lines:
            lines.append("")
        for hard_line in para.split("\n"):
            lines.extend(textwrap.wrap(hard_line, width=width) or [""])
    fig.text(x, y, "\n".join(lines), fontsize=size, color=color, fontweight=weight,
             va="top", linespacing=spacing)
    step = size * spacing / 72 / H_IN
    return y - len(lines) * step


def kicker(fig, text: str, y: float = 0.905) -> None:
    fig.text(L, y, " ".join(text.upper()), fontsize=KICKER, color=ACCENT,
             fontweight="bold", va="top")


def hero(fig, y: float, value: str, label: str, color=INK) -> float:
    fig.text(L, y, value, fontsize=BIG, color=color, fontweight="bold", va="top")
    y -= BIG * 1.05 / 72 / H_IN
    return wrapped(fig, y - 0.012, label, BIGLAB, 60, color=MUTED)


def panel(fig, bottom: float, height: float) -> plt.Axes:
    ax = fig.add_axes([L, bottom, R - L, height])
    ax.set_facecolor(PAPER)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0, labelleft=False, labelbottom=False)
    return ax


# --------------------------------------------------------------------------------------
# the ten slides
# --------------------------------------------------------------------------------------


def slide_01() -> plt.Figure:
    fig = new_slide(1)
    kicker(fig, "Analiza")
    fig.text(L, 0.855, "Turizam\nbez nazivnika", fontsize=62, fontweight="bold",
             color=INK, va="top", linespacing=1.15)
    fig.lines.append(
        plt.Line2D([L, L + 0.16], [0.612, 0.612], color=INK, lw=2.5,
                   transform=fig.transFigure)
    )

    fig.text(L, 0.575, f"{hr(FACTS['nights_last_year'] / 1e6, 1)} mil.", fontsize=52,
             fontweight="bold", color=INK, va="top")
    fig.text(L, 0.522, "komercijalnih noćenja, 2024.", fontsize=BIGLAB, color=MUTED,
             va="top")
    fig.text(L, 0.462, f"{hr(FACTS['hnb_receipts_last'] / 1e9, 2)} mlrd. €", fontsize=52,
             fontweight="bold", color=INK, va="top")
    fig.text(L, 0.409, "prihoda od stranih turista, 2024.", fontsize=BIGLAB, color=MUTED,
             va="top")
    fig.text(L, 0.349, "cijena noći", fontsize=52, fontweight="bold", color=ACCENT,
             va="top")
    fig.text(L, 0.296, "ne postoji ni u jednoj javnoj tablici", fontsize=BIGLAB,
             color=MUTED, va="top")

    wrapped(fig, 0.212, "Hrvatska broji noćenja do zadnjeg kreveta. "
                        "Koliko vrijedi jedna noć, ne objavljuje nitko.",
            PUNCH, 46, color=INK, weight="bold")
    return fig


def slide_02() -> plt.Figure:
    fig = new_slide(2)
    kicker(fig, "Postavka")
    end = wrapped(fig, TOP, "Dvije rekordne brojke pozivaju na dijeljenje. "
                            "Taj bi račun bio pogrešan.", HEAD, 32, weight="bold")

    y = wrapped(fig, end - GAP,
                "Noćenja mjere spavanje u komercijalnom smještaju. "
                "Devizni prihod mjeri sve što strani gost potroši, od hotela do goriva."
                "\n\n"
                "Još važnije. Noćenja obuhvaćaju i poduzeća i kućanstva. "
                "Financijski izvještaji obuhvaćaju poduzeća.",
                BODY, 54, color=MUTED)

    ax = panel(fig, y - 0.235, 0.19)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.plot([0.02, 0.60], [0.66, 0.66], color=INK, lw=2.5)
    ax.text(0.02, 0.76, "BROJNIK   prihod poduzeća", fontsize=17, color=INK,
            fontweight="bold")
    ax.plot([0.02, 0.98], [0.22, 0.22], color=ACCENT, lw=2.5)
    ax.text(0.02, 0.32, "NAZIVNIK  noćenja poduzeća i kućanstava", fontsize=17,
            color=ACCENT, fontweight="bold")

    wrapped(fig, y - 0.275, "Brojnik i nazivnik ne opisuju isti svijet.",
            PUNCH, 44, weight="bold")
    return fig


def slide_03() -> plt.Figure:
    fig = new_slide(3)
    kicker(fig, "Glavna mjera")
    y = hero(fig, TOP, f"{hr(FACTS['eur_per_night_last'], 1)} €",
             "prihoda smještajnih društava po ostvarenom noćenju, 2024.")

    y = wrapped(fig, y - 0.115,
                f"Nominalno {hr(FACTS['eur_per_night_first'], 1)} (2013.) → "
                f"{hr(FACTS['eur_per_night_last'], 1)} (2024.), plus "
                f"{hr(FACTS['eur_per_night_growth_pct'])}%. "
                f"U stalnim cijenama plus {hr(FACTS['eur_per_night_real_growth_pct'])}%. "
                "Polovica rasta je inflacija.",
                BODY, 54, color=MUTED)

    wrapped(fig, y - 0.115,
            "To nije cijena. Brojnik obuhvaća samo društva, a nazivnik i društva i "
            "kućanstva. Iznos mjeri koliko turizma prolazi kroz poduzeća.",
            PUNCH, 44, weight="bold")
    return fig


def slide_04() -> plt.Figure:
    fig = new_slide(4)
    kicker(fig, "Dva gospodarstva")
    end = wrapped(fig, TOP, "Pola noćenja.\nPet posto prihoda.", 38, 30, weight="bold")
    end = wrapped(fig, end - 0.022,
                  "Sobe i apartmani, 2024. Udio u ostvarenim noćenjima i udio u prihodu "
                  "smještajnih društava.", BIGLAB, 58, color=MUTED)

    rows = [
        ("Sobe i apartmani", FACTS["model_apartment_nights_share"],
         FACTS["model_apartment_revenue_share"]),
        ("Kampovi", FACTS["model_553_nights_share_pct"],
         FACTS["model_553_revenue_share_pct"]),
        ("Hoteli", FACTS["model_551_nights_share_pct"],
         FACTS["model_551_revenue_share_pct"]),
    ]
    step = 1.45
    ax = panel(fig, end - 0.395, 0.345)
    ax.set_xlim(0, 108)
    ax.set_ylim(-0.95, (len(rows) - 1) * step + 0.75)
    for i, (name, nights, revenue) in enumerate(rows):
        base = (len(rows) - 1 - i) * step
        ax.barh(base + 0.17, nights, height=0.3, color=MUTED)
        ax.barh(base - 0.17, revenue, height=0.3, color=ACCENT)
        ax.text(nights + 1.6, base + 0.17, f"{hr(nights, 1)}%", va="center", fontsize=17,
                color=INK, fontweight="bold")
        ax.text(revenue + 1.6, base - 0.17, f"{hr(revenue, 1)}%", va="center",
                fontsize=17, color=INK, fontweight="bold")
        ax.text(0, base + 0.56, name, fontsize=17.5, color=INK, fontweight="bold")
    ax.text(0, -0.9, "■ noćenja", fontsize=15, color=MUTED)
    ax.text(20, -0.9, "■ prihod smještajnih društava", fontsize=15, color=ACCENT)

    wrapped(fig, end - 0.435,
            "To nisu dvije strane istog kolača, nego dvije odvojene raspodjele. "
            "Tamo gdje se razilaze, javna usporedba prestaje.",
            PUNCH, 44, weight="bold")
    return fig


def slide_05() -> plt.Figure:
    fig = new_slide(5)
    kicker(fig, "Slijepa točka")
    y = hero(fig, TOP, f"{hr(FACTS['household_commercial_share_pct'])}%",
             f"komercijalnih noćenja ostvare objekti u domaćinstvu. "
             f"{hr(FACTS['household_nights_htz'] / 1e6, 1)} milijuna noćenja, 2024.",
             color=ACCENT)

    y = wrapped(fig, y - GAP,
                "Za njih ne postoji javno objavljen prihod usporediv s prihodom "
                "društava. Ni po noćenju, ni po postelji, ni po zaposlenom."
                "\n\n"
                f"{hr(FACTS['platform_share_of_apartments_pct'])}% noćenja u sobama i "
                "apartmanima ide preko internetskih platformi. Rezervaciju možemo "
                "smjestiti u kanal. Prihod joj ne možemo pridružiti.",
                BODY, 54, color=MUTED)

    wrapped(fig, y - GAP,
            "Četiri od deset noćenja izlaze iz zajedničkog računa.",
            PUNCH, 44, weight="bold")
    return fig


def slide_06() -> plt.Figure:
    fig = new_slide(6)
    kicker(fig, "Devizni prihod")
    end = wrapped(fig, TOP,
                  f"Strani gost potroši {hr(FACTS['eur_per_foreign_night'])} € po noći. "
                  f"Smještajna društva vide najviše "
                  f"{hr(FACTS['accommodation_per_foreign_night'])}.",
                  HEAD, 32, weight="bold")

    parts = [
        ("smještaj", FACTS["accommodation_per_foreign_night"], ACCENT),
        ("ugostiteljstvo", FACTS["food_per_foreign_night"], MUTED),
        ("ostalo", FACTS["rest_per_foreign_night"], SURFACE),
    ]
    total = sum(p[1] for p in parts)
    ax = panel(fig, end - 0.245, 0.185)
    ax.set_xlim(0, total)
    ax.set_ylim(0, 1)
    left = 0.0
    for name, value, color in parts:
        ax.barh(0.70, value, left=left, height=0.44, color=color)
        ax.text(left, 0.34, f"{hr(value)} €", fontsize=22, color=INK, fontweight="bold")
        ax.text(left, 0.16, name, fontsize=14, color=MUTED)
        left += value

    y = wrapped(fig, end - 0.29,
                f"Udio smještaja je {hr(FACTS['accommodation_share_of_receipts_pct'])}%, "
                "i to je gornja granica jer prihod društava uključuje i domaće goste. "
                "U ostatku su trgovina, prijevoz, izleti, marine i kućanstva koja "
                "iznajmljuju. Javni agregati ne pokazuju koliko pripada svakome.",
                BODY, 54, color=MUTED)

    wrapped(fig, y - GAP,
            "Rekordni devizni prihod kaže koliko je novca ušlo. Ne kaže kome pripada.",
            PUNCH, 44, weight="bold")
    return fig


def slide_07() -> plt.Figure:
    fig = new_slide(7)
    kicker(fig, "Ritam kreveta")
    end = wrapped(fig, TOP,
                  f"Hotelska postelja radi {hr(FACTS['nights_per_bed_551'])} noći "
                  f"godišnje. Postelja u sobi ili apartmanu "
                  f"{hr(FACTS['nights_per_bed_552'])}.",
                  HEAD, 32, weight="bold")

    rows = [
        ("Hoteli", FACTS["nights_per_bed_551"], ACCENT),
        ("Kampovi", FACTS["nights_per_bed_553"], MUTED),
        ("Sobe i apartmani", FACTS["nights_per_bed_552"], MUTED),
    ]
    ax = panel(fig, end - 0.34, 0.30)
    ax.set_xlim(0, 178)
    ax.set_ylim(-0.85, len(rows) - 0.25)
    for i, (name, value, color) in enumerate(rows):
        ax.barh(len(rows) - 1 - i, value, height=0.36, color=color)
        ax.text(value + 2.5, len(rows) - 1 - i, hr(value), va="center", fontsize=22,
                color=INK, fontweight="bold")
        ax.text(0, len(rows) - 1 - i + 0.36, name, fontsize=17.5, color=INK,
                fontweight="bold")
    ax.text(0, -0.8, "noćenja po registriranoj postelji, 2024.", fontsize=15,
            color=MUTED)

    y = wrapped(fig, end - 0.375,
                "Postelja u sobama i apartmanima ima više nego hotelskih i kamp "
                "zajedno. Za oba modela znamo koliko kreveta i koliko noći.",
                BODY, 54, color=MUTED)

    wrapped(fig, y - 0.05, "Za samo jedan znamo koliko naplate.", PUNCH, 44,
            weight="bold")
    return fig


def slide_08() -> plt.Figure:
    fig = new_slide(8)
    kicker(fig, "Kontrolna točka")
    end = wrapped(fig, TOP,
                  "Marine su jedino mjesto gdje statistika objavljuje i količinu i "
                  "novac za isti skup objekata.", HEAD, 32, weight="bold")

    y = hero(fig, end - GAP,
             f"{hr(FACTS['marina_national_eur_per_berth'])} €",
             f"prihoda po vezu godišnje, na {hr(FACTS['marina_national_berths'])} "
             "vezova. Bez spajanja dvaju izvora.")

    y = wrapped(fig, y - GAP,
                f"Isto vrijedi za hotele. {hr(FACTS['model_551_eur_per_night'])} € po "
                "noćenju, jer prihod i noćenja opisuju iste objekte. I za kampove, "
                f"{hr(FACTS['model_553_eur_per_night'])} €.",
                BODY, 54, color=MUTED)

    wrapped(fig, y - GAP,
            "Kad se brojnik i nazivnik poklope, razlike možemo istraživati. "
            "Kad se ne poklope, ostaje privid preciznosti.",
            PUNCH, 44, weight="bold")
    return fig


def slide_09() -> plt.Figure:
    fig = new_slide(9)
    kicker(fig, "Model, ne nesreća")
    end = wrapped(fig, TOP, "Sastav smještaja stoji šest godina.", HEAD, 32,
                  weight="bold")

    ax = panel(fig, end - 0.265, 0.22)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.0, 0.86, "Sobe i apartmani", fontsize=16.5, color=INK, fontweight="bold")
    ax.text(0.0, 0.62, f"{hr(FACTS['apartment_share_prepandemic'], 1)}%  (2019.)   →   "
                       f"{hr(FACTS['apartment_share_now'], 1)}%  (2025.)",
            fontsize=25, color=INK, fontweight="bold")
    ax.text(0.0, 0.30, "Hoteli", fontsize=16.5, color=INK, fontweight="bold")
    ax.text(0.0, 0.06, f"{hr(FACTS['hotel_share_prepandemic'], 1)}%  (2019.)   →   "
                       f"{hr(FACTS['hotel_share_now'], 1)}%  (2025.)",
            fontsize=25, color=INK, fontweight="bold")

    y = wrapped(fig, end - 0.30,
                f"Hotelska noć u istom razdoblju ide "
                f"{hr(FACTS['hotel_eur_per_night_first'])} → "
                f"{hr(FACTS['hotel_eur_per_night_last'])} €, plus "
                f"{hr(FACTS['hotel_price_growth_pct'])}%. Ekonomski institut upozorava "
                "da rast cijena smještaja može oslabiti cjenovnu konkurentnost.",
                BODY, 54, color=MUTED)

    wrapped(fig, y - GAP,
            "Model može postati skuplji, a ostati isti. To je najlošiji ishod.",
            PUNCH, 44, weight="bold", color=INK)
    return fig


def slide_10() -> plt.Figure:
    fig = new_slide(10)
    kicker(fig, "Što nedostaje")
    end = wrapped(fig, TOP,
                  "Turizmu ne fali još jedan rekord, nego zajednička mjera.",
                  HEAD, 32, weight="bold")

    y = wrapped(fig, end - GAP,
                "Objavljen agregat prihoda kućanstava po noćenju i po registriranoj "
                "postelji pretvorio bi četiri od deset komercijalnih noćenja iz slijepe "
                "točke u dio turističkog računa."
                "\n\n"
                "Bez njega rasprava o rekordima, cijenama i porezu na nekretnine "
                "stalno preskače istu nepoznanicu.",
                BODY, 54, color=MUTED)

    fig.lines.append(
        plt.Line2D([L, L + 0.16], [y - 0.06, y - 0.06], color=ACCENT, lw=2.5,
                   transform=fig.transFigure)
    )
    fig.text(L, y - 0.10, "Cijela analiza, s izvorima i kodom", fontsize=BIGLAB,
             color=MUTED, va="top")
    fig.text(L, y - 0.142, "mislavsag.github.io/CroAIcon", fontsize=26,
             color=ACCENT, fontweight="bold", va="top")
    fig.text(L, y - 0.205,
             "Izvori. DZS statistika turizma, FINA godišnji financijski izvještaji,\n"
             "HNB devizni prihodi, HTZ. Izračun AI.econ.",
             fontsize=14.5, color=MUTED, va="top", linespacing=1.5)
    return fig


BUILDERS = [slide_01, slide_02, slide_03, slide_04, slide_05,
            slide_06, slide_07, slide_08, slide_09, slide_10]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Carousel. turizam bez nazivnika")
    figures = []
    for i, build in enumerate(BUILDERS, start=1):
        fig = build()
        name = f"slide_{i:02d}.png"
        fig.savefig(OUT_DIR / name, dpi=DPI)
        figures.append(fig)
        print(f"   {name}")

    pdf_path = OUT_DIR / "turizam-bez-nazivnika-carousel.pdf"
    with PdfPages(pdf_path) as pdf:
        for fig in figures:
            pdf.savefig(fig)
    for fig in figures:
        plt.close(fig)
    print(f"   {pdf_path.name}")
    print(f"Wrote {len(BUILDERS)} slides to {OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
