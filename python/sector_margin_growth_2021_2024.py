"""Quick diagnostic: sector net-margin growth from 2021 to 2024.

This uses the newer physical db_afs mapping pattern from the debt-structure
work: operating revenue is b110 and net result is b152 - b153. It also computes
the older Zagreb-profit definition as a cross-check, but the primary ranking is
the physical-codebook definition.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import pymysql


YEARS = (2021, 2024)
MIN_REVENUE_2024 = 1_000_000_000
EXCLUDED_SECTORS = {"K"}

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

CODEBOOK_COLUMNS = ("b110", "b125", "b152", "b153", "b184", "b185", "b197", "b198")


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
            SUM(COALESCE(b152, 0) - COALESCE(b153, 0)) AS net_result,
            SUM(COALESCE(b125, 0)) AS revenue_alt,
            SUM(
                COALESCE(NULLIF(b184, 0), NULLIF(b197, 0), 0)
                - COALESCE(NULLIF(b185, 0), NULLIF(b198, 0), 0)
            ) AS net_result_alt
        FROM db_afs
        WHERE reportyear IN ({year_placeholders})
          AND nacerev21 REGEXP '^[A-U]$'
        GROUP BY reportyear, nacerev21
    """
    df = pd.read_sql(sql, conn, params=list(YEARS))
    for col in ["n_firms", "revenue", "net_result", "revenue_alt", "net_result_alt"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def build_change_table(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["sector_name"] = df["sector"].map(SECTOR_NAMES).fillna(df["sector"])
    df["net_margin"] = df["net_result"] / df["revenue"].where(df["revenue"] > 0)
    df["net_margin_alt"] = df["net_result_alt"] / df["revenue_alt"].where(df["revenue_alt"] > 0)

    wide = df.pivot(index=["sector", "sector_name"], columns="year")
    out = pd.DataFrame(index=wide.index).reset_index()
    for col in ["n_firms", "revenue", "net_result", "net_margin", "revenue_alt", "net_result_alt", "net_margin_alt"]:
        for year in YEARS:
            out[f"{col}_{year}"] = wide[(col, year)].values

    out["margin_change_pp"] = 100 * (out["net_margin_2024"] - out["net_margin_2021"])
    out["margin_change_alt_pp"] = 100 * (out["net_margin_alt_2024"] - out["net_margin_alt_2021"])
    out["revenue_growth_pct"] = 100 * (out["revenue_2024"] / out["revenue_2021"] - 1)
    out["included_main"] = (
        ~out["sector"].isin(EXCLUDED_SECTORS)
        & (out["revenue_2024"] >= MIN_REVENUE_2024)
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

    changes = build_change_table(raw)
    codebook.to_csv(TABLE_DIR / "sector_margin_growth_codebook_audit.csv", index=False, encoding="utf-8-sig")
    raw.to_csv(TABLE_DIR / "sector_margin_growth_raw_2021_2024.csv", index=False, encoding="utf-8-sig")
    changes.to_csv(TABLE_DIR / "sector_margin_growth_2021_2024.csv", index=False, encoding="utf-8-sig")

    cols = [
        "sector",
        "sector_name",
        "n_firms_2024",
        "revenue_2024",
        "net_margin_2021",
        "net_margin_2024",
        "margin_change_pp",
        "margin_change_alt_pp",
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
        "margin_change_alt_pp": lambda x: f"{x:+.2f}" if pd.notna(x) else "",
    }))
    print("\nSaved outputs/tables/sector_margin_growth_2021_2024.csv")


if __name__ == "__main__":
    main()
