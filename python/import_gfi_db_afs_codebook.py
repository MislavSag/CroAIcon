"""Import the physical db_afs codebook from the local FINA workbook.

This table is intentionally separate from `codes_gfi`: in this database,
`codes_gfi` does not match the physical `db_afs.bNNN` column layout for the
balance-sheet and P&L positions used by analysis scripts.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import pymysql


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = Path(
    os.environ.get(
        "GFI_DB_AFS_CODEBOOK_XLSX",
        r"D:\data\poslovni_subjekti\sifrarnik\sifrarnici\financije_sifrarnik.xlsx",
    )
)
SOURCE_SHEET = "cb_afs"
TARGET_TABLE = "codes_gfi_db_afs_physical"


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
        read_timeout=120,
        charset="utf8mb4",
        autocommit=False,
    )


def build_codebook() -> pd.DataFrame:
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(SOURCE_FILE)

    df = pd.read_excel(SOURCE_FILE, sheet_name=SOURCE_SHEET)
    df = df.rename(
        columns={
            "ReportType": "report_type",
            "ReportLabel": "report_label",
            "PositionID": "position_id",
            "PositionLabel": "position_label",
            "PositionLabelLanguage": "position_label_language",
            "PositionLevel": "position_level",
        }
    )

    required = [
        "report_type",
        "report_label",
        "position_id",
        "position_label",
        "position_label_language",
        "position_level",
    ]
    missing = set(required).difference(df.columns)
    if missing:
        raise RuntimeError(f"Missing workbook columns: {', '.join(sorted(missing))}")

    df = df[required].copy()
    df["position_id"] = df["position_id"].astype(str).str.strip()
    df["aop_number"] = df["position_id"].str.extract(r"^(\d{3})B$", expand=False).astype(int)
    df["db_column"] = df["aop_number"].map(lambda value: f"b{value:03d}")
    df["source_file"] = str(SOURCE_FILE).replace("\\", "/")
    df["source_sheet"] = SOURCE_SHEET

    duplicated = df.duplicated(["report_type", "position_id", "position_label_language"]).sum()
    if duplicated:
        raise RuntimeError(f"Duplicate codebook keys found: {duplicated}")

    bad_position_id = df.loc[~df["position_id"].str.match(r"^\d{3}B$"), "position_id"].tolist()
    if bad_position_id:
        raise RuntimeError(f"Unexpected PositionID values: {bad_position_id[:5]}")

    return df.sort_values(["report_type", "aop_number"])


def create_table(conn: pymysql.connections.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {TARGET_TABLE} (
                report_type INT NOT NULL,
                report_label VARCHAR(128) NOT NULL,
                position_id VARCHAR(8) NOT NULL,
                aop_number INT NOT NULL,
                db_column VARCHAR(8) NOT NULL,
                position_label TEXT NOT NULL,
                position_label_language VARCHAR(8) NOT NULL,
                position_level INT NOT NULL,
                source_file VARCHAR(512) NOT NULL,
                source_sheet VARCHAR(64) NOT NULL,
                imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (report_type, position_id, position_label_language),
                KEY idx_codes_gfi_db_afs_physical_db_column (db_column),
                KEY idx_codes_gfi_db_afs_physical_aop (aop_number)
            )
            CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
            COMMENT='Physical codebook for db_afs.bNNN columns imported from financije_sifrarnik.xlsx; do not substitute codes_gfi for db_afs physical mapping.'
            """
        )


def import_rows(conn: pymysql.connections.Connection, codebook: pd.DataFrame) -> None:
    cols = [
        "report_type",
        "report_label",
        "position_id",
        "aop_number",
        "db_column",
        "position_label",
        "position_label_language",
        "position_level",
        "source_file",
        "source_sheet",
    ]
    rows = [tuple(row) for row in codebook[cols].itertuples(index=False, name=None)]

    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {TARGET_TABLE}")
        cur.executemany(
            f"""
            INSERT INTO {TARGET_TABLE}
                ({", ".join(cols)})
            VALUES
                ({", ".join(["%s"] * len(cols))})
            """,
            rows,
        )
    conn.commit()


def main() -> None:
    codebook = build_codebook()
    conn = connect()
    try:
        create_table(conn)
        import_rows(conn, codebook)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print(f"Imported {len(codebook):,} rows into {TARGET_TABLE}")
    print(f"Source: {SOURCE_FILE} [{SOURCE_SHEET}]")


if __name__ == "__main__":
    main()
