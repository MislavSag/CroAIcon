"""Build a four-page 4:5 PDF carousel for the published energy article.

The PDF reads the same ignored facts JSON as the Quarto post. It writes only the
final social artifact to ``output/pdf``; source data and analytical outputs stay
outside version control.
"""

from __future__ import annotations

import json
from pathlib import Path

from matplotlib import font_manager
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


PAPER = "#F7F7F4"
INK = "#18181B"
MUTED = "#71717A"
HAIR = "#E2E2DD"
ACCENT = "#2348E5"
ORANGE = "#C65A1E"
GREEN = "#1C8F5A"
LIGHT_BLUE = "#9EB0F4"
WHITE = "#FFFFFF"

PAGE_W = 1080
PAGE_H = 1350
MARGIN = 86
N_PAGES = 4


def project_root() -> Path:
    current = Path.cwd().resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "_quarto.yml").exists() and (candidate / "outputs").exists():
            return candidate
    raise RuntimeError("Cannot locate the CroAIcon project root.")


ROOT = project_root()
FACTS_PATH = ROOT / "outputs" / "facts" / "energy_attention_balance.json"
OUTPUT_PATH = ROOT / "output" / "pdf" / "energetika-od-racuna-do-krova-carousel.pdf"


def register_fonts() -> None:
    regular = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans"))
    bold = font_manager.findfont(
        font_manager.FontProperties(family="DejaVu Sans", weight="bold")
    )
    mono = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans Mono"))
    pdfmetrics.registerFont(TTFont("HouseSans", regular))
    pdfmetrics.registerFont(TTFont("HouseSansBold", bold))
    pdfmetrics.registerFont(TTFont("HouseMono", mono))


def set_fill(pdf: canvas.Canvas, color: str) -> None:
    pdf.setFillColor(color)


def set_stroke(pdf: canvas.Canvas, color: str) -> None:
    pdf.setStrokeColor(color)


def text_width(text: str, font: str, size: float) -> float:
    return pdfmetrics.stringWidth(text, font, size)


def wrap_lines(text: str, font: str, size: float, max_width: float) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        words = paragraph.split()
        line = words[0]
        for word in words[1:]:
            candidate = f"{line} {word}"
            if text_width(candidate, font, size) <= max_width:
                line = candidate
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_text(
    pdf: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    size: float,
    max_width: float,
    *,
    font: str = "HouseSans",
    color: str = INK,
    leading: float = 1.18,
) -> float:
    lines = wrap_lines(text, font, size, max_width)
    set_fill(pdf, color)
    pdf.setFont(font, size)
    step = size * leading
    for line in lines:
        pdf.drawString(x, y, line)
        y -= step
    return y


def draw_brand(
    pdf: canvas.Canvas,
    page: int,
    source: str,
    *,
    dark: bool = False,
    accent: str = ACCENT,
) -> None:
    base = WHITE if dark else INK
    muted = "#D6D6D2" if dark else MUTED
    set_fill(pdf, accent)
    pdf.rect(MARGIN, PAGE_H - 72, 90, 8, stroke=0, fill=1)
    set_fill(pdf, muted)
    pdf.setFont("HouseMono", 19)
    pdf.drawString(MARGIN, 48, "AI.econ  /  Energetika")
    pdf.drawRightString(PAGE_W - MARGIN, 48, f"{page:02d} / {N_PAGES:02d}")
    pdf.setFont("HouseSans", 16)
    pdf.drawString(MARGIN, 82, source)
    set_stroke(pdf, muted)
    pdf.setLineWidth(1)
    pdf.line(MARGIN, 110, PAGE_W - MARGIN, 110)
    set_fill(pdf, base)


def new_page(pdf: canvas.Canvas, background: str) -> None:
    set_fill(pdf, background)
    pdf.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)


def page_one(pdf: canvas.Canvas, facts: dict) -> None:
    new_page(pdf, PAPER)
    draw_brand(
        pdf,
        1,
        "Izvor: EnergoKlima. Mjesečni udio medijskih objava, 2021.-2023.",
    )
    set_fill(pdf, MUTED)
    pdf.setFont("HouseMono", 24)
    pdf.drawString(MARGIN, 1190, "BRZINA PAŽNJE")
    y = draw_text(
        pdf,
        "Naslovi se mijenjaju u mjesecima.",
        MARGIN,
        1090,
        70,
        PAGE_W - 2 * MARGIN,
        font="HouseSansBold",
        leading=1.08,
    )
    draw_text(
        pdf,
        "Energetski sustav u godinama.",
        MARGIN,
        y - 18,
        70,
        PAGE_W - 2 * MARGIN,
        font="HouseSansBold",
        color=ACCENT,
        leading=1.08,
    )

    peak = facts["media"]["peak_share_pct"]
    set_fill(pdf, ORANGE)
    pdf.circle(MARGIN + 132, 535, 124, stroke=0, fill=1)
    set_fill(pdf, WHITE)
    pdf.setFont("HouseSansBold", 68)
    pdf.drawCentredString(MARGIN + 132, 515, f"{peak:.2f}%".replace(".", ","))

    draw_text(
        pdf,
        "svih medijskih objava u rujnu 2022. govori o energiji i klimi",
        MARGIN + 300,
        610,
        35,
        PAGE_W - MARGIN - (MARGIN + 300),
        font="HouseSansBold",
        leading=1.22,
    )
    draw_text(
        pdf,
        "Pažnja skoči u jednom mjesecu. Elektrane, mreže i grijanje ne mogu.",
        MARGIN,
        315,
        34,
        PAGE_W - 2 * MARGIN,
        color=MUTED,
        leading=1.25,
    )


def page_two(pdf: canvas.Canvas, facts: dict) -> None:
    new_page(pdf, PAPER)
    draw_brand(
        pdf,
        2,
        "Izvor: EIZ, Sektorske analize 123 (2025.). Pokazatelji za 2023.",
        accent=ORANGE,
    )
    set_fill(pdf, MUTED)
    pdf.setFont("HouseMono", 24)
    pdf.drawString(MARGIN, 1190, "BROJ KOJI OSTANE")

    solar = facts["physical"]["renewable_mix_solar"]
    hydro = facts["physical"]["renewable_mix_hydro"]
    set_fill(pdf, ORANGE)
    pdf.setFont("HouseSansBold", 190)
    pdf.drawString(MARGIN, 900, f"{solar:.0f}%")
    draw_text(
        pdf,
        "obnovljive električne energije dolazi iz sunca",
        MARGIN,
        820,
        36,
        620,
        font="HouseSansBold",
        leading=1.15,
    )

    mix = [
        ("Hidro", facts["physical"]["renewable_mix_hydro"], ACCENT),
        ("Vjetar", facts["physical"]["renewable_mix_wind"], LIGHT_BLUE),
        ("Biomasa", facts["physical"]["renewable_mix_biomass"], GREEN),
        ("Sunce", solar, ORANGE),
        ("Ostalo", facts["physical"]["renewable_mix_other"], "#B9B9B2"),
    ]
    set_fill(pdf, MUTED)
    pdf.setFont("HouseMono", 21)
    pdf.drawString(MARGIN, 690, "OBNOVLJIVI MIKS")
    x = MARGIN
    bar_y = 570
    bar_w = PAGE_W - 2 * MARGIN
    for _, value, color in mix:
        width = bar_w * value / 100
        set_fill(pdf, color)
        pdf.rect(x, bar_y, width, 92, stroke=0, fill=1)
        x += width

    set_fill(pdf, ACCENT)
    pdf.setFont("HouseSansBold", 32)
    pdf.drawString(MARGIN, 510, "63% hidro")
    set_fill(pdf, ORANGE)
    pdf.drawRightString(PAGE_W - MARGIN, 510, "4% sunce")

    draw_text(
        pdf,
        "Solar pokazuje smjer. Hidroelektrane još nose rezultat.",
        MARGIN,
        370,
        48,
        PAGE_W - 2 * MARGIN,
        font="HouseSansBold",
        leading=1.14,
    )


def page_three(pdf: canvas.Canvas, facts: dict) -> None:
    new_page(pdf, INK)
    draw_brand(
        pdf,
        3,
        "Izvor: EIZ, FINA GFI i EnergoKlima. Deset najvećih tvrtki, 2023.",
        dark=True,
        accent=ORANGE,
    )
    set_fill(pdf, "#D6D6D2")
    pdf.setFont("HouseMono", 24)
    pdf.drawString(MARGIN, 1190, "KARTA MOĆI")
    draw_text(
        pdf,
        "Sektor izgleda državnije nego što jest.",
        MARGIN,
        1080,
        70,
        PAGE_W - 2 * MARGIN,
        font="HouseSansBold",
        color=WHITE,
        leading=1.08,
    )

    private_revenue = facts["gfi_2023"]["top_ten_private_revenue_share_pct"]
    private_media = facts["gfi_2023"]["media_private_exclusive_share_pct"]
    top_ten = facts["gfi_2023"]["top_ten_share_pct"]
    divider_x = PAGE_W / 2
    set_stroke(pdf, "#52525B")
    pdf.setLineWidth(2)
    pdf.line(divider_x, 430, divider_x, 760)

    set_fill(pdf, ORANGE)
    pdf.setFont("HouseSansBold", 120)
    pdf.drawCentredString(292, 625, f"{private_revenue:.0f}%")
    draw_text(
        pdf,
        "prihoda deset najvećih nose privatne tvrtke",
        120,
        535,
        29,
        340,
        font="HouseSansBold",
        color=WHITE,
        leading=1.2,
    )

    set_fill(pdf, WHITE)
    pdf.setFont("HouseSansBold", 120)
    pdf.drawCentredString(788, 625, f"{private_media:.0f}%")
    draw_text(
        pdf,
        "njihova je isključiva medijska vidljivost",
        620,
        535,
        29,
        340,
        font="HouseSansBold",
        color="#D6D6D2",
        leading=1.2,
    )

    set_fill(pdf, ACCENT)
    pdf.rect(MARGIN, 250, PAGE_W - 2 * MARGIN, 118, stroke=0, fill=1)
    set_fill(pdf, WHITE)
    pdf.setFont("HouseSansBold", 39)
    pdf.drawCentredString(
        PAGE_W / 2,
        292,
        f"10 najvećih = {top_ten:.0f}% prihoda sektora",
    )


def page_four(pdf: canvas.Canvas, facts: dict) -> None:
    del facts
    new_page(pdf, ACCENT)
    draw_brand(
        pdf,
        4,
        "Sažetak analize AI.econ. Od računa za struju do solara na krovu.",
        dark=True,
        accent=ORANGE,
    )
    set_fill(pdf, "#DCE3FF")
    pdf.setFont("HouseMono", 24)
    pdf.drawString(MARGIN, 1190, "ŠTO TREBA ZAPAMTITI")
    draw_text(
        pdf,
        "Pažnja nije tranzicija.",
        MARGIN,
        1065,
        82,
        PAGE_W - 2 * MARGIN,
        font="HouseSansBold",
        color=WHITE,
        leading=1.08,
    )
    draw_text(
        pdf,
        "Tranzicija počinje kada se interes pretvori u instaliranu snagu, toplije domove i manji račun.",
        MARGIN,
        825,
        40,
        PAGE_W - 2 * MARGIN,
        color="#DCE3FF",
        leading=1.25,
    )

    words = [("NASLOV", WHITE), (">", ORANGE), ("KROV", WHITE), (">", ORANGE), ("RAČUN", WHITE)]
    y = 485
    for word, color in words:
        set_fill(pdf, color)
        pdf.setFont("HouseSansBold", 66 if word != ">" else 54)
        pdf.drawCentredString(PAGE_W / 2, y, word)
        y -= 82


def build() -> Path:
    register_fonts()
    facts = json.loads(FACTS_PATH.read_text(encoding="utf-8"))
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT_PATH), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    pdf.setTitle("Od računa za struju do solara na krovu")
    pdf.setAuthor("AI.econ")
    pdf.setSubject("Četverostranični carousel o hrvatskoj energetici")
    for draw_page in (page_one, page_two, page_three, page_four):
        draw_page(pdf, facts)
        pdf.showPage()
    pdf.save()
    return OUTPUT_PATH


if __name__ == "__main__":
    path = build()
    print(path)
