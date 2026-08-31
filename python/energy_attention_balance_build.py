"""Build the audited inputs for the Croatian energy media/sector post.

The post compares three different quantities and keeps them separate:

* media attention from the EnergoKlima corpus;
* physical 2023 sector indicators transcribed from EIZ, Sektorske analize 123;
* 2023 FINA GFI aggregates for NKD 35, decoded with the physical db_afs codebook.

The EnergoKlima and GFI sources are read only. Published numbers are written to
``outputs/tables`` and ``outputs/facts`` so the Quarto post never depends on a
live database during rendering.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import duckdb
import pandas as pd
import pymysql


POST_SLUG = "2026-08-energetika-izmedu-naslova-i-bilance"
FOCAL_TOPICS = {
    "cijene_energije": "Cijene energije",
    "lng_sigurnost": "Sigurnost opskrbe i LNG",
    "solarna": "Sunčana energija",
    "elektromobilnost": "Elektromobilnost",
    "dizalice_obnova": "Obnova i dizalice topline",
    "politika_eu": "EU politika i NECP",
}

# Table 5 (p. 36), EIZ Sektorske analize 123, June 2025. Values are 2023
# total revenue in million euro. Ownership is used only for the two-group cut.
TOP_COMPANIES = [
    ("hep", "HEP d.d.", 3661.7, "state"),
    ("ppd", "Prvo plinarsko društvo", 3501.5, "private"),
    ("hep_proizvodnja", "HEP-Proizvodnja", 1716.9, "state"),
    ("met_croatia", "MET Croatia Energy Trade", 1239.3, "private"),
    ("hep_elektra", "HEP ELEKTRA", 894.9, "state"),
    ("mvm_ceenergy", "MVM CEEnergy Croatia", 607.9, "private"),
    ("hep_ods", "HEP-ODS", 537.4, "state"),
    ("hops", "HOPS d.d.", 367.5, "state"),
    ("gpz_opskrba", "Gradska plinara Zagreb – Opskrba", 311.7, "state"),
    ("gen_i", "GEN-I Hrvatska", 267.8, "private"),
]

# Physical indicators transcribed from pp. 13, 18, 23 and 31 of the same EIZ
# issue. The mix rows are shares within renewable electricity generation.
PHYSICAL_ROWS = [
    ("renewable_electricity_share", "Obnovljivi izvori u bruto potrošnji električne energije", 58.83, "%", 2023, 13),
    ("renewable_mix_hydro", "Hidroenergija u obnovljivoj električnoj energiji", 63.0, "%", 2023, 13),
    ("renewable_mix_wind", "Vjetar u obnovljivoj električnoj energiji", 24.0, "%", 2023, 13),
    ("renewable_mix_biomass", "Kruta biomasa u obnovljivoj električnoj energiji", 6.0, "%", 2023, 13),
    ("renewable_mix_solar", "Sunce u obnovljivoj električnoj energiji", 4.0, "%", 2023, 13),
    ("renewable_mix_other", "Ostalo u obnovljivoj električnoj energiji", 3.0, "%", 2023, 13),
    ("renewable_heat_share", "Obnovljivi izvori u grijanju i hlađenju", 36.2, "%", 2023, 18),
    ("heat_biomass_share", "Biomasa u finalnoj obnovljivoj energiji za grijanje", 91.0, "%", 2023, 18),
    ("heat_pumps_share", "Dizalice topline u obnovljivoj energiji za grijanje", 1.4, "%", 2023, 18),
    ("renewable_transport_share", "Obnovljivi izvori u prijevozu", 1.0, "%", 2023, 23),
    ("renewable_transport_target_2030", "Cilj obnovljivih izvora u prijevozu", 24.6, "%", 2030, 31),
    ("renewable_overall_share", "Obnovljivi izvori u bruto finalnoj potrošnji energije", 28.1, "%", 2023, 31),
    ("renewable_overall_target_2030", "Nacionalni cilj obnovljivih izvora", 42.5, "%", 2030, 31),
]


def project_root() -> Path:
    current = Path.cwd().resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "_quarto.yml").exists() and (candidate / "CroAIcon.Rproj").exists():
            return candidate
    raise RuntimeError("Cannot locate the CroAIcon project root.")


ROOT = project_root()
TABLE_DIR = ROOT / "outputs" / "tables"
FACT_DIR = ROOT / "outputs" / "facts"


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def required_external_path(variable: str) -> Path:
    value = os.environ.get(variable)
    if not value:
        raise RuntimeError(
            f"Missing {variable}. Point it to the external, untracked source file."
        )
    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def mysql_connection() -> pymysql.connections.Connection:
    load_env_file(ROOT / ".env")
    load_env_file(ROOT / ".Renviron")
    required = ["GFI_DB_HOST", "GFI_DB_USER", "GFI_DB_PASSWORD", "GFI_DB_NAME"]
    missing = [key for key in required if not os.environ.get(key)]
    if missing:
        raise RuntimeError(f"Missing GFI database variables: {', '.join(missing)}")
    return pymysql.connect(
        host=os.environ["GFI_DB_HOST"],
        port=int(os.environ.get("GFI_DB_PORT", "3306")),
        user=os.environ["GFI_DB_USER"],
        password=os.environ["GFI_DB_PASSWORD"],
        database=os.environ["GFI_DB_NAME"],
        charset="utf8mb4",
        connect_timeout=15,
        read_timeout=180,
    )


def build_media() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    media_db = required_external_path("ENERGOKLIMA_CORPUS_DB")
    con = duckdb.connect(str(media_db), read_only=True)

    monthly = con.execute(
        """
        WITH den AS (
          SELECT month,
                 SUM(n_after_dedup) AS population,
                 SUM(n_after_dedup_has_text) AS population_text,
                 CASE WHEN SUM(n_after_dedup_has_text) > 0.6 * SUM(n_after_dedup)
                      THEN SUM(n_after_dedup_has_text) ELSE SUM(n_after_dedup) END AS base,
                 MAX(source) AS regime
          FROM population
          GROUP BY month
        ), num AS (
          SELECT month, COUNT(*) AS documents
          FROM documents
          GROUP BY month
        )
        SELECT den.month, num.documents, den.population, den.population_text, den.base,
               den.regime, den.population_text < 0.6 * den.population AS reduced_recall,
               100.0 * num.documents / den.base AS media_share_pct
        FROM den JOIN num USING (month)
        ORDER BY den.month
        """
    ).df()

    topic_rows = []
    for key, label in FOCAL_TOPICS.items():
        rows = con.execute(
            """
            WITH den AS (
              SELECT SUBSTR(month, 1, 4) AS year, COUNT(*) AS documents
              FROM documents
              WHERE SUBSTR(month, 1, 4) IN ('2022', '2023')
              GROUP BY 1
            ), num AS (
              SELECT SUBSTR(d.month, 1, 4) AS year,
                     COUNT(DISTINCT d.doc_id) AS topic_documents
              FROM documents d JOIN doc_categories dc USING (doc_id)
              WHERE dc.category = ? AND SUBSTR(d.month, 1, 4) IN ('2022', '2023')
              GROUP BY 1
            )
            SELECT num.year, num.topic_documents, den.documents,
                   100.0 * num.topic_documents / den.documents AS corpus_share_pct
            FROM num JOIN den USING (year)
            ORDER BY num.year
            """,
            [key],
        ).fetchall()
        for year, topic_docs, all_docs, share in rows:
            topic_rows.append(
                {
                    "category": key,
                    "topic": label,
                    "year": int(year),
                    "topic_documents": int(topic_docs),
                    "energy_documents": int(all_docs),
                    "corpus_share_pct": float(share),
                }
            )
    topics = pd.DataFrame(topic_rows)

    company_rows = []
    for entity_id, company, revenue_m_eur, ownership in TOP_COMPANIES:
        docs = con.execute(
            """
            SELECT COUNT(DISTINCT d.doc_id)
            FROM documents d JOIN doc_entities de USING (doc_id)
            WHERE d.month BETWEEN '2023-01' AND '2023-12' AND de.entity_id = ?
            """,
            [entity_id],
        ).fetchone()[0]
        company_rows.append(
            {
                "entity_id": entity_id,
                "company": company,
                "ownership": ownership,
                "total_revenue_m_eur": revenue_m_eur,
                "media_documents_2023": int(docs),
            }
        )
    companies = pd.DataFrame(company_rows)

    state_ids = companies.loc[companies.ownership == "state", "entity_id"].tolist()
    private_ids = companies.loc[companies.ownership == "private", "entity_id"].tolist()
    st_ph = ",".join("?" for _ in state_ids)
    pv_ph = ",".join("?" for _ in private_ids)
    voice = con.execute(
        f"""
        WITH mentions AS (
          SELECT d.doc_id,
                 BOOL_OR(de.entity_id IN ({st_ph})) AS state_mention,
                 BOOL_OR(de.entity_id IN ({pv_ph})) AS private_mention
          FROM documents d JOIN doc_entities de USING (doc_id)
          WHERE d.month BETWEEN '2023-01' AND '2023-12'
          GROUP BY d.doc_id
        )
        SELECT COUNT(*) FILTER (WHERE state_mention AND NOT private_mention) AS state_only,
               COUNT(*) FILTER (WHERE private_mention AND NOT state_mention) AS private_only,
               COUNT(*) FILTER (WHERE state_mention AND private_mention) AS both,
               COUNT(*) FILTER (WHERE state_mention OR private_mention) AS any_company
        FROM mentions
        """,
        [*state_ids, *private_ids],
    ).fetchone()

    meta = dict(con.execute("SELECT key, value FROM build_meta").fetchall())
    corpus_n, first_month, last_month = con.execute(
        "SELECT COUNT(*), MIN(month), MAX(month) FROM documents"
    ).fetchone()
    con.close()
    media_facts = {
        "database": str(media_db),
        "corpus_documents": int(corpus_n),
        "first_month": first_month,
        "last_month": last_month,
        "latest_append_documents": int(meta["ext_docs_new"]),
        "extension_source_range": meta["ext_source_range"],
        "extension_source_files": meta["ext_source_files"],
        "state_only_2023": int(voice[0]),
        "private_only_2023": int(voice[1]),
        "both_2023": int(voice[2]),
        "any_top_company_2023": int(voice[3]),
    }
    return monthly, topics, companies, media_facts


def build_gfi() -> tuple[pd.DataFrame, pd.DataFrame]:
    conn = mysql_connection()
    codebook_sql = """
        SELECT db_column, aop_number, report_label, position_label, source_file
        FROM codes_gfi_db_afs_physical
        WHERE db_column IN ('b145', 'b147', 'b151')
        ORDER BY db_column
    """
    gfi_sql = """
        SELECT reportyear AS year,
               COUNT(*) AS n_reports,
               COUNT(DISTINCT subjecttaxnoid) AS n_firms,
               SUM(COALESCE(employeecounteop, 0)) AS employees,
               SUM(COALESCE(b145, 0)) AS total_revenue_eur,
               SUM(COALESCE(b147, 0)) AS pretax_result_eur,
               SUM(COALESCE(b151, 0)) AS net_result_eur
        FROM db_afs
        WHERE reportyear = 2023 AND nacerev22 = 35
        GROUP BY reportyear
    """
    codebook = pd.read_sql(codebook_sql, conn)
    sector = pd.read_sql(gfi_sql, conn)
    conn.close()
    expected = {
        "b145": "UKUPNI PRIHODI",
        "b147": "PRIJE OPOREZIVANJA",
        "b151": "DOBIT ILI GUBITAK RAZDOBLJA",
    }
    got = dict(zip(codebook.db_column, codebook.position_label))
    for column, phrase in expected.items():
        if column not in got or phrase not in str(got[column]).upper():
            raise AssertionError(f"Physical GFI codebook mismatch for {column}: {got.get(column)!r}")
    if sector.empty or int(sector.iloc[0].n_firms) != 1248:
        raise AssertionError("Unexpected 2023 NKD 35 GFI coverage.")
    return codebook, sector


def main() -> None:
    load_env_file(ROOT / ".env")
    load_env_file(ROOT / ".Renviron")
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FACT_DIR.mkdir(parents=True, exist_ok=True)
    eiz_pdf = required_external_path("ENERGY_EIZ_PDF")

    monthly, topics, companies, media = build_media()
    codebook, sector = build_gfi()
    physical = pd.DataFrame(
        PHYSICAL_ROWS,
        columns=["metric", "label", "value", "unit", "reference_year", "eiz_page"],
    )
    physical["source"] = "EIZ, Sektorske analize 123: Energetika – obnovljivi izvori energije (lipanj 2025.)"

    top_revenue = float(companies.total_revenue_m_eur.sum())
    private_revenue = float(
        companies.loc[companies.ownership == "private", "total_revenue_m_eur"].sum()
    )
    state_revenue = top_revenue - private_revenue
    sector_revenue_m = float(sector.iloc[0].total_revenue_eur) / 1_000_000
    exclusive_voice = media["state_only_2023"] + media["private_only_2023"]
    peak = monthly.loc[monthly.media_share_pct.idxmax()]

    annual = (
        monthly.assign(year=monthly.month.str[:4])
        .query("year in ['2021', '2022', '2023']")
        .groupby("year", as_index=False)
        .agg(documents=("documents", "sum"), base=("base", "sum"))
    )
    annual["media_share_pct"] = annual.documents / annual.base * 100

    ownership = pd.DataFrame(
        [
            {
                "measure": "Prihod deset najvećih, 2023.",
                "state_pct": 100 * state_revenue / top_revenue,
                "private_pct": 100 * private_revenue / top_revenue,
                "excluded_both": 0,
            },
            {
                "measure": "Medijske objave o tim tvrtkama, 2023.",
                "state_pct": 100 * media["state_only_2023"] / exclusive_voice,
                "private_pct": 100 * media["private_only_2023"] / exclusive_voice,
                "excluded_both": media["both_2023"],
            },
        ]
    )

    facts = {
        "post_slug": POST_SLUG,
        "media": {
            **media,
            "peak_month": str(peak.month),
            "peak_share_pct": float(peak.media_share_pct),
            "annual": annual.to_dict(orient="records"),
            "determdb_precision_genuine_pct": 81.9,
            "determdb_precision_core_pct": 63.8,
        },
        "physical": {row.metric: float(row.value) for row in physical.itertuples()},
        "gfi_2023": {
            "n_firms": int(sector.iloc[0].n_firms),
            "employees": int(sector.iloc[0].employees),
            "total_revenue_eur": float(sector.iloc[0].total_revenue_eur),
            "pretax_result_eur": float(sector.iloc[0].pretax_result_eur),
            "net_result_eur": float(sector.iloc[0].net_result_eur),
            "top_ten_revenue_eur": top_revenue * 1_000_000,
            "top_ten_share_pct": 100 * top_revenue / sector_revenue_m,
            "top_ten_private_revenue_share_pct": 100 * private_revenue / top_revenue,
            "top_ten_state_revenue_share_pct": 100 * state_revenue / top_revenue,
            "media_state_exclusive_share_pct": 100 * media["state_only_2023"] / exclusive_voice,
            "media_private_exclusive_share_pct": 100 * media["private_only_2023"] / exclusive_voice,
        },
        "sources": {
            "eiz_pdf": str(eiz_pdf),
            "media_database": media["database"],
            "gfi_table": "db_afs",
            "gfi_codebook": "codes_gfi_db_afs_physical",
        },
    }

    checks = pd.DataFrame(
        [
            ("media_latest_month", media["last_month"] == "2025-06", media["last_month"]),
            ("media_latest_append", media["latest_append_documents"] == 20984, media["latest_append_documents"]),
            ("renewable_mix_sums_100", physical.query("metric.str.startswith('renewable_mix_')", engine="python").value.sum() == 100, physical.query("metric.str.startswith('renewable_mix_')", engine="python").value.sum()),
            ("top_ten_revenue_reproduced", abs(top_revenue - 13106.6) < 0.01, top_revenue),
            ("gfi_2023_firms", int(sector.iloc[0].n_firms) == 1248, int(sector.iloc[0].n_firms)),
            ("gfi_2023_revenue_positive", float(sector.iloc[0].total_revenue_eur) > 0, float(sector.iloc[0].total_revenue_eur)),
            ("exclusive_voice_reconciles", exclusive_voice == 4957, exclusive_voice),
        ],
        columns=["check", "passed", "value"],
    )
    if not checks.passed.all():
        raise AssertionError(checks.loc[~checks.passed].to_string(index=False))

    monthly.to_csv(TABLE_DIR / "energy_media_monthly.csv", index=False)
    annual.to_csv(TABLE_DIR / "energy_media_annual.csv", index=False)
    topics.to_csv(TABLE_DIR / "energy_media_topic_shift.csv", index=False)
    companies.to_csv(TABLE_DIR / "energy_top_companies_2023.csv", index=False)
    ownership.to_csv(TABLE_DIR / "energy_revenue_media_ownership.csv", index=False)
    physical.to_csv(TABLE_DIR / "energy_physical_2023.csv", index=False)
    codebook.to_csv(TABLE_DIR / "energy_gfi_codebook_audit.csv", index=False)
    sector.to_csv(TABLE_DIR / "energy_gfi_nkd35_2023.csv", index=False)
    checks.to_csv(TABLE_DIR / "energy_validation.csv", index=False)
    (FACT_DIR / "energy_attention_balance.json").write_text(
        json.dumps(facts, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"wrote energy post inputs: {media['corpus_documents']:,} media documents; "
        f"{int(sector.iloc[0].n_firms):,} GFI firms; {len(checks)} checks PASS"
    )


if __name__ == "__main__":
    main()
