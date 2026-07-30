"""Build the tourism value tables.

Joins DZS tourism statistics (nights, beds, capacity, marina revenue) to FINA GFI firm
revenue from `db_afs`, and computes what one tourist night is actually worth.

DZS counts nights and never counts money. GFI counts money and never counts nights.
This script puts the two on the same key.

Outputs land in outputs/tables/ and outputs/facts/. Charts are drawn by
python/tourism_value_charts.py, which refuses to run if the validation gate here fails.

Reads DZS CSVs from the local dump. Column meanings for db_afs resolve through
_workflow/gfi-variable-map.md (b110 revenue, b061 assets, b063 equity).
"""

from __future__ import annotations

import csv
import json
import os
import unicodedata
from pathlib import Path

import warnings

import numpy as np
import pandas as pd
import pymysql

warnings.filterwarnings("ignore", message=".*SQLAlchemy.*")

# --------------------------------------------------------------------------------------
# paths and configuration
# --------------------------------------------------------------------------------------

DZS_ROOT = Path(r"C:\Users\lsikic\Documents\DZS-Turizam\CSV")
ARRIVALS_DIR = DZS_ROOT / "Dolasci i noćenja turista u komercijalnim smještajnim o"
MARINA_DIR = DZS_ROOT / "Kapaciteti i poslovanje luka nautičkog turizma"
RESIDENT_DIR = DZS_ROOT / "Turistička aktivnost stanovništva Republike Hrvatske"
PLATFORM_DIR = (
    DZS_ROOT / "Eksperimentalne statistike"
    / "Smještaj za kraći boravak turista u Hrvatskoj rezervira"
)

FIRST_YEAR = 2013          # BS_TU12 starts here
LAST_YEAR = 2024           # db_afs ends here
MUNI_YEAR = 2024           # headline year for the municipality ranking

# a municipality enters the ranking only above both thresholds, so a handful of
# firms in a tiny place cannot produce a spectacular ratio
MIN_NIGHTS = 100_000
MIN_FIRMS = 5

NKD_ACCOMMODATION = 55     # hotels, apartments, camps
NKD_FOOD = 56              # restaurants and bars


def project_root() -> Path:
    path = Path.cwd().resolve()
    for candidate in [path, *path.parents]:
        if (candidate / "_quarto.yml").exists() and (candidate / "CroAIcon.Rproj").exists():
            return candidate
    raise RuntimeError("Cannot locate CroAIcon project root.")


ROOT = project_root()
TABLE_DIR = ROOT / "outputs" / "tables"
FACT_DIR = ROOT / "outputs" / "facts"

# Two numbers this post needs are not in the DZS tourism dump and not in GFI. Balance of
# payments travel receipts belong to HNB, and wages by activity to the DZS labour release.
# They live in one small hand-entered file where every row carries its own source and URL,
# rather than being typed into the prose. See the Napomene box in the post.
EXTERNAL_PATH = ROOT / "data" / "external" / "tourism_external.csv"


def external(metric: str, year: int) -> float:
    frame = pd.read_csv(EXTERNAL_PATH, encoding="utf-8-sig")
    hit = frame[(frame["metric"] == metric) & (frame["year"] == year)]
    if hit.empty:
        raise RuntimeError(f"external input missing: {metric} {year}")
    return float(hit["value"].iloc[0])


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def connect() -> pymysql.connections.Connection:
    """Connect with charset latin2. The Croatian label tables (codes_municipal,
    codes_nkd2007) are stored latin2 and come back mojibake under utf8mb4."""
    load_env_file(ROOT / ".env")
    load_env_file(ROOT / ".Renviron")
    required = ["GFI_DB_HOST", "GFI_DB_PORT", "GFI_DB_USER", "GFI_DB_PASSWORD", "GFI_DB_NAME"]
    missing = [key for key in required if not os.environ.get(key)]
    if missing:
        raise RuntimeError(f"Missing database env vars: {', '.join(missing)}")
    return pymysql.connect(
        host=os.environ["GFI_DB_HOST"],
        port=int(os.environ.get("GFI_DB_PORT", "3306")),
        user=os.environ["GFI_DB_USER"],
        password=os.environ["GFI_DB_PASSWORD"],
        database=os.environ["GFI_DB_NAME"],
        connect_timeout=15,
        read_timeout=900,
        charset="latin2",
    )


# --------------------------------------------------------------------------------------
# DZS parsing
# --------------------------------------------------------------------------------------

# Every DZS file obeys one rule. All columns except the last are dimensions, the last
# column holds the value and its header is the table title.
#
# Missing value codes are NOT interchangeable:
#   z    confidential, suppressed. NOT zero. Treating it as zero understates small places.
#   -    no occurrence, a true zero.
#   ..   / ....  not available or not yet published.
MISSING_CODES = {"z", "..", "...", "....."}


def parse_value(raw: str) -> float:
    if raw is None:
        return np.nan
    text = raw.strip()
    if text == "-":
        return 0.0
    if text == "" or text == "z" or text.startswith(".."):
        return np.nan
    try:
        return float(text)
    except ValueError:
        return np.nan


def read_dzs(path: Path) -> pd.DataFrame:
    """Read one DZS CSV. Renames the value column to `value`, keeps the raw string in
    `value_raw` so confidential cells stay distinguishable from true zeros."""
    frame = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    value_col = frame.columns[-1]
    frame = frame.rename(columns={value_col: "value_raw"})
    frame["value"] = frame["value_raw"].map(parse_value)
    frame.attrs["title"] = value_col
    return frame


def parse_year(series: pd.Series) -> pd.Series:
    """Year members are not spelled consistently. The arrivals tables use `2024`, the
    marina tables use `2024.` with the Croatian trailing period."""
    return series.astype(str).str.strip().str.rstrip(".").astype(int)


def norm_name(text: str) -> str:
    """Normalise a place name for matching. Lowercase, strip diacritics, collapse
    separators. Croatian dj/đ handled before the ASCII fold."""
    out = text.strip().lower()
    for src, dst in (("š", "s"), ("đ", "d"), ("č", "c"), ("ć", "c"), ("ž", "z")):
        out = out.replace(src, dst)
    out = unicodedata.normalize("NFKD", out).encode("ascii", "ignore").decode()
    out = out.replace("-", " ").replace(".", " ")
    return " ".join(out.split())


# DZS and GFI disagree on ~10 municipality names. Hyphen and spacing variants fall out
# of norm_name; these are the genuine differences, mapped DZS -> GFI. Kept as a literal
# so the crosswalk is auditable rather than buried in fuzzy matching.
MUNI_ALIASES = {
    "novigrad": "novigrad zadarski",              # DZS has two Novigrads, this is the Zadar one
    "motovun montana": "motovun montona",          # DZS typo, Montana for Montona
    "kastelir labinci castelliere s domenica": "kastelir labinci castelliere s domenica",
    "grad zagreb": "zagreb",
}


# --------------------------------------------------------------------------------------
# BS_TU19, municipality level. Nights, beds, population.
# --------------------------------------------------------------------------------------

NUTS2 = {"Panonska Hrvatska", "Jadranska Hrvatska", "Sjeverna Hrvatska", "Grad Zagreb"}


def read_municipality_panel() -> pd.DataFrame:
    """BS_TU19 mixes four hierarchy levels in one flat column with no indentation, and
    repeats four labels for genuinely different places. The file is ordered
    country -> NUTS-2 -> county -> its municipalities, so county context is recovered
    from row order. Grad Zagreb appears three times in a row (region, county, city)
    with identical values."""
    path = ARRIVALS_DIR / "BS_TU19.csv"
    records = []
    current_county = None
    seen_zagreb_county = False

    with open(path, encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        next(reader)
        for row in reader:
            place, year, indicator, raw = row[0].strip(), row[1], row[2], row[3]

            if place == "Republika Hrvatska":
                level = "country"
            elif place == "Grad Zagreb županija":
                level, current_county = "county", "Grad Zagreb"
                seen_zagreb_county = True
            elif place == "Grad Zagreb":
                # region before the county row, the city itself after it
                level = "municipality" if seen_zagreb_county else "region"
            elif place in NUTS2:
                level = "region"
            elif place.endswith(" županija"):
                level, current_county = "county", place[: -len(" županija")]
            else:
                level = "municipality"

            records.append(
                {
                    "place": place,
                    "county": current_county if level == "municipality" else None,
                    "level": level,
                    "year": int(year),
                    "indicator": indicator,
                    "value": parse_value(raw),
                    "value_raw": raw.strip(),
                }
            )

    return pd.DataFrame.from_records(records)


def municipality_wide(panel: pd.DataFrame, year: int) -> pd.DataFrame:
    """Pivot the municipality rows for one year to one row per place."""
    wanted = {
        "Noćenja turista": "nights",
        "Dolasci turista": "arrivals",
        "Broj stalnih postelja": "beds",
        "Broj stanovnika, Popis 2021.": "population",
        "Prosječan broj noćenja turista po postelji": "nights_per_bed",
    }
    subset = panel[
        (panel["level"] == "municipality")
        & (panel["year"] == year)
        & (panel["indicator"].isin(wanted))
    ].copy()
    subset["metric"] = subset["indicator"].map(wanted)

    # (county, place) is the unique key. `place` alone is not: Otok, Privlaka and
    # Sveta Nedelja each name two different municipalities in different counties.
    wide = subset.pivot_table(
        index=["county", "place"], columns="metric", values="value", aggfunc="first"
    ).reset_index()
    wide.columns.name = None
    return wide


# --------------------------------------------------------------------------------------
# national and county nights
# --------------------------------------------------------------------------------------

def read_national_monthly() -> pd.DataFrame:
    """BS_TU11, national monthly 2005 onwards. The annual total is the month member
    `Ukupno` and the residency total is `ukupno`, both lowercase-sensitive."""
    frame = read_dzs(ARRIVALS_DIR / "BS_TU11.csv")
    frame = frame.rename(
        columns={"Mjesec": "month", "Godina": "year", "Turist": "residency",
                 "Dolasci i noćenja": "measure"}
    )
    frame["year"] = parse_year(frame["year"])
    return frame


def read_county_monthly() -> pd.DataFrame:
    """BS_TU12, county monthly 2013 onwards. Month total is `UKUPNO` (all caps here,
    unlike BS_TU11), residency total is `Ukupno` (title case)."""
    frame = read_dzs(ARRIVALS_DIR / "BS_TU12.csv")
    frame = frame.rename(
        columns={"Županije": "county", "Mjesec": "month", "Tip": "measure",
                 "Godina": "year", "Turisti": "residency"}
    )
    frame["year"] = parse_year(frame["year"])
    return frame


ROMAN_MONTHS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
HR_MONTHS = ["Siječanj", "Veljača", "Ožujak", "Travanj", "Svibanj", "Lipanj", "Srpanj",
             "Kolovoz", "Rujan", "Listopad", "Studeni", "Prosinac"]

# DZS splits nights by NKD 2025 division 55; GFI splits firms by nacerev23. The two
# classifications line up one to one, which is what makes the value-per-model comparison
# possible at all.
ACCOMMODATION_TYPES = {
    "55.1. Hoteli i sličan smještaj": (551, "Hoteli"),
    "55.2. Odmarališta i slični objekti za kraći odmor": (552, "Sobe i apartmani"),
    "55.3. Kampovi i prostori za kampiranje": (553, "Kampovi"),
}
TYPE_TOTAL = "Turistički smještajni objekti - ukupno"


def read_accommodation_types(year: int) -> pd.DataFrame:
    """BS_TU14, nights by accommodation type. Hierarchy is marked by leading whitespace,
    so match on the stripped label. The month total here is `01.-12.`."""
    frame = read_dzs(ARRIVALS_DIR / "BS_TU14.csv").rename(
        columns={"Vrste smještaja": "type", "Godina": "year", "Mjesec": "month",
                 "Smještajni kapaciteti, Dolasci i Noćenja": "measure"}
    )
    frame["year"] = parse_year(frame["year"])
    frame["type_clean"] = frame["type"].str.strip()
    subset = frame[(frame["year"] == year) & (frame["month"] == "01.-12.")]

    nights = subset[subset["measure"] == "Noćenja turista - ukupno"]
    beds = subset[subset["measure"] == "Broj stalnih postelja"]
    nights_map = dict(zip(nights["type_clean"], nights["value"]))
    beds_map = dict(zip(beds["type_clean"], beds["value"]))

    rows = []
    for label, (group, short) in ACCOMMODATION_TYPES.items():
        rows.append({
            "nkd_group": group,
            "label": short,
            "dzs_label": label,
            "nights": nights_map.get(label),
            "beds": beds_map.get(label),
        })
    out = pd.DataFrame(rows)
    out.attrs["total_nights"] = nights_map.get(TYPE_TOTAL)
    out.attrs["total_beds"] = beds_map.get(TYPE_TOTAL)
    return out


# The second level of BS_TU14. Group 55.2 is not one business: it holds rooms, apartments
# and holiday homes on one side and hostels, spas, dormitories and mountain huts on the
# other. Naming the big sub-type is what stops the prose calling the whole group
# `apartmani`. Note what this level still does NOT carry: the operator. DZS splits nights
# by the kind of object, never by whether a household or a company runs it, so the
# household share of these nights is not a measurable quantity here.
SUBTYPE_ROOMS = "Sobe, apartmani, studio-apartmani,  kuće za odmor"   # DZS double space
SUBTYPE_HOSTELS = "Hosteli"


def read_accommodation_subtypes(year: int) -> pd.DataFrame:
    """BS_TU14 second level, nights and beds per sub-type of accommodation.

    Hierarchy carries no id column. A parent row starts at column zero, a child row starts
    with whitespace, and the file is ordered parent then its children, so the parent is
    recovered from row order on the raw, unstripped label."""
    frame = read_dzs(ARRIVALS_DIR / "BS_TU14.csv").rename(
        columns={"Vrste smještaja": "type", "Godina": "year", "Mjesec": "month",
                 "Smještajni kapaciteti, Dolasci i Noćenja": "measure"}
    )
    frame["year"] = parse_year(frame["year"])
    frame["type_clean"] = frame["type"].str.strip()
    frame["is_child"] = frame["type"].str.startswith((" ", "\t"))

    parent_of: dict[str, str] = {}
    current: str | None = None
    for raw, clean, is_child in zip(frame["type"], frame["type_clean"], frame["is_child"]):
        if clean == TYPE_TOTAL:
            continue
        if is_child:
            if current is not None:
                parent_of.setdefault(clean, current)
        else:
            current = clean

    subset = frame[(frame["year"] == year) & (frame["month"] == "01.-12.") & frame["is_child"]]
    nights = dict(zip(
        subset.loc[subset["measure"] == "Noćenja turista - ukupno", "type_clean"],
        subset.loc[subset["measure"] == "Noćenja turista - ukupno", "value"],
    ))
    beds = dict(zip(
        subset.loc[subset["measure"] == "Broj stalnih postelja", "type_clean"],
        subset.loc[subset["measure"] == "Broj stalnih postelja", "value"],
    ))

    rows = []
    for clean, parent in parent_of.items():
        if parent not in ACCOMMODATION_TYPES:
            continue
        group, short = ACCOMMODATION_TYPES[parent]
        rows.append({
            "nkd_group": group,
            "parent_label": short,
            "subtype": clean,
            "nights": nights.get(clean),
            "beds": beds.get(clean),
        })
    return pd.DataFrame(rows).sort_values(["nkd_group", "nights"], ascending=[True, False])


def read_type_share_panel() -> pd.DataFrame:
    """BS_TU14 across all its years, so the mix of accommodation types can be watched
    moving rather than read off one snapshot. The table starts in 2019 and carries a
    residency split, which is what makes it comparable to the published hotel share."""
    frame = read_dzs(ARRIVALS_DIR / "BS_TU14.csv").rename(
        columns={"Vrste smještaja": "type", "Godina": "year", "Mjesec": "month",
                 "Smještajni kapaciteti, Dolasci i Noćenja": "measure"}
    )
    frame["year"] = parse_year(frame["year"])
    frame["type_clean"] = frame["type"].str.strip()
    annual = frame[
        (frame["month"] == "01.-12.") & (frame["type_clean"].isin(ACCOMMODATION_TYPES))
    ].copy()
    annual["label"] = annual["type_clean"].map(lambda t: ACCOMMODATION_TYPES[t][1])

    # DZS spells the residency members with irregular internal spacing. Match on the
    # stripped, collapsed string rather than the literal.
    def measure_key(text: str) -> str:
        return " ".join(str(text).split())

    annual["measure_key"] = annual["measure"].map(measure_key)
    wanted = {
        "Noćenja turista - ukupno": "total",
        "Noćenja turista - strani": "foreign",
        "Noćenja turista - domaći": "domestic",
    }
    annual = annual[annual["measure_key"].isin(wanted)]
    annual["residency"] = annual["measure_key"].map(wanted)

    panel = annual.pivot_table(
        index=["year", "residency"], columns="label", values="value", aggfunc="sum"
    ).reset_index()
    panel.columns.name = None
    labels = [short for _, short in ACCOMMODATION_TYPES.values()]
    panel["total_nights"] = panel[labels].sum(axis=1)
    # 2026 exists as empty placeholder rows in the shipped file
    panel = panel[panel["total_nights"] > 0].copy()
    for label in labels:
        panel[f"share_{label.split()[0].lower()}"] = panel[label] / panel["total_nights"] * 100
    return panel.sort_values(["residency", "year"])


def read_platform_nights() -> pd.DataFrame:
    """DZS experimental statistics. Nights in group 55.2 booked through online platforms.

    The household layer is invisible to financial statistics because it files no accounts,
    but it is not invisible to the platforms that sell it. This is the only official count
    of how much of it is intermediated."""
    frame = read_dzs(PLATFORM_DIR / "T02.csv").rename(
        columns={"Kategorija": "category", "Godina": "year"}
    )
    frame["year"] = parse_year(frame["year"])
    wanted = {
        "Noćenja turista, ukupno": "platform_nights_total",
        "Strani turisti": "platform_nights_foreign",
        "Domaći turisti": "platform_nights_domestic",
    }
    frame["key"] = frame["category"].str.strip().map(wanted)
    out = frame.dropna(subset=["key"]).pivot_table(
        index="year", columns="key", values="value", aggfunc="sum"
    ).reset_index()
    out.columns.name = None
    return out


# --------------------------------------------------------------------------------------
# GFI queries
# --------------------------------------------------------------------------------------

# Every query leads with nacerev21 + reportyear. nacerev22/23 are NOT indexed; a bare
# filter on them full-scans 2,3M rows and times out.

SQL_NATIONAL = """
SELECT reportyear AS year,
       nacerev22  AS nkd_division,
       COUNT(*)                          AS n_firms,
       SUM(COALESCE(b110, 0))            AS revenue,
       SUM(COALESCE(b061, 0))            AS assets,
       SUM(COALESCE(employeecounteop,0)) AS employees,
       AVG(price_deflator)               AS deflator,
       AVG(b110 IS NOT NULL)             AS revenue_coverage
FROM db_afs
WHERE nacerev21 = 'I'
  AND reportyear BETWEEN %s AND %s
  AND nacerev22 IN (%s, %s)
GROUP BY reportyear, nacerev22
ORDER BY reportyear, nacerev22
"""

SQL_MUNICIPALITY = """
SELECT d.reportyear                        AS year,
       d.municipalityid                    AS municipality_id,
       m.naziv                             AS municipality_name,
       d.countyid                          AS county_id,
       COUNT(*)                            AS n_firms,
       SUM(COALESCE(d.b110, 0))            AS revenue,
       SUM(COALESCE(d.b061, 0))            AS assets,
       SUM(COALESCE(d.employeecounteop,0)) AS employees
FROM db_afs d
LEFT JOIN codes_municipal m ON m.municipalID = d.municipalityid
WHERE d.nacerev21 = 'I'
  AND d.reportyear BETWEEN %s AND %s
  AND d.nacerev22 = %s
GROUP BY d.reportyear, d.municipalityid, m.naziv, d.countyid
"""

SQL_MODEL_SPLIT = """
SELECT reportyear             AS year,
       nacerev23              AS nkd_group,
       COUNT(*)               AS n_firms,
       SUM(COALESCE(b110,0))  AS revenue,
       SUM(COALESCE(b061,0))  AS assets,
       SUM(COALESCE(b152,0) - COALESCE(b153,0)) AS net_result,
       SUM(COALESCE(employeecounteop,0))        AS employees
FROM db_afs
WHERE nacerev21 = 'I'
  AND reportyear BETWEEN %s AND %s
  AND nacerev22 = 55
GROUP BY reportyear, nacerev23
ORDER BY reportyear, nacerev23
"""

# One row per firm, so concentration is computed here rather than trusted from anyone's
# summary. EIZ, Sektorske analize br. 126, reports that the ten largest firms take 41,2% of
# the revenue of NKD 55.10. Reproducing that from the raw base is what licenses the rest of
# the comparison, and it is also how the 3,0 vs 3,25 mlrd. discrepancy in their text resolves.
SQL_FIRM_REVENUE = """
SELECT nacerev23             AS nkd_group,
       b110                  AS revenue,
       COALESCE(employeecounteop, 0) AS employees
FROM db_afs
WHERE nacerev21 = 'I'
  AND reportyear = %s
  AND nacerev22 = 55
  AND b110 > 0
ORDER BY b110 DESC
"""

SQL_BALANCE_CHECK = """
SELECT COUNT(*) AS n,
       AVG(ABS(COALESCE(b061,0) - COALESCE(b108,0)) < 1) AS identity_ok
FROM db_afs
WHERE nacerev21 = 'I' AND reportyear = %s AND nacerev22 = 55 AND b061 > 0
"""

# County is the honest grain for revenue per night. At municipality level the big coastal
# groups book a whole neighbourhood's camps at their own address, so Vrsar and Funtana
# read near zero while Rovinj and Poreč read high. Inside a county that displacement
# nets out.
SQL_COUNTY = """
SELECT d.countyid                          AS county_id,
       COUNT(*)                            AS n_firms,
       SUM(COALESCE(d.b110, 0))            AS revenue,
       SUM(COALESCE(d.b061, 0))            AS assets,
       SUM(COALESCE(d.employeecounteop,0)) AS employees
FROM db_afs d
WHERE d.nacerev21 = 'I'
  AND d.reportyear = %s
  AND d.nacerev22 = 55
GROUP BY d.countyid
"""

# countyid is the official Croatian county numbering, which is also the member order of
# the Županije dimension in BS_TU12 after dropping the national row.
COUNTY_NAMES = {
    1: "ZAGREBAČKA", 2: "KRAPINSKO-ZAGORSKA", 3: "SISAČKO-MOSLAVAČKA", 4: "KARLOVAČKA",
    5: "VARAŽDINSKA", 6: "KOPRIVNIČKO-KRIŽEVAČKA", 7: "BJELOVARSKO-BILOGORSKA",
    8: "PRIMORSKO-GORANSKA", 9: "LIČKO-SENJSKA", 10: "VIROVITIČKO-PODRAVSKA",
    11: "POŽEŠKO-SLAVONSKA", 12: "BRODSKO-POSAVSKA", 13: "ZADARSKA",
    14: "OSJEČKO-BARANJSKA", 15: "ŠIBENSKO-KNINSKA", 16: "VUKOVARSKO-SRIJEMSKA",
    17: "SPLITSKO-DALMATINSKA", 18: "ISTARSKA", 19: "DUBROVAČKO-NERETVANSKA",
    20: "MEĐIMURSKA", 21: "GRAD ZAGREB",
}
COASTAL_COUNTIES = [8, 9, 13, 15, 17, 18, 19]

# Zagreb books the highest revenue per night in the country, which invites the objection
# that it is just coastal groups registered at a Zagreb address. This query tests it. A
# head-office artefact would show FEWER, LARGER firms and very high revenue per employee.
# The opposite pattern means the number is real city-hotel business.
SQL_SEAT_CHECK = """
SELECT countyid AS county_id, b110 AS revenue, employeecounteop AS employees
FROM db_afs
WHERE nacerev21 = 'I' AND reportyear = %s AND nacerev22 = 55
  AND countyid IN (18, 21) AND b110 > 0
ORDER BY countyid, b110 DESC
"""

COUNTY_LABELS = {
    8: "Primorsko-goranska", 9: "Ličko-senjska", 13: "Zadarska", 15: "Šibensko-kninska",
    17: "Splitsko-dalmatinska", 18: "Istarska", 19: "Dubrovačko-neretvanska",
    21: "Grad Zagreb",
}


# --------------------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------------------

def main() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FACT_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict] = []
    facts: dict = {}

    def check(rule: str, passed: bool, detail: str) -> None:
        checks.append({"rule": rule, "passed": bool(passed), "detail": detail})
        flag = "ok  " if passed else "FAIL"
        print(f"   [{flag}] {rule}. {detail}")

    print("reading DZS ...")
    national = read_national_monthly()
    county = read_county_monthly()
    muni_panel = read_municipality_panel()

    # ---------------------------------------------------------------- national nights
    nights_nat = (
        national[
            (national["month"] == "Ukupno")
            & (national["residency"] == "ukupno")
            & (national["measure"] == "noćenja")
        ]
        .set_index("year")["value"]
        .dropna()
    )
    arrivals_nat = (
        national[
            (national["month"] == "Ukupno")
            & (national["residency"] == "ukupno")
            & (national["measure"] == "dolasci")
        ]
        .set_index("year")["value"]
        .dropna()
    )

    # Nights and arrivals side by side, by residency. Nights per arrival is the length of
    # one stay, and it is falling while the nights total rises. The headline count grows
    # because more people come, not because they buy more.
    stay = (
        national[national["month"] == "Ukupno"]
        .pivot_table(index=["year", "residency"], columns="measure",
                     values="value", aggfunc="sum")
        .reset_index()
    )
    stay.columns.name = None
    stay = stay[(stay["noćenja"] > 0) & (stay["dolasci"] > 0)].copy()
    stay["nights_per_arrival"] = stay["noćenja"] / stay["dolasci"]
    stay = stay[stay["year"].between(FIRST_YEAR, LAST_YEAR)]
    stay_wide = stay.pivot_table(
        index="year", columns="residency", values="nights_per_arrival"
    )

    # ------------------------------------------------- VALIDATION. reproduce DZS first
    # House rule: match someone else's headline before extending it. The same national
    # nights total must fall out of three independent tables.
    nights_cty = (
        county[
            (county["county"] == "REPUBLIKA HRVATSKA")
            & (county["month"] == "UKUPNO")
            & (county["measure"] == "Noćenja")
            & (county["residency"] == "Ukupno")
        ]
        .set_index("year")["value"]
        .dropna()
    )
    overlap = sorted(set(nights_nat.index) & set(nights_cty.index) & set(range(FIRST_YEAR, LAST_YEAR + 1)))
    diffs = [(y, nights_nat[y], nights_cty[y]) for y in overlap]
    worst = max((abs(a - b) / b for _, a, b in diffs), default=1.0)
    check("dzs_national_vs_county", worst < 0.001,
          f"BS_TU11 vs BS_TU12 national nights, {len(overlap)} years, max rel. diff {worst:.5f}")

    nights_muni_nat = muni_panel[
        (muni_panel["level"] == "country")
        & (muni_panel["indicator"] == "Noćenja turista")
    ].set_index("year")["value"]
    y = MUNI_YEAR
    rel = abs(nights_muni_nat.get(y, np.nan) - nights_nat.get(y, np.nan)) / nights_nat.get(y, np.nan)
    check("dzs_national_vs_municipality_table", rel < 0.001,
          f"BS_TU19 vs BS_TU11 national nights {y}, rel. diff {rel:.5f}")

    # sum of municipality leaves must reconstruct the national total, which is the real
    # test that the hierarchy walk found the right rows
    leaves = municipality_wide(muni_panel, MUNI_YEAR)
    leaf_sum = leaves["nights"].sum()
    rel_leaf = abs(leaf_sum - nights_nat[MUNI_YEAR]) / nights_nat[MUNI_YEAR]
    check("municipality_leaves_sum_to_national", rel_leaf < 0.02,
          f"{len(leaves)} municipalities sum to {leaf_sum:,.0f} vs national "
          f"{nights_nat[MUNI_YEAR]:,.0f}, gap {rel_leaf:.3%} (confidential cells)")

    print("\nquerying GFI ...")
    conn = connect()
    try:
        nat_fin = pd.read_sql(
            SQL_NATIONAL, conn,
            params=[FIRST_YEAR, LAST_YEAR, NKD_ACCOMMODATION, NKD_FOOD],
        )
        muni_fin = pd.read_sql(
            SQL_MUNICIPALITY, conn,
            params=[MUNI_YEAR - 3, LAST_YEAR, NKD_ACCOMMODATION],
        )
        models = pd.read_sql(SQL_MODEL_SPLIT, conn, params=[FIRST_YEAR, LAST_YEAR])
        balance = pd.read_sql(SQL_BALANCE_CHECK, conn, params=[MUNI_YEAR])
        county_fin = pd.read_sql(SQL_COUNTY, conn, params=[LAST_YEAR])
        seat = pd.read_sql(SQL_SEAT_CHECK, conn, params=[LAST_YEAR])
        firms = pd.read_sql(SQL_FIRM_REVENUE, conn, params=[LAST_YEAR])
    finally:
        conn.close()

    # ------------------------------------------------ concentration, and the EIZ crosscheck
    # Ten firms against everyone else, computed from firm-level rows. The hotel figure is a
    # published number elsewhere, so it doubles as an external check on our revenue base.
    def top_share(block: pd.DataFrame, n: int = 10) -> float:
        return float(block["revenue"].head(n).sum() / block["revenue"].sum() * 100)

    hotels = firms[firms["nkd_group"] == 551].sort_values("revenue", ascending=False)
    all_55 = firms.sort_values("revenue", ascending=False)
    top10_hotels_pct = top_share(hotels)
    top10_all_pct = top_share(all_55)
    top10_hotels_revenue = float(hotels["revenue"].head(10).sum())

    eiz_share = external("eiz_top10_share_5510", LAST_YEAR)
    eiz_top10_revenue = external("eiz_top10_revenue_5510", LAST_YEAR)
    # EIZ's text says the activity earned 3,0 mlrd, but their own top-ten table divided by
    # their own 41,2% implies 3,31 mlrd. Ours is 3,25 mlrd of operating revenue, which is
    # what a slightly narrower revenue definition should give. The share is the real test.
    eiz_implied_total = eiz_top10_revenue / (eiz_share / 100)
    check("concentration_matches_eiz", abs(top10_hotels_pct - eiz_share) < 1.5,
          f"top ten hotel firms take {top10_hotels_pct:.1f}% of the activity's revenue, "
          f"EIZ reports {eiz_share:.1f}%")
    check("revenue_base_matches_eiz_implied", abs(hotels["revenue"].sum() / eiz_implied_total - 1) < 0.05,
          f"our 55.1 revenue {hotels['revenue'].sum()/1e9:.2f} mlrd vs EIZ implied "
          f"{eiz_implied_total/1e9:.2f} mlrd (their text says 3,0, their table says otherwise)")

    # Is Zagreb's high revenue per night a registered-seat artefact?
    seat_stats = {}
    for cid, name in ((21, "zagreb"), (18, "istra")):
        block = seat[seat["county_id"] == cid].sort_values("revenue", ascending=False)
        total = block["revenue"].sum()
        seat_stats[f"{name}_top10_share_pct"] = float(
            block["revenue"].head(10).sum() / total * 100
        )
        seat_stats[f"{name}_revenue_per_employee"] = float(
            total / max(block["employees"].sum(), 1)
        )
    # A seat artefact concentrates revenue in a few staffless firms. Zagreb showing LOWER
    # concentration and LOWER revenue per employee than Istria refutes that reading.
    seat_artefact_refuted = (
        seat_stats["zagreb_top10_share_pct"] < seat_stats["istra_top10_share_pct"]
        and seat_stats["zagreb_revenue_per_employee"] < seat_stats["istra_revenue_per_employee"]
    )
    check("zagreb_not_a_seat_artefact", seat_artefact_refuted,
          f"Zagreb top-10 concentration {seat_stats['zagreb_top10_share_pct']:.1f}% vs Istria "
          f"{seat_stats['istra_top10_share_pct']:.1f}%, revenue per employee "
          f"{seat_stats['zagreb_revenue_per_employee']:,.0f} vs "
          f"{seat_stats['istra_revenue_per_employee']:,.0f}")

    cov = nat_fin.loc[nat_fin["nkd_division"] == NKD_ACCOMMODATION, "revenue_coverage"].min()
    check("revenue_coverage", cov >= 0.85,
          f"b110 populated for {cov:.1%} of accommodation firms, worst year")
    check("balance_identity", float(balance["identity_ok"].iloc[0]) > 0.99,
          f"b061 = b108 holds for {float(balance['identity_ok'].iloc[0]):.2%} of accommodation firms")

    # ------------------------------------------------------- 1. euros per night, national
    acc = nat_fin[nat_fin["nkd_division"] == NKD_ACCOMMODATION].set_index("year")
    food = nat_fin[nat_fin["nkd_division"] == NKD_FOOD].set_index("year")

    per_night = pd.DataFrame({
        "year": sorted(set(acc.index) & set(nights_nat.index)),
    })
    per_night["nights"] = per_night["year"].map(nights_nat)
    per_night["arrivals"] = per_night["year"].map(arrivals_nat)
    per_night["revenue_accommodation"] = per_night["year"].map(acc["revenue"])
    per_night["revenue_food"] = per_night["year"].map(food["revenue"])
    per_night["firms_accommodation"] = per_night["year"].map(acc["n_firms"])
    per_night["deflator"] = per_night["year"].map(acc["deflator"])
    per_night["eur_per_night"] = per_night["revenue_accommodation"] / per_night["nights"]
    per_night["eur_per_night_with_food"] = (
        (per_night["revenue_accommodation"] + per_night["revenue_food"]) / per_night["nights"]
    )
    # real terms, rebased to the last year with a deflator. 2024 has none, so the real
    # series stops one year short of the nominal one and the chart says so.
    base_year = int(per_night.loc[per_night["deflator"].notna(), "year"].max())
    base = float(per_night.loc[per_night["year"] == base_year, "deflator"].iloc[0])
    per_night["eur_per_night_real"] = np.where(
        per_night["deflator"].notna(),
        per_night["eur_per_night"] * base / per_night["deflator"],
        np.nan,
    )
    per_night["real_base_year"] = base_year

    per_night["nights_per_arrival"] = per_night["nights"] / per_night["arrivals"]
    per_night["eur_per_arrival"] = per_night["revenue_accommodation"] / per_night["arrivals"]

    anchor = float(per_night.loc[per_night["year"] == LAST_YEAR, "eur_per_night"].iloc[0])
    check("macro_anchor_eur_per_night", 15 <= anchor <= 80,
          f"{LAST_YEAR} accommodation revenue per night is {anchor:.1f} EUR")

    # -------------------------------------- 1b. what the country takes against what firms take
    # HNB counts every euro a non-resident spends inside Croatia on travel. GFI counts what
    # accommodation companies book. The distance between the two is the rest of the tourist
    # economy: restaurants, shops, transport, excursions, and the households renting rooms.
    #
    # The two populations are not identical, so the comparison is built to be unfalsifiable.
    # Foreign receipts are divided by FOREIGN nights only. Accommodation revenue is divided by
    # the same foreign nights even though some of it comes from domestic guests, which makes
    # the firms' share an upper bound. The real number can only be lower than what we print.
    foreign_by_year = (
        national[
            (national["month"] == "Ukupno")
            & (national["measure"] == "noćenja")
            & (national["residency"] == "strani")
        ]
        .set_index("year")["value"]
        .dropna()
    )
    gap_rows = []
    for gap_year in (2019, LAST_YEAR):
        receipts = external("hnb_travel_receipts", gap_year)
        f_nights = float(foreign_by_year[gap_year])
        acc_rev = float(per_night.loc[per_night["year"] == gap_year, "revenue_accommodation"].iloc[0])
        food_rev = float(per_night.loc[per_night["year"] == gap_year, "revenue_food"].iloc[0])
        gap_rows.append({
            "year": gap_year,
            "hnb_receipts": receipts,
            "foreign_nights": f_nights,
            "eur_per_foreign_night": receipts / f_nights,
            "accommodation_revenue": acc_rev,
            "accommodation_per_foreign_night": acc_rev / f_nights,
            "accommodation_share_pct": acc_rev / receipts * 100,
            "food_revenue": food_rev,
            "food_per_foreign_night": food_rev / f_nights,
            "rest_per_foreign_night": (receipts - acc_rev - food_rev) / f_nights,
        })
    gap = pd.DataFrame(gap_rows)
    gap_last = gap[gap["year"] == LAST_YEAR].iloc[0]
    check("hnb_gap_sane", 15 <= gap_last["accommodation_share_pct"] <= 40,
          f"accommodation firms book {gap_last['accommodation_share_pct']:.1f}% of the "
          f"{gap_last['hnb_receipts']/1e9:.2f} mlrd foreign guests spend, "
          f"{gap_last['eur_per_foreign_night']:.0f} EUR per foreign night in total")

    # -------------------------------------------------- 2. euros per night, municipality
    muni_fin_y = muni_fin[muni_fin["year"] == MUNI_YEAR].copy()
    muni_fin_y["key"] = muni_fin_y["municipality_name"].fillna("").map(norm_name)

    leaves = leaves.copy()
    leaves["key"] = leaves["place"].map(norm_name).replace(MUNI_ALIASES)

    matched = leaves.merge(muni_fin_y, on="key", how="left", suffixes=("", "_gfi"))
    match_rate = matched["revenue"].notna().mean()
    # weight by nights, since matching a large destination matters more than a hamlet
    weighted = (
        matched.loc[matched["revenue"].notna(), "nights"].sum()
        / matched["nights"].sum()
    )
    check("municipality_match_rate", weighted >= 0.98,
          f"{match_rate:.1%} of names matched, {weighted:.1%} weighted by nights")

    ranked = matched[
        (matched["nights"] >= MIN_NIGHTS)
        & (matched["n_firms"] >= MIN_FIRMS)
        & (matched["revenue"] > 0)
    ].copy()
    ranked["eur_per_night"] = ranked["revenue"] / ranked["nights"]
    ranked["beds_per_firm"] = ranked["beds"] / ranked["n_firms"]
    ranked["revenue_per_bed"] = ranked["revenue"] / ranked["beds"]
    ranked = ranked.sort_values("eur_per_night", ascending=False)

    # ------------------------------------------- 2b. euros per night, by county (headline)
    cty_nights = (
        county[
            (county["month"] == "UKUPNO")
            & (county["measure"] == "Noćenja")
            & (county["residency"] == "Ukupno")
            & (county["year"] == LAST_YEAR)
        ]
        .set_index("county")["value"]
    )
    county_fin["county_name"] = county_fin["county_id"].map(COUNTY_NAMES)
    county_fin["nights"] = county_fin["county_name"].map(cty_nights)
    county_fin["label"] = county_fin["county_id"].map(COUNTY_LABELS)
    county_fin["is_coastal"] = county_fin["county_id"].isin(COASTAL_COUNTIES)
    county_fin["eur_per_night"] = county_fin["revenue"] / county_fin["nights"]
    county_value = county_fin[
        county_fin["county_id"].isin(COASTAL_COUNTIES + [21])
    ].sort_values("eur_per_night", ascending=False)

    coastal = county_value[county_value["is_coastal"]]
    check("coastal_spread_sane", coastal["eur_per_night"].between(5, 120).all(),
          f"coastal counties span {coastal['eur_per_night'].min():.1f} to "
          f"{coastal['eur_per_night'].max():.1f} EUR per night")

    # ----------------------------- 3. what each accommodation model earns from one night
    # The heart of the post. DZS division 55 subclasses map one to one onto GFI nacerev23,
    # so nights and company revenue can be compared model by model. Half of Croatia's
    # nights sit in rooms and apartments, a category that barely exists as companies.
    types = read_accommodation_types(LAST_YEAR)
    model_rev = models[models["year"] == LAST_YEAR].set_index("nkd_group")
    model_value = types.copy()
    model_value["revenue"] = model_value["nkd_group"].map(model_rev["revenue"])
    model_value["n_firms"] = model_value["nkd_group"].map(model_rev["n_firms"])
    model_value["employees"] = model_value["nkd_group"].map(model_rev["employees"])
    model_value["assets"] = model_value["nkd_group"].map(model_rev["assets"])
    model_value["eur_per_night"] = model_value["revenue"] / model_value["nights"]
    model_value["eur_per_bed"] = model_value["revenue"] / model_value["beds"]
    model_value["nights_share_pct"] = (
        model_value["nights"] / types.attrs["total_nights"] * 100
    )
    model_value["revenue_share_pct"] = (
        model_value["revenue"] / model_value["revenue"].sum() * 100
    )

    # ------------------------------- 3a. what the headline ratio is, and what it is not
    # The national ratio divides COMPANY revenue by EVERYBODY'S nights. In hotels and camps
    # those two populations coincide, because no household runs a hotel, so the per-night
    # figure there is a genuine price. In 55.2 they do not: roughly 1.700 companies sit in a
    # segment of 732.000 beds that households overwhelmingly operate.
    #
    # So 55.2 gets NO per-night figure in the post. The quotient is not a cheap price, and it
    # is not a capture rate either, because DZS never splits nights by operator. How many of
    # those 46,6 million nights belong to the 1.691 companies is unknown and cannot be
    # recovered from this dump. The column stays here as a diagnostic and is deliberately
    # withheld from the facts file, so the prose cannot reach for it. See `facts` below.
    #
    # 40 EUR is a capture rate for the whole country. 75 EUR is what a night earns where the
    # measurement is clean.
    matched_segments = model_value[model_value["nkd_group"].isin([551, 553])]
    eur_per_night_matched = float(
        matched_segments["revenue"].sum() / matched_segments["nights"].sum()
    )
    model_value["nights_per_bed"] = model_value["nights"] / model_value["beds"]
    check("apartment_rate_is_not_a_price", model_value.loc[
              model_value["nkd_group"] == 552, "eur_per_night"].iloc[0] < 10,
          f"55.2 reads {model_value.loc[model_value['nkd_group']==552,'eur_per_night'].iloc[0]:.2f} "
          f"EUR per night, below any survivable rate, which is the population mismatch showing. "
          f"Matched segments (hotels + camps) read {eur_per_night_matched:.1f} EUR")

    type_total = types.attrs["total_nights"]
    rel_types = abs(model_value["nights"].sum() - type_total) / type_total
    rel_types_cov = (1 - rel_types) * 100
    check("accommodation_types_sum", rel_types < 0.01,
          f"three models cover {rel_types_cov:.2f}% of national nights "
          f"(55.9 other accommodation is the remainder)")

    # --------------------------- 3a2. what group 55.2 actually holds, one level deeper
    # Calling the whole of 55.2 `apartmani` is what let the earlier draft slide from a type
    # share to an ownership share. The sub-types name the denominator exactly: rooms,
    # apartments and holiday homes on one side, hostels and institutional accommodation on
    # the other. Still no operator split, which is the point.
    subtypes = read_accommodation_subtypes(LAST_YEAR)
    sub_552 = subtypes[subtypes["nkd_group"] == 552]
    nights_552 = float(model_value.loc[model_value["nkd_group"] == 552, "nights"].iloc[0])
    rel_sub = abs(sub_552["nights"].sum() - nights_552) / nights_552
    check("subtypes_sum_to_552", rel_sub < 0.001,
          f"{len(sub_552)} sub-types of 55.2 sum to {sub_552['nights'].sum():,.0f} nights vs "
          f"the published group total {nights_552:,.0f}, rel. diff {rel_sub:.5f}")

    rooms = sub_552[sub_552["subtype"] == SUBTYPE_ROOMS]
    if rooms.empty:
        raise RuntimeError(f"BS_TU14 sub-type not found: {SUBTYPE_ROOMS!r}")
    rooms_nights = float(rooms["nights"].iloc[0])
    rooms_beds = float(rooms["beds"].iloc[0])
    hostel_nights = float(
        sub_552.loc[sub_552["subtype"] == SUBTYPE_HOSTELS, "nights"].iloc[0]
    )
    # The big sub-type has to dominate its group, otherwise the prose cannot use `sobe,
    # apartmani i kuće za odmor` as a stand-in for the segment at all.
    check("rooms_dominate_552", rooms_nights / nights_552 > 0.9,
          f"rooms, apartments and holiday homes are {rooms_nights/1e6:.1f}M of the "
          f"{nights_552/1e6:.1f}M nights in 55.2 ({rooms_nights/nights_552:.1%}), "
          f"{rooms_beds:,.0f} beds")

    # ------------------------------------------- 3b. the mix, moving rather than as a snapshot
    # Whether Croatia is stuck in the cheap model or slowly leaving it is a question the
    # single-year split cannot answer. This panel can.
    type_panel = read_type_share_panel()
    mix_total = type_panel[type_panel["residency"] == "total"].set_index("year")
    mix_first_year = int(mix_total.index.min())
    mix_last_year = int(mix_total.index.max())
    # 2020 and 2021 are closed borders and a collapsed hotel sector; the trough there is the
    # pandemic, not a change of model. The prose dates the recovery from 2021 for that reason.
    hotel_share_now = float(mix_total.loc[mix_last_year, "share_hoteli"])
    hotel_share_2021 = float(mix_total.loc[2021, "share_hoteli"])
    # The published reading of this series is "the hotel share is rising". Measured from the
    # 2021 trough it is. Measured from 2019 it is not: the share is still below where the
    # pandemic found it. Six years of recovery, not a change of model. Both anchors are kept
    # so the prose cannot quietly pick the flattering one.
    hotel_share_prepandemic = float(mix_total.loc[mix_first_year, "share_hoteli"])
    check("hotel_share_not_yet_recovered", hotel_share_now <= hotel_share_prepandemic + 0.5,
          f"hotel share {hotel_share_prepandemic:.1f}% ({mix_first_year}) -> "
          f"{hotel_share_2021:.1f}% (2021) -> {hotel_share_now:.1f}% ({mix_last_year}), "
          f"still {hotel_share_prepandemic - hotel_share_now:.1f} pp below pre-pandemic")

    # ------------------------------------- 3b2. the one defensible price series in the post
    # Hotel revenue over hotel nights, both populations identical, so this is an actual
    # price and can be tracked through time. It only starts in 2019 because that is when
    # nights by accommodation type begin. Everything earlier would have to divide hotel
    # revenue by a nights total that includes households, which is the very error the post
    # is at pains to avoid.
    hotel_rev = models[models["nkd_group"] == 551].set_index("year")["revenue"]
    hotel_price = pd.DataFrame({"year": sorted(set(mix_total.index) & set(hotel_rev.index))})
    hotel_price["nights"] = hotel_price["year"].map(mix_total["Hoteli"])
    hotel_price["revenue"] = hotel_price["year"].map(hotel_rev)
    hotel_price["eur_per_night"] = hotel_price["revenue"] / hotel_price["nights"]
    hp_first = hotel_price.iloc[0]
    hp_last = hotel_price[hotel_price["year"] == LAST_YEAR].iloc[0]
    check("hotel_price_series_is_clean", 60 <= hp_first["eur_per_night"] <= 200,
          f"hotel EUR per night {hp_first['eur_per_night']:.0f} ({int(hp_first['year'])}) -> "
          f"{hp_last['eur_per_night']:.0f} ({LAST_YEAR}), "
          f"+{hp_last['eur_per_night']/hp_first['eur_per_night']*100-100:.0f}%")

    # ----------------------------------- 3c. the household layer, as the platforms see it
    # It files no accounts, so financial statistics cannot see it. Booking and Airbnb can.
    platforms = read_platform_nights()
    platform_last = platforms[platforms["year"] == LAST_YEAR].iloc[0]
    apartment_nights = float(
        model_value.loc[model_value["nkd_group"] == 552, "nights"].iloc[0]
    )
    platform_share_of_apartments = (
        float(platform_last["platform_nights_total"]) / apartment_nights * 100
    )
    check("platform_nights_within_segment", 0 < platform_share_of_apartments < 100,
          f"{platform_last['platform_nights_total']/1e6:.1f}M of the {apartment_nights/1e6:.1f}M "
          f"nights in rooms and apartments were booked through platforms "
          f"({platform_share_of_apartments:.0f}%)")

    # How big the published collection is, counted from the shipped index rather than
    # tallied by hand. The opener leans on this, so it traces like every other number.
    index_path = DZS_ROOT.parent / "_tables-index.csv"
    dzs_index = pd.read_csv(index_path, encoding="utf-8-sig")
    dzs_tables = len(dzs_index)
    dzs_files = int(dzs_index["n_files"].sum())
    check("dzs_collection_counted", dzs_tables > 0 and dzs_files >= dzs_tables,
          f"DZS collection is {dzs_tables} tables in {dzs_files} files")

    # --------------------------------------------------- 4. beds with and without a firm
    # GFI sees only registered companies. DZS counts every bed, including the apartment
    # a household rents out. The gap between them is the household layer.
    beds = matched[matched["beds"].notna() & (matched["beds"] > 0)].copy()
    beds["n_firms"] = beds["n_firms"].fillna(0)
    beds["revenue"] = beds["revenue"].fillna(0)
    beds["beds_per_firm"] = beds["beds"] / beds["n_firms"].replace(0, np.nan)
    national_beds = float(beds["beds"].sum())
    national_firms = float(beds["n_firms"].sum())

    # --------------------------------------------------------------- 4. seasonality
    months = national[
        (national["month"].isin(HR_MONTHS))
        & (national["residency"] == "ukupno")
        & (national["measure"] == "noćenja")
    ].copy()
    months["month_no"] = months["month"].map({m: i + 1 for i, m in enumerate(HR_MONTHS)})
    season = (
        months[months["year"].between(FIRST_YEAR, LAST_YEAR)]
        .pivot_table(index="year", columns="month_no", values="value", aggfunc="sum")
    )
    season_share = season.div(season.sum(axis=1), axis=0) * 100
    peak_share = season_share[[7, 8]].sum(axis=1)

    cty_months = county[
        (county["month"].isin(ROMAN_MONTHS))
        & (county["measure"] == "Noćenja")
        & (county["residency"] == "Ukupno")
        & (county["county"] != "REPUBLIKA HRVATSKA")
        & (county["year"] == LAST_YEAR)
    ].copy()
    cty_months["month_no"] = cty_months["month"].map({m: i + 1 for i, m in enumerate(ROMAN_MONTHS)})
    cty_pivot = cty_months.pivot_table(index="county", columns="month_no", values="value", aggfunc="sum")
    cty_season = pd.DataFrame({
        "county": cty_pivot.index,
        "nights": cty_pivot.sum(axis=1).values,
        "peak_share_pct": (cty_pivot[[7, 8]].sum(axis=1) / cty_pivot.sum(axis=1) * 100).values,
    }).sort_values("peak_share_pct", ascending=False)

    # ------------------------------------------------------------- 5. domestic share
    dom = national[
        (national["month"] == "Ukupno")
        & (national["measure"] == "noćenja")
        & (national["residency"].isin(["domaći", "strani"]))
    ].pivot_table(index="year", columns="residency", values="value", aggfunc="sum")
    dom = dom.dropna()
    dom["total"] = dom["domaći"] + dom["strani"]
    # 2026 exists as placeholder rows that parse to zero. Keep only complete years.
    dom = dom[dom["total"] > 0]
    dom["domestic_share_pct"] = dom["domaći"] / dom["total"] * 100
    dom = dom.reset_index()

    # ----------------------------------------------------------- 6. marina per berth
    # Computed from DZS alone. Both revenue and berths are published, so this needs no
    # firm matching. GFI's marina code (5222) captures a different population and is
    # not used here.
    berths = read_dzs(MARINA_DIR / "BS_TU18_02.csv").rename(
        columns={"Kapacitet, zaposleni": "metric", "Godina": "year", "Prostorna jedinica": "place"}
    )
    berths["year"] = parse_year(berths["year"])
    berth_count = berths[berths["metric"] == "Broj vezova, ukupno"][["place", "year", "value"]]
    berth_count = berth_count.rename(columns={"value": "berths"})
    seasonal = berths[berths["metric"] == "Od toga sezonski zaposleni"][["place", "year", "value"]]
    seasonal = seasonal.rename(columns={"value": "seasonal_staff"})
    staff = berths[berths["metric"] == "Broj zaposlenih, ukupno"][["place", "year", "value"]]
    staff = staff.rename(columns={"value": "staff"})

    marina_rev = read_dzs(MARINA_DIR / "BS_TU18_11.csv").rename(
        columns={"Prostorna jedinica": "place", "Godina": "year", "Vrsta prihoda": "metric"}
    )
    marina_rev["year"] = parse_year(marina_rev["year"])
    # euro members only. Kuna and euro run in parallel across the whole period and
    # summing the measure dimension would double-count the money.
    rev_eur = marina_rev[marina_rev["metric"] == "Ukupan prihod (tis. euro)"][["place", "year", "value"]]
    rev_eur = rev_eur.rename(columns={"value": "revenue_thousand_eur"})
    # the two tables spell the national total differently
    rev_eur["place"] = rev_eur["place"].replace({"Republika Hrvatska, ukupno": "Republika Hrvatska"})

    marina = (
        berth_count.merge(rev_eur, on=["place", "year"], how="inner")
        .merge(staff, on=["place", "year"], how="left")
        .merge(seasonal, on=["place", "year"], how="left")
    )
    marina["eur_per_berth"] = marina["revenue_thousand_eur"] * 1000 / marina["berths"]
    marina["seasonal_share_pct"] = marina["seasonal_staff"] / marina["staff"] * 100
    marina_last = marina[marina["year"] == marina["year"].max()].sort_values(
        "eur_per_berth", ascending=False
    )

    # ------------------------------------------------------- residents spending abroad
    resident = read_dzs(RESIDENT_DIR / "T11.csv").rename(
        columns={"Izdaci": "metric", "Godina": "year", "Tip putovanja": "trip_type",
                 "Destinacija": "destination"}
    )
    resident["year"] = parse_year(resident["year"])
    spend = resident[
        (resident["metric"] == "Izdaci - Ukupno (euro)")
        & (resident["trip_type"] == "Višednevna putovanja")
        & (resident["destination"].isin(["Hrvatska", "Inozemstvo"]))
    ].pivot_table(index="year", columns="destination", values="value", aggfunc="sum").dropna()
    spend["abroad_share_pct"] = spend["Inozemstvo"] / (spend["Inozemstvo"] + spend["Hrvatska"]) * 100
    spend = spend.reset_index()

    # ------------------------------------------------------------------- go / no go
    critical = {"dzs_national_vs_county", "dzs_national_vs_municipality_table",
                "revenue_coverage", "macro_anchor_eur_per_night", "municipality_match_rate",
                "concentration_matches_eiz", "hnb_gap_sane",
                "platform_nights_within_segment",
                "subtypes_sum_to_552", "rooms_dominate_552"}
    failed = [c["rule"] for c in checks if not c["passed"] and c["rule"] in critical]
    go = not failed
    checks.append({
        "rule": "go_no_go",
        "passed": go,
        "detail": "all critical checks passed" if go else f"failed: {', '.join(failed)}",
    })

    # ------------------------------------------------------------------------ write
    print("\nwriting outputs ...")
    out = {
        "tourism_eur_per_night_national.csv": per_night,
        "tourism_eur_per_night_by_county.csv": county_value[[
            "county_id", "label", "is_coastal", "nights", "n_firms", "revenue",
            "employees", "eur_per_night",
        ]],
        "tourism_value_by_model.csv": model_value[[
            "nkd_group", "label", "nights", "beds", "n_firms", "revenue", "employees",
            "eur_per_night", "eur_per_bed", "nights_per_bed", "nights_share_pct",
            "revenue_share_pct",
        ]],
        "tourism_accommodation_subtypes.csv": subtypes,
        "tourism_eur_per_night_by_municipality.csv": ranked[[
            "county", "place", "nights", "beds", "population", "n_firms",
            "revenue", "employees", "eur_per_night", "revenue_per_bed", "beds_per_firm",
        ]],
        "tourism_beds_vs_firms.csv": beds[[
            "county", "place", "nights", "beds", "population", "n_firms", "revenue",
            "beds_per_firm",
        ]],
        "tourism_seasonality_national.csv": season_share.reset_index(),
        "tourism_seasonality_by_county.csv": cty_season,
        "tourism_hnb_gap.csv": gap,
        "tourism_type_share_panel.csv": type_panel,
        "tourism_platform_nights.csv": platforms,
        "tourism_stay_length.csv": stay_wide.reset_index(),
        "tourism_firm_concentration.csv": pd.DataFrame([
            {"scope": "55.1 hoteli", "n_firms": len(hotels),
             "revenue": float(hotels["revenue"].sum()), "top10_share_pct": top10_hotels_pct,
             "top10_revenue": top10_hotels_revenue},
            {"scope": "55 ukupno", "n_firms": len(all_55),
             "revenue": float(all_55["revenue"].sum()), "top10_share_pct": top10_all_pct,
             "top10_revenue": float(all_55["revenue"].head(10).sum())},
        ]),
        "tourism_domestic_share.csv": dom,
        "tourism_resident_spend.csv": spend,
        "tourism_marina_per_berth.csv": marina_last,
        "tourism_marina_panel.csv": marina,
        "tourism_model_split.csv": models,
        "tourism_validation.csv": pd.DataFrame(checks),
    }
    for name, frame in out.items():
        frame.to_csv(TABLE_DIR / name, index=False, encoding="utf-8-sig")
        print(f"   {name}  ({len(frame)} rows)")

    # ------------------------------------------------------------------------ facts
    last = per_night[per_night["year"] == LAST_YEAR].iloc[0]
    first = per_night[per_night["year"] == FIRST_YEAR].iloc[0]
    top = ranked.iloc[0]
    bottom = ranked.iloc[-1]

    facts = {
        "last_year": LAST_YEAR,
        "first_year": FIRST_YEAR,
        "muni_year": MUNI_YEAR,
        "nights_last_year": float(last["nights"]),
        "arrivals_last_year": float(last["arrivals"]),
        "revenue_accommodation_last_year": float(last["revenue_accommodation"]),
        "revenue_food_last_year": float(last["revenue_food"]),
        "eur_per_night_last": float(last["eur_per_night"]),
        "eur_per_night_first": float(first["eur_per_night"]),
        "eur_per_night_with_food_last": float(last["eur_per_night_with_food"]),
        "eur_per_night_real_base_year": base_year,
        "eur_per_night_real_first": float(first["eur_per_night_real"]),
        "eur_per_night_real_base": float(
            per_night.loc[per_night["year"] == base_year, "eur_per_night_real"].iloc[0]
        ),
        "firms_accommodation_last_year": int(last["firms_accommodation"]),
        "muni_ranked_count": int(len(ranked)),
        "muni_top_name": str(top["place"]),
        "muni_top_eur_per_night": float(top["eur_per_night"]),
        "muni_bottom_name": str(bottom["place"]),
        "muni_bottom_eur_per_night": float(bottom["eur_per_night"]),
        "muni_ratio_top_bottom": float(top["eur_per_night"] / bottom["eur_per_night"]),
        "muni_median_eur_per_night": float(ranked["eur_per_night"].median()),

        # county, the headline geography
        "county_top_label": str(coastal.iloc[0]["label"]),
        "county_top_eur_per_night": float(coastal.iloc[0]["eur_per_night"]),
        "county_bottom_label": str(coastal.iloc[-1]["label"]),
        "county_bottom_eur_per_night": float(coastal.iloc[-1]["eur_per_night"]),
        "county_coastal_ratio": float(
            coastal.iloc[0]["eur_per_night"] / coastal.iloc[-1]["eur_per_night"]
        ),
        "zagreb_eur_per_night": float(
            county_value.loc[county_value["county_id"] == 21, "eur_per_night"].iloc[0]
        ),
        "zagreb_to_coastal_top_ratio": float(
            county_value.loc[county_value["county_id"] == 21, "eur_per_night"].iloc[0]
            / coastal.iloc[0]["eur_per_night"]
        ),

        # magnitudes for the arrows. House style puts the change in parentheses next to
        # every arrow, so the growth rates belong in the facts, not typed into prose.
        "eur_per_night_growth_pct": float(
            (last["eur_per_night"] / first["eur_per_night"] - 1) * 100
        ),
        "eur_per_night_real_growth_pct": float(
            (per_night.loc[per_night["year"] == base_year, "eur_per_night_real"].iloc[0]
             / first["eur_per_night_real"] - 1) * 100
        ),
        "peak_share_change_pp": float(
            peak_share.loc[LAST_YEAR] - peak_share.loc[FIRST_YEAR]
        ),
        "marina_top_bottom_ratio": float(
            marina_last[marina_last["place"] != "Republika Hrvatska"].iloc[0]["eur_per_berth"]
            / marina_last[marina_last["place"] != "Republika Hrvatska"].iloc[-1]["eur_per_berth"]
        ),

        # scene-setting counts, so even the hook's numbers trace to a file
        "dzs_table_count": int(dzs_tables),
        "dzs_file_count": int(dzs_files),
        "accommodation_types_coverage_pct": float(rel_types_cov),
        "municipality_gap_pct": float(rel_leaf * 100),
        "domestic_share_2024": float(
            dom.loc[dom["year"] == LAST_YEAR, "domestic_share_pct"].iloc[0]
        ),
        **{k: float(v) for k, v in seat_stats.items()},

        # accommodation models.
        # 55.2 is withheld from the money-per-unit keys on purpose. Its revenue belongs to
        # 1.691 companies and its nights belong overwhelmingly to households that file no
        # accounts, and DZS publishes no operator split, so revenue per night and revenue per
        # bed there measure nothing. Counts, shares and utilisation are fine, because each of
        # those is computed inside one population. The diagnostic value stays in
        # tourism_value_by_model.csv for the validation gate above.
        **{
            f"model_{row.nkd_group}_{key}": float(getattr(row, key))
            for row in model_value.itertuples()
            for key in ("nights", "beds", "revenue", "eur_per_night", "eur_per_bed",
                        "nights_share_pct", "revenue_share_pct", "employees", "n_firms")
            if not (row.nkd_group == 552 and key in ("eur_per_night", "eur_per_bed"))
        },

        # what group 55.2 holds, one level down. Names the denominator without pretending
        # to know who owns it.
        "subtype_rooms_nights": rooms_nights,
        "subtype_rooms_beds": rooms_beds,
        "subtype_rooms_share_of_552_pct": rooms_nights / nights_552 * 100,
        "subtype_rooms_share_of_national_pct": rooms_nights / type_total * 100,
        "subtype_hostels_nights": hostel_nights,
        # the one real price series, hotels only, populations identical
        "hotel_price_first_year": int(hp_first["year"]),
        "hotel_eur_per_night_first": float(hp_first["eur_per_night"]),
        "hotel_eur_per_night_last": float(hp_last["eur_per_night"]),
        "hotel_price_growth_pct": float(
            hp_last["eur_per_night"] / hp_first["eur_per_night"] * 100 - 100
        ),

        # the honest pair. capture rate against a price measured where populations match
        "eur_per_night_matched_segments": eur_per_night_matched,
        "matched_segments_nights": float(matched_segments["nights"].sum()),
        "eur_per_night_matched_to_headline_ratio": eur_per_night_matched / anchor,

        # utilisation, computed from DZS alone. No company accounts anywhere near it, so it
        # carries the same finding with none of the population problem.
        **{
            f"nights_per_bed_{int(row.nkd_group)}": float(row.nights_per_bed)
            for row in model_value.itertuples()
        },
        "hotel_to_apartment_bed_use_ratio": float(
            model_value.loc[model_value["nkd_group"] == 551, "nights_per_bed"].iloc[0]
            / model_value.loc[model_value["nkd_group"] == 552, "nights_per_bed"].iloc[0]
        ),

        # no hotel-to-apartment revenue-per-night ratio here either. It would be the same
        # meaningless quotient with a multiplication sign in front of it.
        "model_apartment_nights_share": float(
            model_value.loc[model_value["nkd_group"] == 552, "nights_share_pct"].iloc[0]
        ),
        "model_apartment_revenue_share": float(
            model_value.loc[model_value["nkd_group"] == 552, "revenue_share_pct"].iloc[0]
        ),
        "national_beds": national_beds,
        "national_accommodation_firms": national_firms,
        "beds_per_firm_national": national_beds / national_firms,
        "peak_share_last": float(peak_share.loc[LAST_YEAR]),
        "peak_share_first": float(peak_share.loc[FIRST_YEAR]),
        "peak_share_max_county": str(cty_season.iloc[0]["county"]),
        "peak_share_max_value": float(cty_season.iloc[0]["peak_share_pct"]),
        "domestic_share_2005": float(dom.loc[dom["year"] == 2005, "domestic_share_pct"].iloc[0]),
        "domestic_share_last": float(dom["domestic_share_pct"].iloc[-1]),
        "domestic_share_last_year": int(dom["year"].iloc[-1]),
        "marina_year": int(marina_last["year"].iloc[0]),
        "marina_national_eur_per_berth": float(
            marina_last.loc[marina_last["place"] == "Republika Hrvatska", "eur_per_berth"].iloc[0]
        ),
        "marina_national_berths": float(
            marina_last.loc[marina_last["place"] == "Republika Hrvatska", "berths"].iloc[0]
        ),
        "marina_seasonal_share": float(
            marina_last.loc[marina_last["place"] == "Republika Hrvatska", "seasonal_share_pct"].iloc[0]
        ),
        # what the country takes against what the accommodation firm takes
        "hnb_receipts_last": float(gap_last["hnb_receipts"]),
        "foreign_nights_last": float(gap_last["foreign_nights"]),
        "eur_per_foreign_night": float(gap_last["eur_per_foreign_night"]),
        "accommodation_per_foreign_night": float(gap_last["accommodation_per_foreign_night"]),
        "accommodation_share_of_receipts_pct": float(gap_last["accommodation_share_pct"]),
        "food_per_foreign_night": float(gap_last["food_per_foreign_night"]),
        "rest_per_foreign_night": float(gap_last["rest_per_foreign_night"]),
        "accommodation_share_of_receipts_2019_pct": float(
            gap.loc[gap["year"] == 2019, "accommodation_share_pct"].iloc[0]
        ),
        "eur_per_foreign_night_2019": float(
            gap.loc[gap["year"] == 2019, "eur_per_foreign_night"].iloc[0]
        ),
        "hnb_receipts_growth_pct": float(
            gap.loc[gap["year"] == LAST_YEAR, "hnb_receipts"].iloc[0]
            / gap.loc[gap["year"] == 2019, "hnb_receipts"].iloc[0] * 100 - 100
        ),
        "arrivals_growth_pct": float(
            per_night.loc[per_night["year"] == LAST_YEAR, "arrivals"].iloc[0]
            / per_night.loc[per_night["year"] == FIRST_YEAR, "arrivals"].iloc[0] * 100 - 100
        ),
        "nights_growth_pct": float(
            per_night.loc[per_night["year"] == LAST_YEAR, "nights"].iloc[0]
            / per_night.loc[per_night["year"] == FIRST_YEAR, "nights"].iloc[0] * 100 - 100
        ),
        "resident_spend_year": int(spend["year"].iloc[-1]),

        # the stay is getting shorter while the headline count grows
        "nights_per_arrival_last": float(stay_wide.loc[LAST_YEAR, "ukupno"]),
        "nights_per_arrival_first": float(stay_wide.loc[FIRST_YEAR, "ukupno"]),
        "nights_per_arrival_foreign_last": float(stay_wide.loc[LAST_YEAR, "strani"]),
        "nights_per_arrival_foreign_first": float(stay_wide.loc[FIRST_YEAR, "strani"]),
        "eur_per_arrival_last": float(
            per_night.loc[per_night["year"] == LAST_YEAR, "eur_per_arrival"].iloc[0]
        ),
        "eur_per_arrival_first": float(
            per_night.loc[per_night["year"] == FIRST_YEAR, "eur_per_arrival"].iloc[0]
        ),
        "arrivals_first_year": float(
            per_night.loc[per_night["year"] == FIRST_YEAR, "arrivals"].iloc[0]
        ),
        "nights_first_year": float(
            per_night.loc[per_night["year"] == FIRST_YEAR, "nights"].iloc[0]
        ),

        # the mix, moving
        "mix_last_year": mix_last_year,
        "mix_first_year": mix_first_year,
        "hotel_share_now": hotel_share_now,
        "hotel_share_2021": hotel_share_2021,
        "hotel_share_prepandemic": hotel_share_prepandemic,
        "hotel_share_pp_change": hotel_share_now - hotel_share_2021,
        "hotel_share_pp_vs_prepandemic": hotel_share_now - hotel_share_prepandemic,
        "apartment_share_now": float(mix_total.loc[mix_last_year, "share_sobe"]),
        "apartment_share_2021": float(mix_total.loc[2021, "share_sobe"]),
        "apartment_share_prepandemic": float(mix_total.loc[mix_first_year, "share_sobe"]),

        # concentration
        "top10_hotels_share_pct": top10_hotels_pct,
        "top10_all_share_pct": top10_all_pct,
        "top10_hotels_revenue": top10_hotels_revenue,
        "eiz_top10_share_pct": eiz_share,
        "eiz_implied_total_revenue": float(eiz_implied_total),
        "hotels_revenue_last": float(hotels["revenue"].sum()),
        "hotels_n_firms_last": int(len(hotels)),

        # the household layer as the platforms see it
        "platform_nights_last": float(platform_last["platform_nights_total"]),
        "platform_share_of_apartments_pct": float(platform_share_of_apartments),
        "platform_nights_first": float(
            platforms.loc[platforms["year"] == platforms["year"].min(), "platform_nights_total"].iloc[0]
        ),
        "platform_first_year": int(platforms["year"].min()),

        # wages, the human side of a forty euro night
        "wage_net_economy": external("wage_net_economy", LAST_YEAR),
        "wage_net_accommodation": external("wage_net_accommodation", LAST_YEAR),
        "wage_net_food": external("wage_net_food", LAST_YEAR),
        "wage_accommodation_gap_pct": (
            1 - external("wage_net_accommodation", LAST_YEAR)
            / external("wage_net_economy", LAST_YEAR)
        ) * 100,
        "wage_food_gap_pct": (
            1 - external("wage_net_food", LAST_YEAR)
            / external("wage_net_economy", LAST_YEAR)
        ) * 100,

        # domestic nights are a flat share of a growing total, not a flat number
        "domestic_nights_last": float(
            dom.loc[dom["year"] == LAST_YEAR, "domaći"].iloc[0]
        ),
        "domestic_nights_first": float(
            dom.loc[dom["year"] == FIRST_YEAR, "domaći"].iloc[0]
        ),
        "domestic_nights_growth_pct": float(
            dom.loc[dom["year"] == LAST_YEAR, "domaći"].iloc[0]
            / dom.loc[dom["year"] == FIRST_YEAR, "domaći"].iloc[0] * 100 - 100
        ),

        "resident_abroad_share_last": float(spend["abroad_share_pct"].iloc[-1]),
        "resident_abroad_share_first": float(spend["abroad_share_pct"].iloc[0]),
        "resident_spend_home_last": float(spend["Hrvatska"].iloc[-1]),
        "resident_spend_abroad_last": float(spend["Inozemstvo"].iloc[-1]),

        # a berth against a bed. The average bed is dominated by apartment beds, so state
        # both comparisons; a hotel bed alone out-earns a berth.
        "beds_total": float(model_value["beds"].sum()),
        "revenue_per_bed_all": float(
            model_value["revenue"].sum() / model_value["beds"].sum()
        ),
        "berth_to_average_bed_ratio": float(
            marina_last.loc[marina_last["place"] == "Republika Hrvatska", "eur_per_berth"].iloc[0]
            / (model_value["revenue"].sum() / model_value["beds"].sum())
        ),
        "marina_top_label": str(
            marina_last[marina_last["place"] != "Republika Hrvatska"].iloc[0]["place"]
        ).replace(" županija", ""),
        "marina_top_eur_per_berth": float(
            marina_last[marina_last["place"] != "Republika Hrvatska"].iloc[0]["eur_per_berth"]
        ),
        "marina_bottom_label": str(
            marina_last[marina_last["place"] != "Republika Hrvatska"].iloc[-1]["place"]
        ).replace(" županija", ""),
        "marina_bottom_eur_per_berth": float(
            marina_last[marina_last["place"] != "Republika Hrvatska"].iloc[-1]["eur_per_berth"]
        ),
        "validation_passed": go,
    }
    (FACT_DIR / "tourism_value.json").write_text(
        json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"   outputs/facts/tourism_value.json ({len(facts)} keys)")

    print("\n" + "=" * 78)
    print(f"GO / NO GO: {'PASSED' if go else 'FAILED — ' + ', '.join(failed)}")
    print("=" * 78)
    print(f"\n  {LAST_YEAR}. jedna noć = {facts['eur_per_night_last']:.1f} EUR "
          f"(smještaj) / {facts['eur_per_night_with_food_last']:.1f} EUR (+ ugostiteljstvo)")
    print("\n  po modelu smještaja:")
    for row in model_value.itertuples():
        # 552 prints its quotient in brackets. It is a diagnostic here and nowhere else.
        rate = (f"({row.eur_per_night:6.1f})" if row.nkd_group == 552
                else f"{row.eur_per_night:7.1f} ")
        print(f"    {row.label:18s} {row.nights_share_pct:5.1f}% noćenja   "
              f"{row.revenue_share_pct:5.1f}% prihoda   {rate} EUR/noć   "
              f"{row.revenue/1e6:8.1f} M EUR")
    print(f"\n  u skupini 55.2: sobe, apartmani i kuće za odmor "
          f"{rooms_nights/1e6:.1f} mil. noćenja "
          f"({facts['subtype_rooms_share_of_national_pct']:.1f}% državnih), "
          f"{rooms_beds:,.0f} postelja. hosteli {hostel_nights/1e3:.0f} tis. noćenja. "
          f"DZS ne dijeli noćenja po tome vodi li objekt firma ili kućanstvo.")
    print(f"\n  obala: {facts['county_top_label']} {facts['county_top_eur_per_night']:.1f} -> "
          f"{facts['county_bottom_label']} {facts['county_bottom_eur_per_night']:.1f} EUR "
          f"({facts['county_coastal_ratio']:.1f}x). Zagreb {facts['zagreb_eur_per_night']:.0f}")
    print(f"\n  strano noćenje. zemlja {facts['eur_per_foreign_night']:.0f} EUR, "
          f"smještaj najviše {facts['accommodation_per_foreign_night']:.0f} EUR "
          f"({facts['accommodation_share_of_receipts_pct']:.0f}% deviznih prihoda, "
          f"2019. {facts['accommodation_share_of_receipts_2019_pct']:.0f}%)")
    print(f"  noćenja po dolasku {facts['nights_per_arrival_first']:.2f} -> "
          f"{facts['nights_per_arrival_last']:.2f}")
    print(f"  udio hotela u noćenjima {facts['hotel_share_2021']:.1f}% (2021.) -> "
          f"{facts['hotel_share_now']:.1f}% ({facts['mix_last_year']}.)")
    print(f"  koncentracija. top 10 = {facts['top10_hotels_share_pct']:.1f}% hotelskog "
          f"prihoda (EIZ objavljuje {facts['eiz_top10_share_pct']:.1f}%)")
    print(f"  platforme. {facts['platform_nights_last']/1e6:.1f} mil. od "
          f"{facts['model_552_nights']/1e6:.1f} mil. noćenja u 55.2 "
          f"({facts['platform_share_of_apartments_pct']:.0f}%)")
    print(f"  srpanj+kolovoz = {facts['peak_share_last']:.1f}% godine")
    print(f"  domaći gosti: {facts['domestic_share_2005']:.1f}% (2005.) -> "
          f"{facts['domestic_share_last']:.1f}% ({facts['domestic_share_last_year']}.)")
    print(f"  vez: {facts['marina_national_eur_per_berth']:,.0f} EUR/god")


if __name__ == "__main__":
    main()
