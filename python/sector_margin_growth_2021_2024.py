"""Quick diagnostic: sector net-margin growth from 2021 to 2024.

This uses the physical db_afs mapping pattern from the debt-structure work:
operating revenue is b110 and net result is b152 - b153.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import pymysql


YEARS = (2021, 2024)
MIN_REVENUE_2024_SECTION = 1_000_000_000
MIN_REVENUE_2024_DETAIL = 500_000_000
EXCLUDED_SECTORS = {"K"}

DETAIL_LEVELS = {
    "nkd2": {
        "column": "nacerev22",
        "digits": 2,
        "razina": 2,
        "label": "NKD razina 2",
        "min_revenue_2024": MIN_REVENUE_2024_DETAIL,
    },
    "nkd3": {
        "column": "nacerev23",
        "digits": 3,
        "razina": 3,
        "label": "NKD razina 3",
        "min_revenue_2024": MIN_REVENUE_2024_DETAIL,
    },
    "nkd4": {
        "column": "nacerev24",
        "digits": 4,
        "razina": 4,
        "label": "NKD razina 4",
        "min_revenue_2024": MIN_REVENUE_2024_DETAIL,
    },
}

SECTOR_NAMES = {
    "A": "Poljoprivreda",
    "B": "Rudarstvo",
    "C": "Preradjivacka industrija",
    "D": "Energetika",
    "E": "Vodoopskrba",
    "F": "Gradjevinarstvo",
    "G": "Trgovina",
    "H": "Prijevoz i skladistenje",
    "I": "Smjestaj i ugostiteljstvo",
    "J": "Informacije i komunikacije",
    "K": "Financije i osiguranje",
    "L": "Nekretnine",
    "M": "Strucne djelatnosti",
    "N": "Administrativne usluge",
    "O": "Javna uprava",
    "P": "Obrazovanje",
    "Q": "Zdravstvo",
    "R": "Umjetnost i rekreacija",
    "S": "Ostale usluzne djelatnosti",
}

CODEBOOK_COLUMNS = ("b110", "b152", "b153")


def project_root() -> Path:
    path = Path.cwd().resolve()
    for candidate in [path, *path.parents]:
        if (candidate / "_quarto.yml").exists() and (candidate / "CroAIcon.Rproj").exists():
            return candidate
    raise RuntimeError("Cannot locate CroAIcon project root.")


ROOT = project_root()
TABLE_DIR = ROOT / "outputs" / "tables"


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
    load_env_file(ROOT / ".env")
    load_env_file(ROOT / ".Renviron")

    required = [
        "GFI_DB_HOST",
        "GFI_DB_PORT",
        "GFI_DB_USER",
        "GFI_DB_PASSWORD",
        "GFI_DB_NAME",
    ]
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
        charset="utf8mb4",
    )


def query_codebook(conn: pymysql.connections.Connection) -> pd.DataFrame:
    placeholders = ", ".join(["%s"] * len(CODEBOOK_COLUMNS))
    sql = f"""
        SELECT
            db_column,
            aop_number,
            report_label,
            position_label,
            source_file
        FROM codes_gfi_db_afs_physical
        WHERE db_column IN ({placeholders})
        ORDER BY db_column
    """
    return pd.read_sql(sql, conn, params=list(CODEBOOK_COLUMNS))


def query_sector_margins(conn: pymysql.connections.Connection) -> pd.DataFrame:
    year_placeholders = ", ".join(["%s"] * len(YEARS))
    sql = f"""
        SELECT
            reportyear AS year,
            nacerev21 AS sector,
            COUNT(*) AS n_firms,
            SUM(COALESCE(b110, 0)) AS revenue,
            SUM(COALESCE(b152, 0) - COALESCE(b153, 0)) AS net_result
        FROM db_afs
        WHERE reportyear IN ({year_placeholders})
          AND nacerev21 REGEXP '^[A-U]$'
        GROUP BY reportyear, nacerev21
    """
    df = pd.read_sql(sql, conn, params=list(YEARS))
    for col in ["n_firms", "revenue", "net_result"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def query_nkd_detail_margins(conn: pymysql.connections.Connection, level_key: str) -> pd.DataFrame:
    level = DETAIL_LEVELS[level_key]
    year_placeholders = ", ".join(["%s"] * len(YEARS))
    column = level["column"]
    digits = level["digits"]
    sql = f"""
        SELECT
            d.reportyear AS year,
            d.nacerev21 AS sector,
            LPAD(d.{column}, {digits}, '0') AS nkd_code,
            c.OPIS_DJEL AS nkd_name,
            COUNT(*) AS n_firms,
            SUM(COALESCE(d.b110, 0)) AS revenue,
            SUM(COALESCE(d.b152, 0) - COALESCE(d.b153, 0)) AS net_result
        FROM db_afs d
        LEFT JOIN codes_nkd2007 c
          ON c.RAZINA = %s
         AND c.SIFRA = LPAD(d.{column}, {digits}, '0')
        WHERE d.reportyear IN ({year_placeholders})
          AND d.nacerev21 REGEXP '^[A-U]$'
          AND d.{column} IS NOT NULL
        GROUP BY d.reportyear, d.nacerev21, nkd_code, c.OPIS_DJEL
    """
    df = pd.read_sql(sql, conn, params=[level["razina"], *YEARS])
    for col in ["n_firms", "revenue", "net_result"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["level"] = level_key
    df["level_label"] = level["label"]
    return df


def build_change_table(df: pd.DataFrame, min_revenue_2024: float) -> pd.DataFrame:
    df = df.copy()
    df["sector_name"] = df["sector"].map(SECTOR_NAMES).fillna(df["sector"])
    df["net_margin"] = df["net_result"] / df["revenue"].where(df["revenue"] > 0)

    wide = df.pivot(index=["sector", "sector_name"], columns="year")
    out = pd.DataFrame(index=wide.index).reset_index()
    for col in ["n_firms", "revenue", "net_result", "net_margin"]:
        for year in YEARS:
            out[f"{col}_{year}"] = wide[(col, year)].values

    out["margin_change_pp"] = 100 * (out["net_margin_2024"] - out["net_margin_2021"])
    out["revenue_growth_pct"] = 100 * (out["revenue_2024"] / out["revenue_2021"] - 1)
    out["included_main"] = (
        ~out["sector"].isin(EXCLUDED_SECTORS)
        & (out["revenue_2024"] >= min_revenue_2024)
        & out["net_margin_2021"].notna()
        & out["net_margin_2024"].notna()
    )
    return out.sort_values("margin_change_pp", ascending=False)


def build_nkd_change_table(df: pd.DataFrame, level_key: str) -> pd.DataFrame:
    df = df.copy()
    level = DETAIL_LEVELS[level_key]
    df["sector_name"] = df["sector"].map(SECTOR_NAMES).fillna(df["sector"])
    df["nkd_name"] = df["nkd_name"].fillna(df["nkd_code"])
    df["net_margin"] = df["net_result"] / df["revenue"].where(df["revenue"] > 0)

    wide = df.pivot(index=["level", "level_label", "sector", "sector_name", "nkd_code", "nkd_name"], columns="year")
    out = pd.DataFrame(index=wide.index).reset_index()
    for col in ["n_firms", "revenue", "net_result", "net_margin"]:
        for year in YEARS:
            out[f"{col}_{year}"] = wide[(col, year)].values

    out["margin_change_pp"] = 100 * (out["net_margin_2024"] - out["net_margin_2021"])
    out["revenue_growth_pct"] = 100 * (out["revenue_2024"] / out["revenue_2021"] - 1)
    out["included_chart"] = (
        ~out["sector"].isin(EXCLUDED_SECTORS)
        & (out["revenue_2024"] >= level["min_revenue_2024"])
        & out["net_margin_2021"].notna()
        & out["net_margin_2024"].notna()
    )
    return out.sort_values("margin_change_pp", ascending=False)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        codebook = query_codebook(conn)
        raw = query_sector_margins(conn)
        detail_raw = {
            level_key: query_nkd_detail_margins(conn, level_key)
            for level_key in DETAIL_LEVELS
        }

    changes = build_change_table(raw, MIN_REVENUE_2024_SECTION)
    codebook.to_csv(TABLE_DIR / "sector_margin_growth_codebook_audit.csv", index=False, encoding="utf-8-sig")
    raw.to_csv(TABLE_DIR / "sector_margin_growth_raw_2021_2024.csv", index=False, encoding="utf-8-sig")
    changes.to_csv(TABLE_DIR / "sector_margin_growth_2021_2024.csv", index=False, encoding="utf-8-sig")

    detail_changes = {}
    for level_key, raw_detail in detail_raw.items():
        changes_detail = build_nkd_change_table(raw_detail, level_key)
        detail_changes[level_key] = changes_detail
        raw_detail.to_csv(
            TABLE_DIR / f"sector_margin_growth_{level_key}_raw_2021_2024.csv",
            index=False,
            encoding="utf-8-sig",
        )
        changes_detail.to_csv(
            TABLE_DIR / f"sector_margin_growth_{level_key}_2021_2024.csv",
            index=False,
            encoding="utf-8-sig",
        )

    cols = [
        "sector",
        "sector_name",
        "n_firms_2024",
        "revenue_2024",
        "net_margin_2021",
        "net_margin_2024",
        "margin_change_pp",
    ]
    top = changes[changes["included_main"]].sort_values("margin_change_pp", ascending=False).head(10)
    pd.set_option("display.width", 180)
    pd.set_option("display.max_columns", 20)
    print("=== Codebook rows used ===")
    print(codebook.to_string(index=False))
    print("\n=== Top sector net-margin increases, 2021 to 2024 ===")
    print(top[cols].to_string(index=False, formatters={
        "revenue_2024": lambda x: f"{x:,.0f}",
        "net_margin_2021": lambda x: f"{100*x:.2f}%",
        "net_margin_2024": lambda x: f"{100*x:.2f}%",
        "margin_change_pp": lambda x: f"{x:+.2f}",
    }))
    for level_key, detail in detail_changes.items():
        top_detail = detail[detail["included_chart"]].sort_values("margin_change_pp", ascending=False).head(8)
        print(f"\n=== Top {level_key} net-margin increases, 2021 to 2024 ===")
        print(top_detail[[
            "nkd_code",
            "nkd_name",
            "revenue_2024",
            "net_margin_2021",
            "net_margin_2024",
            "margin_change_pp",
        ]].to_string(index=False, formatters={
            "revenue_2024": lambda x: f"{x:,.0f}",
            "net_margin_2021": lambda x: f"{100*x:.2f}%",
            "net_margin_2024": lambda x: f"{100*x:.2f}%",
            "margin_change_pp": lambda x: f"{x:+.2f}",
        }))

    print("\nSaved sector and detailed NKD margin-growth tables in outputs/tables")


if __name__ == "__main__":
    main()
