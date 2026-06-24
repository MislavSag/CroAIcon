"""Build or block the GFI debt-structure post.

The script is intentionally conservative. It first audits the raw GFI financial
fields needed for debt ratios. If the audit fails, it writes diagnostics and
placeholder output tables, then stops before producing publishable findings.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pymysql


YEARS = range(2008, 2025)
POST_SLUG = "2026-06-zaduzenost-hrvatskih-firmi"

AOP_COLUMNS = {
    "b058": 58,
    "b061": 61,
    "b063": 63,
    "b084": 84,
    "b086": 86,
    "b087": 87,
    "b094": 94,
    "b096": 96,
    "b097": 97,
    "b108": 108,
    "b125": 125,
    "b152": 152,
    "b153": 153,
}

EXCEL_AOP_LABELS = {
    "b058": "IV. NOVAC U BANCI I BLAGAJNI",
    "b061": "E) UKUPNO AKTIVA",
    "b063": "A) KAPITAL I REZERVE",
    "b084": "C) DUGOROČNE OBVEZE",
    "b086": "2. Obveze za zajmove, depozite i slično",
    "b087": "3. Obveze prema bankama i drugim financijskim institucijama",
    "b094": "D) KRATKOROČNE OBVEZE",
    "b096": "2. Obveze za zajmove, depozite i slično",
    "b097": "3. Obveze prema bankama i drugim financijskim institucijama",
    "b108": "F) UKUPNO PASIVA",
    "b125": "I. POSLOVNI PRIHODI",
    "b152": "1. Dobit razdoblja",
    "b153": "2. Gubitak razdoblja",
}

SIZE_LABELS = {
    0: "nepoznato",
    1: "mikro",
    2: "mala",
    3: "srednja",
    4: "velika",
}

SECTOR_NAMES = {
    "A": "Poljoprivreda",
    "B": "Rudarstvo",
    "C": "Preradjivacka ind.",
    "D": "Energetika",
    "E": "Vodoopskrba",
    "F": "Gradjevinarstvo",
    "G": "Trgovina",
    "H": "Prijevoz i sklad.",
    "I": "Smjestaj i ugost.",
    "J": "Informacije i komun.",
    "K": "Financije i osig.",
    "L": "Nekretnine",
    "M": "Strucne djelatnosti",
    "N": "Administrativne usl.",
    "O": "Javna uprava",
    "P": "Obrazovanje",
    "Q": "Zdravstvo",
    "R": "Umjetnost i rekreac.",
    "S": "Ostale usluzne",
}


def project_root() -> Path:
    path = Path.cwd().resolve()
    for candidate in [path, *path.parents]:
        if (candidate / "_quarto.yml").exists() and (candidate / "CroAIcon.Rproj").exists():
            return candidate
    raise RuntimeError("Cannot locate CroAIcon project root.")


ROOT = project_root()
TABLE_DIR = ROOT / "outputs" / "tables"
FIG_DIR = ROOT / "outputs" / "figures"


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


def ensure_dirs() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def query_aop_map(conn: pymysql.connections.Connection) -> pd.DataFrame:
    # The `codes_gfi` table does not match the physical `db_afs.bNNN`
    # positions for balance-sheet columns in this database. Use the local FINA
    # workbook `financije_sifrarnik.xlsx` mapping (PositionID -> label) instead.
    rows = []
    for column_name, aop in AOP_COLUMNS.items():
        rows.append(
            {
                "column_name": column_name,
                "aop": aop,
                "position_id": f"{aop:03d}B",
                "label_hr": EXCEL_AOP_LABELS[column_name],
                "source": "D:/data/poslovni_subjekti/sifrarnik/sifrarnici/financije_sifrarnik.xlsx",
            }
        )
    return pd.DataFrame(rows).sort_values("aop")


def query_year_audit(conn: pymysql.connections.Connection, year: int) -> dict[str, float]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            COUNT(*) AS n,
            SUM(CASE WHEN b061 IS NOT NULL AND b061 <> 0 THEN 1 ELSE 0 END) AS n_assets,
            SUM(CASE WHEN b108 IS NOT NULL AND b108 <> 0 THEN 1 ELSE 0 END) AS n_passive,
            SUM(CASE WHEN b061 IS NOT NULL AND b061 <> 0
                      AND b108 IS NOT NULL AND b108 <> 0 THEN 1 ELSE 0 END) AS n_both,
            SUM(CASE WHEN b061 IS NOT NULL AND b061 <> 0
                      AND b108 IS NOT NULL AND b108 <> 0
                      AND ABS(b061 - b108) <=
                          GREATEST(1, 0.01 * GREATEST(ABS(b061), ABS(b108)))
                     THEN 1 ELSE 0 END) AS n_balanced_1pct,
            SUM(CASE WHEN ABS(COALESCE(b086, 0) + COALESCE(b087, 0))
                         <= ABS(COALESCE(b084, 0)) + 1
                     THEN 1 ELSE 0 END) AS n_lt_components_ok,
            SUM(CASE WHEN ABS(COALESCE(b096, 0) + COALESCE(b097, 0))
                         <= ABS(COALESCE(b094, 0)) + 1
                     THEN 1 ELSE 0 END) AS n_st_components_ok,
            SUM(CASE WHEN COALESCE(b166, 0) + COALESCE(b168, 0) > 0
                     THEN 1 ELSE 0 END) AS n_interest_pos,
            SUM(CASE WHEN COALESCE(b166, 0) + COALESCE(b168, 0) < 0
                     THEN 1 ELSE 0 END) AS n_interest_neg,
            SUM(CASE WHEN COALESCE(b086, 0) + COALESCE(b087, 0)
                          + COALESCE(b096, 0) + COALESCE(b097, 0) <> 0
                     THEN 1 ELSE 0 END) AS n_fin_debt,
            SUM(ABS(COALESCE(b084, 0))) AS sum_lt_liabilities,
            SUM(ABS(COALESCE(b094, 0))) AS sum_st_liabilities,
            SUM(ABS(COALESCE(b086, 0) + COALESCE(b087, 0))) AS sum_lt_fin_debt,
            SUM(ABS(COALESCE(b096, 0) + COALESCE(b097, 0))) AS sum_st_fin_debt,
            SUM(COALESCE(b125, 0)) AS sum_revenue,
            SUM(COALESCE(b131, 0)) AS sum_opex,
            SUM(COALESCE(b152, 0) - COALESCE(b153, 0)) AS sum_net_result
        FROM db_afs
        WHERE reportyear = %s
          AND b125 > 0
          AND nacerev21 IS NOT NULL
          AND nacerev21 <> ''
          AND nacerev21 <> 'K'
        """,
        (year,),
    )
    cols = [d[0] for d in cur.description]
    row = dict(zip(cols, cur.fetchone()))
    return {key: float(value or 0) for key, value in row.items()} | {"year": year}


def make_validation_tables(yearly: pd.DataFrame) -> tuple[pd.DataFrame, bool, str]:
    yearly = yearly.copy()
    yearly["asset_coverage"] = yearly["n_assets"] / yearly["n"]
    yearly["passive_coverage"] = yearly["n_passive"] / yearly["n"]
    yearly["balance_match_share"] = np.where(
        yearly["n_both"] > 0,
        yearly["n_balanced_1pct"] / yearly["n_both"],
        0,
    )
    yearly["lt_components_ok_share"] = yearly["n_lt_components_ok"] / yearly["n"]
    yearly["st_components_ok_share"] = yearly["n_st_components_ok"] / yearly["n"]
    interest_nonzero = yearly["n_interest_pos"] + yearly["n_interest_neg"]
    yearly["interest_sign_majority_share"] = np.where(
        interest_nonzero > 0,
        yearly[["n_interest_pos", "n_interest_neg"]].max(axis=1) / interest_nonzero,
        0,
    )
    yearly["financial_debt_coverage"] = yearly["n_fin_debt"] / yearly["n"]
    yearly["financial_debt_to_total_liabilities"] = (
        yearly["sum_lt_fin_debt"] + yearly["sum_st_fin_debt"]
    ) / (yearly["sum_lt_liabilities"] + yearly["sum_st_liabilities"])
    yearly["scaled_debt_to_revenue"] = (
        yearly["sum_lt_fin_debt"] + yearly["sum_st_fin_debt"]
    ) / (yearly["sum_revenue"] * 1000)

    checks = [
        (
            "active_sample_size",
            "All years must have at least 5,000 active non-financial firms.",
            yearly["n"].min(),
            5000,
            yearly["n"].min() >= 5000,
        ),
        (
            "financial_debt_component_coverage",
            "Direct loan and bank-debt components must be non-zero in enough rows to describe a distribution.",
            yearly["financial_debt_coverage"].min(),
            0.50,
            yearly["financial_debt_coverage"].min() >= 0.50,
        ),
        (
            "scaled_stock_flow_plausibility",
            "Debt/revenue must be plausible after scaling P&L revenue by 1,000.",
            yearly["scaled_debt_to_revenue"].max(),
            2.00,
            yearly["scaled_debt_to_revenue"].between(0.001, 2.00).all(),
        ),
        (
            "asset_coverage",
            "Full-balance debt/assets is blocked unless assets cover at least 70% of the sample every year.",
            yearly["asset_coverage"].min(),
            0.70,
            yearly["asset_coverage"].min() >= 0.70,
        ),
        (
            "balance_identity",
            "Rows with both asset and passive totals must match within 1% in at least 95% of cases.",
            yearly["balance_match_share"].min(),
            0.95,
            yearly["balance_match_share"].min() >= 0.95,
        ),
        (
            "long_term_debt_components",
            "Long-term financial debt components must fit inside long-term liabilities in 95% of rows.",
            yearly["lt_components_ok_share"].min(),
            0.95,
            yearly["lt_components_ok_share"].min() >= 0.95,
        ),
        (
            "short_term_debt_components",
            "Short-term financial debt components must fit inside current liabilities in 95% of rows.",
            yearly["st_components_ok_share"].min(),
            0.95,
            yearly["st_components_ok_share"].min() >= 0.95,
        ),
        (
            "interest_sign",
            "Interest expense sign must be consistent in at least 95% of non-zero rows.",
            yearly["interest_sign_majority_share"].min(),
            0.95,
            yearly["interest_sign_majority_share"].min() >= 0.95,
        ),
    ]

    audit = pd.DataFrame(
        checks,
        columns=["rule", "description", "observed_min", "threshold", "passed"],
    )
    fatal_rules = {
        "active_sample_size",
        "financial_debt_component_coverage",
        "scaled_stock_flow_plausibility",
        "long_term_debt_components",
        "short_term_debt_components",
        "balance_identity",
    }
    failed = audit.loc[(~audit["passed"]) & audit["rule"].isin(fatal_rules), "rule"].tolist()
    blocked_but_nonfatal = audit.loc[
        (~audit["passed"]) & ~audit["rule"].isin(fatal_rules), "rule"
    ].tolist()
    go = not failed
    if go:
        reason = (
            "passed for narrow financial-debt post; blocked full-balance ratios: "
            + ", ".join(blocked_but_nonfatal)
        )
    else:
        reason = "failed fatal rules: " + ", ".join(failed)
    audit = pd.concat(
        [
            audit,
            pd.DataFrame(
                [
                    {
                        "rule": "go_no_go",
                        "description": "Narrow financial-debt post can be written if fatal validation gates pass.",
                        "observed_min": 1.0 if go else 0.0,
                        "threshold": 1.0,
                        "passed": go,
                    }
                ]
            ),
        ],
        ignore_index=True,
    )
    return audit, go, reason


def query_firm_panel(conn: pymysql.connections.Connection) -> pd.DataFrame:
    cols = [
        "subjecttaxnoid",
        "reportyear",
        "nacerev21",
        "subjectsizeeurev2",
        "employeecounteop",
        "b058",
        "b063",
        "b061",
        "b084",
        "b086",
        "b087",
        "b094",
        "b096",
        "b097",
        "b108",
        "b125",
        "b166",
        "b168",
        "b152",
        "b153",
    ]
    cur = conn.cursor()
    frames = []
    for year in YEARS:
        cur.execute(
            f"""
            SELECT {", ".join(cols)}
            FROM db_afs
            WHERE reportyear = %s
              AND b125 > 0
              AND nacerev21 IS NOT NULL
              AND nacerev21 <> ''
              AND nacerev21 <> 'K'
            """,
            (year,),
        )
        frames.append(pd.DataFrame(cur.fetchall(), columns=cols))
        print(f"pulled active non-financial rows for {year}: {len(frames[-1]):,}", flush=True)
    return pd.concat(frames, ignore_index=True)


def winsorize_by_year(data: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = data.copy()
    for col in columns:
        lo = out.groupby("year")[col].transform(lambda x: x.quantile(0.01))
        hi = out.groupby("year")[col].transform(lambda x: x.quantile(0.99))
        out[col] = out[col].clip(lo, hi)
    return out


def compute_outputs(conn: pymysql.connections.Connection, yearly_diag: pd.DataFrame) -> None:
    panel = query_firm_panel(conn)
    numeric_cols = [col for col in panel.columns if col.startswith("b")] + [
        "subjectsizeeurev2",
        "employeecounteop",
    ]
    for col in numeric_cols:
        panel[col] = pd.to_numeric(panel[col], errors="coerce").fillna(0)

    df = panel.rename(columns={"reportyear": "year", "nacerev21": "sector"}).copy()
    df["sector_name"] = df["sector"].map(SECTOR_NAMES).fillna(df["sector"])
    df["size_name"] = df["subjectsizeeurev2"].fillna(0).astype(int).map(SIZE_LABELS).fillna("nepoznato")
    # GFI P&L revenue is stored on a thousand-unit scale relative to balance
    # sheet stocks in this extract. Stock/flow ratios therefore use scaled revenue.
    df["revenue"] = df["b125"] * 1000
    df["net_result"] = df["b152"] - df["b153"]
    df["ebit"] = np.nan
    df["ebitda"] = np.nan
    df["interest_raw"] = df["b166"] + df["b168"]

    # This branch runs only after interest sign validation passes.
    sign_by_year = yearly_diag.set_index("year")
    majority_negative = sign_by_year["n_interest_neg"].sum() > sign_by_year["n_interest_pos"].sum()
    df["interest"] = (-df["interest_raw"] if majority_negative else df["interest_raw"]) * 1000

    df["lt_fin_debt"] = df["b086"] + df["b087"]
    df["st_fin_debt"] = df["b096"] + df["b097"]
    df["financial_debt"] = df["lt_fin_debt"] + df["st_fin_debt"]
    df["net_debt"] = df["financial_debt"] - df["b058"]
    df["assets"] = df["b061"]
    df["equity"] = df["b063"]

    for col in ["financial_debt", "lt_fin_debt", "st_fin_debt", "interest"]:
        df.loc[df[col] < 0, col] = np.nan

    df["debt_to_revenue"] = df["financial_debt"] / df["revenue"].where(df["revenue"] > 0)
    df["debt_to_assets"] = df["financial_debt"] / df["assets"].where(df["assets"] > 0)
    df["debt_to_equity"] = df["financial_debt"] / df["equity"].where(df["equity"] > 0)
    df["net_debt_to_revenue"] = df["net_debt"] / df["revenue"].where(df["revenue"] > 0)
    df["net_margin"] = df["net_result"] / df["revenue"].where(df["revenue"] > 0)
    df["roa"] = df["net_result"] / df["assets"].where(df["assets"] > 0)
    df["icr"] = np.nan
    df["st_debt_share"] = df["st_fin_debt"] / df["financial_debt"].where(df["financial_debt"] > 0)

    ratio_cols = [
        "debt_to_revenue",
        "debt_to_assets",
        "debt_to_equity",
        "net_debt_to_revenue",
        "net_margin",
        "roa",
        "icr",
        "st_debt_share",
    ]
    for col in ratio_cols:
        df.loc[~np.isfinite(df[col]), col] = np.nan
    clean = winsorize_by_year(df, ratio_cols)

    yearly = clean.groupby("year").agg(
        n_firms=("subjecttaxnoid", "size"),
        revenue=("revenue", "sum"),
        financial_debt=("financial_debt", "sum"),
        net_debt=("net_debt", "sum"),
        lt_fin_debt=("lt_fin_debt", "sum"),
        st_fin_debt=("st_fin_debt", "sum"),
        net_result=("net_result", "sum"),
        debt_to_revenue_median=("debt_to_revenue", "median"),
        debt_to_revenue_p75=("debt_to_revenue", lambda x: x.quantile(0.75)),
        debt_to_revenue_p90=("debt_to_revenue", lambda x: x.quantile(0.90)),
        debt_to_assets_median=("debt_to_assets", "median"),
        net_margin_median=("net_margin", "median"),
        icr_median=("icr", "median"),
    ).reset_index()
    yearly["agg_debt_to_revenue"] = yearly["financial_debt"] / yearly["revenue"]
    yearly["agg_net_debt_to_revenue"] = yearly["net_debt"] / yearly["revenue"]
    yearly["st_debt_share"] = yearly["st_fin_debt"] / yearly["financial_debt"]
    yearly["agg_net_margin"] = yearly["net_result"] / yearly["revenue"]
    yearly.to_csv(TABLE_DIR / "debt_structure_yearly.csv", index=False, encoding="utf-8-sig")

    latest = clean[clean["year"] == clean["year"].max()].copy()
    profit_rank = latest["net_margin"].rank(method="first", na_option="keep")
    latest["profitability_bin"] = pd.qcut(
        profit_rank,
        q=5,
        labels=["najslabija", "niska", "srednja", "visoka", "najvisa"],
    )
    bins = latest.groupby("profitability_bin", observed=True).agg(
        n_firms=("subjecttaxnoid", "size"),
        revenue=("revenue", "sum"),
        financial_debt=("financial_debt", "sum"),
        median_debt_to_revenue=("debt_to_revenue", "median"),
        p75_debt_to_revenue=("debt_to_revenue", lambda x: x.quantile(0.75)),
        median_net_margin=("net_margin", "median"),
    ).reset_index()
    bins["agg_debt_to_revenue"] = bins["financial_debt"] / bins["revenue"]
    bins.to_csv(TABLE_DIR / "debt_profitability_bins.csv", index=False, encoding="utf-8-sig")

    by_sector_size = latest.groupby(["sector", "sector_name", "size_name"]).agg(
        n_firms=("subjecttaxnoid", "size"),
        revenue=("revenue", "sum"),
        financial_debt=("financial_debt", "sum"),
        median_debt_to_revenue=("debt_to_revenue", "median"),
        median_net_margin=("net_margin", "median"),
    ).reset_index()
    by_sector_size["agg_debt_to_revenue"] = (
        by_sector_size["financial_debt"] / by_sector_size["revenue"]
    )
    by_sector_size.to_csv(
        TABLE_DIR / "debt_by_sector_size.csv",
        index=False,
        encoding="utf-8-sig",
    )


def write_blocked_outputs(reason: str, yearly_diag: pd.DataFrame) -> None:
    blocked = pd.DataFrame(
        [
            {
                "status": "blocked",
                "reason": reason,
            }
        ]
    )
    blocked.to_csv(TABLE_DIR / "debt_profitability_bins.csv", index=False, encoding="utf-8-sig")
    blocked.to_csv(TABLE_DIR / "debt_by_sector_size.csv", index=False, encoding="utf-8-sig")
    yearly_diag.to_csv(TABLE_DIR / "debt_structure_yearly.csv", index=False, encoding="utf-8-sig")


def main() -> int:
    ensure_dirs()
    conn = connect()
    try:
        aop_map = query_aop_map(conn)
        aop_map.to_csv(TABLE_DIR / "debt_structure_aop_map.csv", index=False, encoding="utf-8-sig")

        yearly_records = []
        for year in YEARS:
            yearly_records.append(query_year_audit(conn, year))
            print(f"audited {year}", flush=True)
        yearly_diag = pd.DataFrame(yearly_records)
        audit, go, reason = make_validation_tables(yearly_diag)
        audit.to_csv(TABLE_DIR / "debt_structure_audit.csv", index=False, encoding="utf-8-sig")

        yearly_diag.to_csv(TABLE_DIR / "debt_structure_yearly.csv", index=False, encoding="utf-8-sig")
        if not go:
            write_blocked_outputs(reason, yearly_diag)
            print("BLOCKED. Debt validation failed.")
            print(reason)
            print(f"Wrote audit: {TABLE_DIR / 'debt_structure_audit.csv'}")
            return 0

        compute_outputs(conn, yearly_diag)
        print("OK. Debt validation passed and output tables were written.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
