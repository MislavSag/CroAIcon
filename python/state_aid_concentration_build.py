"""Build aggregate outputs for the Croatian state-aid concentration post.

The script reads the published Croatian State Aid Register snapshot from
`odvjet12_znalac`, keeps only verified positive awards, and writes aggregate
outputs for the 2017 to 2025 observed register universe, the 2021 to 2023
official-total coverage audit, within-type concentration, and 2023 to 2024
recipient recurrence. It never writes recipient names, OIBs, or other
row-level identifiers.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pymysql


START_YEAR = 2017
END_YEAR = 2025
SOURCE_SCHEMA = "odvjet12_znalac"
SOURCE_TABLE = "state_aid_awards"
SOURCE_NAME = "croatian_state_aid_register"

SIZE_ORDER = ["Veliki", "Srednje veliki", "Mali", "Mikro", "Nepoznato"]


def project_root() -> Path:
    path = Path.cwd().resolve()
    for candidate in [path, *path.parents]:
        if (candidate / "_quarto.yml").exists() and (candidate / "CroAIcon.Rproj").exists():
            return candidate
    raise RuntimeError("Cannot locate CroAIcon project root.")


ROOT = project_root()
TABLE_DIR = ROOT / "outputs" / "tables"
FACT_DIR = ROOT / "outputs" / "facts"
OFFICIAL_TOTALS_PATH = (
    ROOT / "data" / "reference" / "mfin_state_aid_official_totals_2021_2023.csv"
)


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def first_env(*keys: str, default: str | None = None) -> str | None:
    for key in keys:
        value = os.environ.get(key)
        if value:
            return value
    return default


def connect() -> pymysql.connections.Connection:
    load_env_file(ROOT / ".env")
    load_env_file(ROOT / ".Renviron")

    host = first_env("ZNALAC_DB_HOST", "GFI_DB_HOST", "MYSQL_HOST")
    port = first_env("ZNALAC_DB_PORT", "GFI_DB_PORT", "MYSQL_PORT", default="3306")
    user = first_env("ZNALAC_DB_USER", "GFI_DB_USER", "MYSQL_USER")
    password = first_env("ZNALAC_DB_PASSWORD", "GFI_DB_PASSWORD", "MYSQL_PASSWORD")
    missing = [
        name
        for name, value in {
            "database host": host,
            "database user": user,
            "database password": password,
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing {', '.join(missing)} in environment or repo env files.")

    return pymysql.connect(
        host=host,
        port=int(port or "3306"),
        user=user,
        password=password,
        charset="utf8mb4",
        connect_timeout=15,
        read_timeout=300,
    )


def ensure_dirs() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FACT_DIR.mkdir(parents=True, exist_ok=True)


def query_frame(
    conn: pymysql.connections.Connection,
    sql: str,
    params: tuple[Any, ...] = (),
) -> pd.DataFrame:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        columns = [item[0] for item in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=columns)


def query_one(
    conn: pymysql.connections.Connection,
    sql: str,
    params: tuple[Any, ...] = (),
) -> dict[str, Any]:
    frame = query_frame(conn, sql, params)
    if len(frame) != 1:
        raise RuntimeError(f"Expected one row, got {len(frame)}.")
    return frame.iloc[0].to_dict()


def published_snapshot(conn: pymysql.connections.Connection) -> dict[str, Any]:
    return query_one(
        conn,
        f"""
        SELECT id AS snapshot_id, total_rows, valid_rows, invalid_rows,
               completed_at, details_json
        FROM {SOURCE_SCHEMA}.source_imports
        WHERE source = %s AND status = 'published'
        ORDER BY id DESC
        LIMIT 1
        """,
        (SOURCE_NAME,),
    )


def base_filter(
    valid_oib: bool = False,
    start_year: int = START_YEAR,
    end_year: int = END_YEAR,
) -> str:
    clauses = [
        "snapshot_id = %s",
        "verification_status = 'Ispravan'",
        "gross_amount_eur > 0",
        f"LEFT(awarded_at, 4) BETWEEN '{start_year}' AND '{end_year}'",
        "awarded_at REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}'",
    ]
    if valid_oib:
        clauses.append("recipient_oib REGEXP '^[0-9]{11}$'")
    return " AND ".join(clauses)


def coverage_output(
    conn: pymysql.connections.Connection,
    snapshot_id: int,
) -> pd.DataFrame:
    registry = query_frame(
        conn,
        f"""
        SELECT CAST(LEFT(awarded_at, 4) AS UNSIGNED) AS year,
               COUNT(*) AS registry_award_count_all,
               SUM(gross_amount_eur) AS registry_amount_all_eur,
               SUM(recipient_oib REGEXP '^[0-9]{{11}}$') AS registry_award_count_valid_oib,
               SUM(CASE WHEN recipient_oib REGEXP '^[0-9]{{11}}$'
                        THEN gross_amount_eur ELSE 0 END) AS registry_amount_valid_oib_eur
        FROM {SOURCE_SCHEMA}.{SOURCE_TABLE}
        WHERE {base_filter(valid_oib=False, start_year=2021, end_year=2023)}
        GROUP BY CAST(LEFT(awarded_at, 4) AS UNSIGNED)
        ORDER BY year
        """,
        (snapshot_id,),
    )
    official = pd.read_csv(OFFICIAL_TOTALS_PATH)
    coverage = official.merge(registry, on="year", how="left", validate="one_to_one")
    amount_columns = [
        "official_total_amount_eur",
        "registry_amount_all_eur",
        "registry_amount_valid_oib_eur",
    ]
    for column in amount_columns:
        coverage[column] = coverage[column].astype(float)
    coverage["registry_to_official_pct"] = (
        coverage["registry_amount_all_eur"]
        / coverage["official_total_amount_eur"]
        * 100
    )
    coverage["analytical_to_official_pct"] = (
        coverage["registry_amount_valid_oib_eur"]
        / coverage["official_total_amount_eur"]
        * 100
    )
    return coverage


def aid_type_concentration_output(
    conn: pymysql.connections.Connection,
    snapshot_id: int,
) -> pd.DataFrame:
    recipient_type = query_frame(
        conn,
        f"""
        SELECT COALESCE(aid_type, 'Nepoznato') AS aid_type,
               recipient_oib,
               COUNT(*) AS award_count,
               SUM(gross_amount_eur) AS amount_eur
        FROM {SOURCE_SCHEMA}.{SOURCE_TABLE}
        WHERE {base_filter(valid_oib=True)}
        GROUP BY COALESCE(aid_type, 'Nepoznato'), recipient_oib
        """,
        (snapshot_id,),
    )
    recipient_type["amount_eur"] = recipient_type["amount_eur"].astype(float)

    rows: list[dict[str, Any]] = []
    total_amount = float(recipient_type["amount_eur"].sum())
    for aid_type, group in recipient_type.groupby("aid_type", sort=False):
        ranked = group.sort_values("amount_eur", ascending=False).reset_index(drop=True)
        recipient_count = len(ranked)
        top_1_count = math.ceil(recipient_count * 0.01)
        amount_eur = float(ranked["amount_eur"].sum())
        top_1_amount = float(ranked.head(top_1_count)["amount_eur"].sum())
        rows.append(
            {
                "aid_type": aid_type,
                "recipient_count": recipient_count,
                "award_count": int(ranked["award_count"].sum()),
                "amount_eur": amount_eur,
                "amount_share_pct": amount_eur / total_amount * 100,
                "top_1_recipient_count": top_1_count,
                "top_1_amount_eur": top_1_amount,
                "top_1_amount_share_pct": top_1_amount / amount_eur * 100,
                "median_recipient_amount_eur": float(ranked["amount_eur"].median()),
            }
        )
    output = pd.DataFrame(rows).sort_values("amount_eur", ascending=False).reset_index(drop=True)
    output["display_order"] = np.arange(1, len(output) + 1)
    return output


def recurrence_output(
    conn: pymysql.connections.Connection,
    snapshot_id: int,
) -> pd.DataFrame:
    recipients = query_frame(
        conn,
        f"""
        SELECT recipient_oib,
               COUNT(DISTINCT CAST(LEFT(awarded_at, 4) AS UNSIGNED)) AS active_year_count,
               COUNT(*) AS award_count,
               SUM(gross_amount_eur) AS amount_eur
        FROM {SOURCE_SCHEMA}.{SOURCE_TABLE}
        WHERE {base_filter(valid_oib=True, start_year=2023, end_year=2024)}
        GROUP BY recipient_oib
        """,
        (snapshot_id,),
    )
    recipients["amount_eur"] = recipients["amount_eur"].astype(float)
    recipients["recurrence_group"] = np.where(
        recipients["active_year_count"] >= 2,
        "Obje godine",
        "Jedna godina",
    )
    output = (
        recipients.groupby("recurrence_group", as_index=False)
        .agg(
            recipient_count=("recipient_oib", "size"),
            award_count=("award_count", "sum"),
            amount_eur=("amount_eur", "sum"),
        )
    )
    output["recipient_share_pct"] = (
        output["recipient_count"] / output["recipient_count"].sum() * 100
    )
    output["amount_share_pct"] = output["amount_eur"] / output["amount_eur"].sum() * 100
    output["average_amount_per_recipient_eur"] = (
        output["amount_eur"] / output["recipient_count"]
    )
    output["display_order"] = output["recurrence_group"].map(
        {"Jedna godina": 1, "Obje godine": 2}
    )
    return output.sort_values("display_order")


def gini(values: np.ndarray) -> float:
    clean = np.asarray(values, dtype=float)
    clean = clean[np.isfinite(clean) & (clean >= 0)]
    if clean.size == 0 or clean.sum() == 0:
        return float("nan")
    clean.sort()
    n = clean.size
    ranks = np.arange(1, n + 1, dtype=float)
    return float((2 * np.sum(ranks * clean) / (n * clean.sum())) - (n + 1) / n)


def concentration_outputs(
    conn: pymysql.connections.Connection,
    snapshot_id: int,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    recipients = query_frame(
        conn,
        f"""
        SELECT recipient_oib, COUNT(*) AS award_count,
               SUM(gross_amount_eur) AS amount_eur
        FROM {SOURCE_SCHEMA}.{SOURCE_TABLE}
        WHERE {base_filter(valid_oib=True)}
        GROUP BY recipient_oib
        """,
        (snapshot_id,),
    )
    recipients["amount_eur"] = recipients["amount_eur"].astype(float)
    recipients = recipients.sort_values("amount_eur", ascending=False).reset_index(drop=True)

    n = len(recipients)
    total = float(recipients["amount_eur"].sum())
    top_1_n = math.ceil(n * 0.01)
    top_10pct_n = math.ceil(n * 0.10)

    group_specs = [
        ("Gornjih 1%", 0, top_1_n, 1),
        ("Sljedećih 9%", top_1_n, top_10pct_n, 2),
        ("Donjih 90%", top_10pct_n, n, 3),
    ]
    rows = []
    for label, start, end, order in group_specs:
        amount = float(recipients.iloc[start:end]["amount_eur"].sum())
        count = int(end - start)
        rows.append(
            {
                "group": label,
                "display_order": order,
                "recipient_count": count,
                "recipient_share_pct": count / n * 100,
                "amount_eur": amount,
                "amount_share_pct": amount / total * 100,
            }
        )
    groups = pd.DataFrame(rows)

    facts = {
        "recipient_count": n,
        "amount_eur": total,
        "award_count_oib": int(recipients["award_count"].sum()),
        "top_1_recipient_count": top_1_n,
        "top_1_amount_eur": float(recipients.head(top_1_n)["amount_eur"].sum()),
        "top_1_amount_share_pct": float(groups.loc[groups["group"] == "Gornjih 1%", "amount_share_pct"].iloc[0]),
        "top_10_entities_amount_eur": float(recipients.head(10)["amount_eur"].sum()),
        "top_10_entities_share_pct": float(recipients.head(10)["amount_eur"].sum() / total * 100),
        "top_10pct_recipient_count": top_10pct_n,
        "top_10pct_share_pct": float(recipients.head(top_10pct_n)["amount_eur"].sum() / total * 100),
        "median_recipient_amount_eur": float(recipients["amount_eur"].median()),
        "gini": gini(recipients["amount_eur"].to_numpy()),
    }
    return groups, facts


def category_outputs(
    conn: pymysql.connections.Connection,
    snapshot_id: int,
) -> dict[str, pd.DataFrame]:
    size = query_frame(
        conn,
        f"""
        SELECT COALESCE(company_size, 'Nepoznato') AS company_size,
               COUNT(*) AS award_count,
               COUNT(DISTINCT recipient_oib) AS recipient_count,
               SUM(gross_amount_eur) AS amount_eur
        FROM {SOURCE_SCHEMA}.{SOURCE_TABLE}
        WHERE {base_filter(valid_oib=True)}
        GROUP BY COALESCE(company_size, 'Nepoznato')
        """,
        (snapshot_id,),
    )
    size["amount_eur"] = size["amount_eur"].astype(float)
    size["amount_share_pct"] = size["amount_eur"] / size["amount_eur"].sum() * 100
    size["average_award_eur"] = size["amount_eur"] / size["award_count"]
    size["display_order"] = size["company_size"].map(
        {label: idx + 1 for idx, label in enumerate(SIZE_ORDER)}
    ).fillna(len(SIZE_ORDER) + 1)
    size = size.sort_values("display_order")

    aid_type = query_frame(
        conn,
        f"""
        SELECT COALESCE(aid_type, 'Nepoznato') AS aid_type,
               COUNT(*) AS award_count,
               COUNT(DISTINCT recipient_oib) AS recipient_count,
               SUM(gross_amount_eur) AS amount_eur
        FROM {SOURCE_SCHEMA}.{SOURCE_TABLE}
        WHERE {base_filter(valid_oib=True)}
        GROUP BY COALESCE(aid_type, 'Nepoznato')
        ORDER BY amount_eur DESC
        """,
        (snapshot_id,),
    )
    aid_type["amount_eur"] = aid_type["amount_eur"].astype(float)
    aid_type["amount_share_pct"] = aid_type["amount_eur"] / aid_type["amount_eur"].sum() * 100

    sector = query_frame(
        conn,
        f"""
        SELECT COALESCE(activity_section_2007, 'Nepoznato') AS activity,
               COUNT(*) AS award_count,
               COUNT(DISTINCT recipient_oib) AS recipient_count,
               SUM(gross_amount_eur) AS amount_eur
        FROM {SOURCE_SCHEMA}.{SOURCE_TABLE}
        WHERE {base_filter(valid_oib=True)}
        GROUP BY COALESCE(activity_section_2007, 'Nepoznato')
        ORDER BY amount_eur DESC
        """,
        (snapshot_id,),
    )
    sector["amount_eur"] = sector["amount_eur"].astype(float)
    sector["amount_share_pct"] = sector["amount_eur"] / sector["amount_eur"].sum() * 100

    yearly = query_frame(
        conn,
        f"""
        SELECT CAST(LEFT(awarded_at, 4) AS UNSIGNED) AS year,
               COUNT(*) AS award_count,
               COUNT(DISTINCT recipient_oib) AS recipient_count,
               SUM(gross_amount_eur) AS amount_eur
        FROM {SOURCE_SCHEMA}.{SOURCE_TABLE}
        WHERE {base_filter(valid_oib=True)}
        GROUP BY CAST(LEFT(awarded_at, 4) AS UNSIGNED)
        ORDER BY year
        """,
        (snapshot_id,),
    )
    yearly["amount_eur"] = yearly["amount_eur"].astype(float)

    return {"size": size, "aid_type": aid_type, "sector": sector, "year": yearly}


def validation_output(
    conn: pymysql.connections.Connection,
    snapshot: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    snapshot_id = int(snapshot["snapshot_id"])
    validation = query_one(
        conn,
        f"""
        SELECT COUNT(*) AS raw_rows,
               SUM(verification_status = 'Ispravan') AS verified_rows,
               SUM(verification_status = 'Upozorenje') AS warning_rows,
               SUM(verification_status = 'Upozorenje' AND gross_amount_eur > 0) AS positive_warning_rows,
               MAX(CASE WHEN verification_status = 'Upozorenje' THEN gross_amount_eur END) AS max_warning_amount_eur,
               SUM({base_filter(valid_oib=False)}) AS included_awards_all,
               SUM({base_filter(valid_oib=True)}) AS included_awards_valid_oib,
               SUM(CASE WHEN {base_filter(valid_oib=False)} THEN gross_amount_eur ELSE 0 END) AS included_amount_all_eur,
               SUM(CASE WHEN {base_filter(valid_oib=True)} THEN gross_amount_eur ELSE 0 END) AS included_amount_valid_oib_eur
        FROM {SOURCE_SCHEMA}.{SOURCE_TABLE}
        WHERE snapshot_id = %s
        """,
        (snapshot_id,) * 5,
    )
    details = json.loads(snapshot.get("details_json") or "{}")
    values = {
        **validation,
        "snapshot_id": snapshot_id,
        "source_total_rows": int(snapshot["total_rows"]),
        "source_valid_rows": int(snapshot["valid_rows"]),
        "source_invalid_rows": int(snapshot["invalid_rows"]),
        "snapshot_completed_at": str(snapshot["completed_at"]),
        "source_uri": details.get("source_uri", "https://rdp.gov.hr/javno"),
        "source_recipient_oib_count": details.get("recipient_oib_count"),
        "source_gdpr_recipient_count": details.get("gdpr_recipient_count"),
    }
    frame = pd.DataFrame(
        [{"metric": key, "value": value} for key, value in values.items()]
    )
    return frame, values


def json_ready(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if hasattr(value, "item"):
        return json_ready(value.item())
    return value


def write_facts(
    concentration: dict[str, Any],
    validation: dict[str, Any],
    categories: dict[str, pd.DataFrame],
    coverage: pd.DataFrame,
    aid_type_concentration: pd.DataFrame,
    recurrence: pd.DataFrame,
) -> dict[str, Any]:
    size = categories["size"].set_index("company_size")
    coverage_by_year = coverage.set_index("year")
    recurrence_by_group = recurrence.set_index("recurrence_group")
    facts: dict[str, Any] = {
        "period_start": START_YEAR,
        "period_end": END_YEAR,
        **concentration,
        "included_awards_all": int(validation["included_awards_all"]),
        "included_awards_valid_oib": int(validation["included_awards_valid_oib"]),
        "included_amount_all_eur": float(validation["included_amount_all_eur"]),
        "included_amount_valid_oib_eur": float(validation["included_amount_valid_oib_eur"]),
        "excluded_warning_max_eur": float(validation["max_warning_amount_eur"]),
        "source_snapshot_completed_at": validation["snapshot_completed_at"],
        "source_uri": validation["source_uri"],
    }
    for year in [2021, 2022, 2023]:
        if year not in coverage_by_year.index:
            raise RuntimeError(f"Missing coverage year: {year}")
        row = coverage_by_year.loc[year]
        facts[f"coverage_{year}_official_amount_eur"] = float(
            row["official_total_amount_eur"]
        )
        facts[f"coverage_{year}_registry_amount_all_eur"] = float(
            row["registry_amount_all_eur"]
        )
        facts[f"coverage_{year}_analytical_amount_eur"] = float(
            row["registry_amount_valid_oib_eur"]
        )
        facts[f"coverage_{year}_registry_to_official_pct"] = float(
            row["registry_to_official_pct"]
        )
        facts[f"coverage_{year}_analytical_to_official_pct"] = float(
            row["analytical_to_official_pct"]
        )

    for group, prefix in [("Jedna godina", "one_year"), ("Obje godine", "both_years")]:
        if group not in recurrence_by_group.index:
            raise RuntimeError(f"Missing recurrence group: {group}")
        row = recurrence_by_group.loc[group]
        facts[f"{prefix}_recipient_count"] = int(row["recipient_count"])
        facts[f"{prefix}_recipient_share_pct"] = float(row["recipient_share_pct"])
        facts[f"{prefix}_amount_eur"] = float(row["amount_eur"])
        facts[f"{prefix}_amount_share_pct"] = float(row["amount_share_pct"])

    major_types = aid_type_concentration.loc[
        aid_type_concentration["amount_share_pct"] >= 10
    ].copy()
    facts["major_aid_type_count"] = int(len(major_types))
    facts["major_aid_type_top_1_share_min_pct"] = float(
        major_types["top_1_amount_share_pct"].min()
    )
    facts["major_aid_type_top_1_share_max_pct"] = float(
        major_types["top_1_amount_share_pct"].max()
    )
    for label, prefix in [("Veliki", "large"), ("Mikro", "micro")]:
        if label not in size.index:
            raise RuntimeError(f"Missing company-size category: {label}")
        facts[f"{prefix}_award_count"] = int(size.loc[label, "award_count"])
        facts[f"{prefix}_recipient_count"] = int(size.loc[label, "recipient_count"])
        facts[f"{prefix}_amount_eur"] = float(size.loc[label, "amount_eur"])
        facts[f"{prefix}_amount_share_pct"] = float(size.loc[label, "amount_share_pct"])
        facts[f"{prefix}_average_award_eur"] = float(size.loc[label, "average_award_eur"])
    facts["large_to_micro_average_award_ratio"] = (
        facts["large_average_award_eur"] / facts["micro_average_award_eur"]
    )

    clean = {key: json_ready(value) for key, value in facts.items()}
    (FACT_DIR / "state_aid_concentration.json").write_text(
        json.dumps(clean, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return clean


def main() -> None:
    ensure_dirs()
    conn = connect()
    try:
        snapshot = published_snapshot(conn)
        snapshot_id = int(snapshot["snapshot_id"])
        groups, concentration = concentration_outputs(conn, snapshot_id)
        categories = category_outputs(conn, snapshot_id)
        coverage = coverage_output(conn, snapshot_id)
        aid_type_concentration = aid_type_concentration_output(conn, snapshot_id)
        recurrence = recurrence_output(conn, snapshot_id)
        validation_frame, validation = validation_output(conn, snapshot)
    finally:
        conn.close()

    groups.to_csv(
        TABLE_DIR / "state_aid_concentration_groups.csv",
        index=False,
        encoding="utf-8-sig",
    )
    categories["size"].to_csv(
        TABLE_DIR / "state_aid_concentration_by_size.csv",
        index=False,
        encoding="utf-8-sig",
    )
    categories["aid_type"].to_csv(
        TABLE_DIR / "state_aid_concentration_by_type.csv",
        index=False,
        encoding="utf-8-sig",
    )
    categories["sector"].to_csv(
        TABLE_DIR / "state_aid_concentration_by_sector.csv",
        index=False,
        encoding="utf-8-sig",
    )
    categories["year"].to_csv(
        TABLE_DIR / "state_aid_concentration_by_year.csv",
        index=False,
        encoding="utf-8-sig",
    )
    validation_frame.to_csv(
        TABLE_DIR / "state_aid_concentration_validation.csv",
        index=False,
        encoding="utf-8-sig",
    )
    coverage.to_csv(
        TABLE_DIR / "state_aid_coverage_comparison.csv",
        index=False,
        encoding="utf-8-sig",
    )
    aid_type_concentration.to_csv(
        TABLE_DIR / "state_aid_concentration_within_type.csv",
        index=False,
        encoding="utf-8-sig",
    )
    recurrence.to_csv(
        TABLE_DIR / "state_aid_recipient_recurrence_2023_2024.csv",
        index=False,
        encoding="utf-8-sig",
    )
    facts = write_facts(
        concentration,
        validation,
        categories,
        coverage,
        aid_type_concentration,
        recurrence,
    )

    print(
        "OK - state aid concentration outputs saved | "
        f"recipients={facts['recipient_count']:,} | "
        f"amount_eur={facts['amount_eur']:,.0f} | "
        f"top_1_share={facts['top_1_amount_share_pct']:.2f}%"
    )


if __name__ == "__main__":
    main()
