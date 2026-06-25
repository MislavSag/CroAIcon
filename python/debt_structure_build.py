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
    "b002": 2,
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
    "b110": 110,
    "b152": 152,
    "b153": 153,
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
    columns = sorted(AOP_COLUMNS)
    placeholders = ", ".join(["%s"] * len(columns))
    cur = conn.cursor()
    cur.execute(
        f"""
        SELECT
            db_column AS column_name,
            aop_number AS aop,
            position_id,
            report_label,
            position_label AS label_hr,
            position_label_language,
            source_file AS source
        FROM codes_gfi_db_afs_physical
        WHERE db_column IN ({placeholders})
        ORDER BY aop_number
        """,
        columns,
    )
    rows = cur.fetchall()
    aop_map = pd.DataFrame(
        rows,
        columns=[
            "column_name",
            "aop",
            "position_id",
            "report_label",
            "label_hr",
            "position_label_language",
            "source",
        ],
    )
    missing = sorted(set(columns).difference(aop_map["column_name"]))
    if missing:
        raise RuntimeError(
            "Missing physical db_afs codebook rows in "
            f"`codes_gfi_db_afs_physical`: {', '.join(missing)}"
        )
    return aop_map


def query_year_audit(conn: pymysql.connections.Connection, year: int) -> dict[str, float]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            COUNT(*) AS n,
            SUM(CASE WHEN b002 IS NOT NULL THEN 1 ELSE 0 END) AS n_fixed_assets,
            SUM(CASE WHEN b002 IS NOT NULL AND b002 >= 0 THEN 1 ELSE 0 END) AS n_fixed_assets_nonnegative,
            SUM(CASE WHEN b002 IS NOT NULL
                      AND b061 IS NOT NULL
                      AND b002 >= 0
                      AND b002 <= b061 + 1
                     THEN 1 ELSE 0 END) AS n_fixed_assets_inside_assets,
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
            SUM(CASE WHEN COALESCE(b086, 0) + COALESCE(b087, 0)
                          + COALESCE(b096, 0) + COALESCE(b097, 0) <> 0
                     THEN 1 ELSE 0 END) AS n_fin_debt,
            SUM(ABS(COALESCE(b084, 0))) AS sum_lt_liabilities,
            SUM(ABS(COALESCE(b094, 0))) AS sum_st_liabilities,
            SUM(ABS(COALESCE(b086, 0) + COALESCE(b087, 0))) AS sum_lt_fin_debt,
            SUM(ABS(COALESCE(b096, 0) + COALESCE(b097, 0))) AS sum_st_fin_debt,
            SUM(COALESCE(b002, 0)) AS sum_fixed_assets,
            SUM(COALESCE(b061, 0)) AS sum_assets,
            SUM(COALESCE(b110, 0)) AS sum_revenue,
            SUM(COALESCE(b152, 0) - COALESCE(b153, 0)) AS sum_net_result
        FROM db_afs
        WHERE reportyear = %s
          AND b110 > 0
          AND nacerev21 IN (
              'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
              'J', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S'
          )
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
    yearly["fixed_asset_coverage"] = yearly["n_fixed_assets"] / yearly["n"]
    yearly["fixed_asset_nonnegative_share"] = np.where(
        yearly["n_fixed_assets"] > 0,
        yearly["n_fixed_assets_nonnegative"] / yearly["n_fixed_assets"],
        0,
    )
    yearly["fixed_asset_inside_assets_share"] = np.where(
        yearly["n_fixed_assets"] > 0,
        yearly["n_fixed_assets_inside_assets"] / yearly["n_fixed_assets"],
        0,
    )
    yearly["fixed_assets_to_assets"] = yearly["sum_fixed_assets"] / yearly["sum_assets"]
    yearly["balance_match_share"] = np.where(
        yearly["n_both"] > 0,
        yearly["n_balanced_1pct"] / yearly["n_both"],
        0,
    )
    yearly["lt_components_ok_share"] = yearly["n_lt_components_ok"] / yearly["n"]
    yearly["st_components_ok_share"] = yearly["n_st_components_ok"] / yearly["n"]
    yearly["financial_debt_coverage"] = yearly["n_fin_debt"] / yearly["n"]
    yearly["financial_debt_to_total_liabilities"] = (
        yearly["sum_lt_fin_debt"] + yearly["sum_st_fin_debt"]
    ) / (yearly["sum_lt_liabilities"] + yearly["sum_st_liabilities"])
    yearly["debt_to_revenue"] = (
        yearly["sum_lt_fin_debt"] + yearly["sum_st_fin_debt"]
    ) / yearly["sum_revenue"]

    checks = [
        (
            "active_sample_size",
            "All years must have at least 5,000 active non-financial firms.",
            yearly["n"].min(),
            5000,
            yearly["n"].min() >= 5000,
        ),
        (
            "fixed_asset_coverage",
            "Fixed assets b002 must be present for at least 70% of active non-financial firms.",
            yearly["fixed_asset_coverage"].min(),
            0.70,
            yearly["fixed_asset_coverage"].min() >= 0.70,
        ),
        (
            "fixed_asset_nonnegative",
            "Fixed assets b002 must be non-negative in at least 99% of covered rows.",
            yearly["fixed_asset_nonnegative_share"].min(),
            0.99,
            yearly["fixed_asset_nonnegative_share"].min() >= 0.99,
        ),
        (
            "fixed_asset_inside_assets",
            "Fixed assets b002 must fit inside total assets b061 in at least 95% of covered rows.",
            yearly["fixed_asset_inside_assets_share"].min(),
            0.95,
            yearly["fixed_asset_inside_assets_share"].min() >= 0.95,
        ),
        (
            "financial_debt_component_coverage",
            "Share of firms with non-zero direct loan and bank-debt components.",
            yearly["financial_debt_coverage"].min(),
            0.00,
            yearly["financial_debt_coverage"].min() > 0.00,
        ),
        (
            "stock_flow_plausibility",
            "Debt/revenue must be plausible using the physical db_afs revenue column b110.",
            yearly["debt_to_revenue"].max(),
            2.00,
            yearly["debt_to_revenue"].between(0.001, 2.00).all(),
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
    ]

    audit = pd.DataFrame(
        checks,
        columns=["rule", "description", "observed_min", "threshold", "passed"],
    )
    fatal_rules = {
        "active_sample_size",
        "stock_flow_plausibility",
        "fixed_asset_coverage",
        "fixed_asset_nonnegative",
        "fixed_asset_inside_assets",
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
        "b002",
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
        "b110",
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
              AND b110 > 0
              AND nacerev21 IN (
                  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                  'J', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S'
              )
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


DEBT_BIN_LABELS = ["0%", "0-10%", "10-50%", "50-100%", ">100%"]


def assign_debt_bins(values: pd.Series) -> pd.Series:
    return pd.cut(
        values.fillna(0),
        bins=[-np.inf, 0, 0.10, 0.50, 1.00, np.inf],
        labels=DEBT_BIN_LABELS,
        include_lowest=True,
    )


def add_profit_groups(data: pd.DataFrame) -> pd.DataFrame:
    out = data.copy()
    out["profit_group"] = pd.NA
    labels = ["slaba marza", "srednja marza", "jaka marza"]
    for _, idx in out.groupby("year").groups.items():
        margin = out.loc[idx, "lag_net_margin"]
        ok = margin.notna()
        if ok.sum() < 3:
            continue
        ranks = margin.loc[ok].rank(method="first")
        out.loc[ranks.index, "profit_group"] = pd.qcut(ranks, q=3, labels=labels).astype(str)
    return out


def aggregate_investment(data: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    grouped = data.groupby(group_cols, observed=True).agg(
        n_obs=("subjecttaxnoid", "size"),
        n_firms=("subjecttaxnoid", "nunique"),
        revenue=("revenue", "sum"),
        lag_fixed_assets=("lag_fixed_assets", "sum"),
        delta_fixed_assets=("delta_fixed_assets", "sum"),
        median_investment_rate=("investment_rate", "median"),
        p25_investment_rate=("investment_rate", lambda x: x.quantile(0.25)),
        p75_investment_rate=("investment_rate", lambda x: x.quantile(0.75)),
        median_lag_debt_to_revenue=("lag_debt_to_revenue", "median"),
        median_lag_net_margin=("lag_net_margin", "median"),
        median_lag_st_debt_share=("lag_st_debt_share", "median"),
    ).reset_index()
    grouped["agg_investment_rate"] = grouped["delta_fixed_assets"] / grouped["lag_fixed_assets"]
    return grouped


def make_investment_panel(clean: pd.DataFrame) -> pd.DataFrame:
    base = clean.sort_values(["subjecttaxnoid", "year"]).copy()
    group = base.groupby("subjecttaxnoid", sort=False)
    lag_cols = [
        "year",
        "fixed_assets",
        "financial_debt",
        "debt_to_revenue",
        "debt_to_assets",
        "net_margin",
        "st_debt_share",
        "revenue",
        "assets",
    ]
    for col in lag_cols:
        base[f"lag_{col}"] = group[col].shift(1)

    consecutive = base["year"].eq(base["lag_year"] + 1)
    valid = (
        consecutive
        & base["fixed_assets"].notna()
        & base["lag_fixed_assets"].notna()
        & (base["fixed_assets"] >= 0)
        & (base["lag_fixed_assets"] > 0)
    )
    inv = base.loc[valid].copy()
    inv["delta_fixed_assets"] = inv["fixed_assets"] - inv["lag_fixed_assets"]
    inv["investment_rate"] = inv["delta_fixed_assets"] / inv["lag_fixed_assets"]
    inv.loc[~np.isfinite(inv["investment_rate"]), "investment_rate"] = np.nan
    inv = inv[inv["investment_rate"].notna()].copy()
    inv = winsorize_by_year(inv, ["investment_rate"])
    inv["debt_bin"] = assign_debt_bins(inv["lag_debt_to_revenue"])
    inv["debt_bin_order"] = inv["debt_bin"].astype(str).map(
        {label: i for i, label in enumerate(DEBT_BIN_LABELS)}
    )
    inv = add_profit_groups(inv)
    return inv


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
    df["revenue"] = df["b110"]
    df["net_result"] = df["b152"] - df["b153"]
    df["ebit"] = np.nan
    df["ebitda"] = np.nan
    df["interest"] = np.nan

    df["lt_fin_debt"] = df["b086"] + df["b087"]
    df["st_fin_debt"] = df["b096"] + df["b097"]
    df["financial_debt"] = df["lt_fin_debt"] + df["st_fin_debt"]
    df["net_debt"] = df["financial_debt"] - df["b058"]
    df["assets"] = df["b061"]
    df["equity"] = df["b063"]
    df["fixed_assets"] = df["b002"]

    for col in ["financial_debt", "lt_fin_debt", "st_fin_debt", "interest", "fixed_assets"]:
        df.loc[df[col] < 0, col] = np.nan

    df["debt_to_revenue"] = df["financial_debt"] / df["revenue"].where(df["revenue"] > 0)
    df["debt_to_assets"] = df["financial_debt"] / df["assets"].where(df["assets"] > 0)
    df["debt_to_equity"] = df["financial_debt"] / df["equity"].where(df["equity"] > 0)
    df["net_debt_to_revenue"] = df["net_debt"] / df["revenue"].where(df["revenue"] > 0)
    df["fixed_assets_to_revenue"] = df["fixed_assets"] / df["revenue"].where(df["revenue"] > 0)
    df["fixed_assets_to_assets"] = df["fixed_assets"] / df["assets"].where(df["assets"] > 0)
    df["net_margin"] = df["net_result"] / df["revenue"].where(df["revenue"] > 0)
    df["roa"] = df["net_result"] / df["assets"].where(df["assets"] > 0)
    df["icr"] = np.nan
    df["st_debt_share"] = df["st_fin_debt"] / df["financial_debt"].where(df["financial_debt"] > 0)

    ratio_cols = [
        "debt_to_revenue",
        "debt_to_assets",
        "debt_to_equity",
        "net_debt_to_revenue",
        "fixed_assets_to_revenue",
        "fixed_assets_to_assets",
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
        fixed_assets=("fixed_assets", "sum"),
        net_result=("net_result", "sum"),
        debt_to_revenue_median=("debt_to_revenue", "median"),
        debt_to_revenue_p75=("debt_to_revenue", lambda x: x.quantile(0.75)),
        debt_to_revenue_p90=("debt_to_revenue", lambda x: x.quantile(0.90)),
        debt_to_assets_median=("debt_to_assets", "median"),
        fixed_assets_to_revenue_median=("fixed_assets_to_revenue", "median"),
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

    by_sector_detail = latest.groupby(["sector", "sector_name"]).agg(
        n_firms=("subjecttaxnoid", "size"),
        revenue=("revenue", "sum"),
        financial_debt=("financial_debt", "sum"),
        lt_fin_debt=("lt_fin_debt", "sum"),
        st_fin_debt=("st_fin_debt", "sum"),
        cash=("b058", "sum"),
        assets=("assets", "sum"),
        fixed_assets=("fixed_assets", "sum"),
        equity=("equity", "sum"),
        net_result=("net_result", "sum"),
        debt_firm_share=("financial_debt", lambda x: (x > 0).mean()),
        median_debt_to_revenue=("debt_to_revenue", "median"),
        p75_debt_to_revenue=("debt_to_revenue", lambda x: x.quantile(0.75)),
        p90_debt_to_revenue=("debt_to_revenue", lambda x: x.quantile(0.90)),
        median_debt_to_assets=("debt_to_assets", "median"),
        median_fixed_assets_to_revenue=("fixed_assets_to_revenue", "median"),
        median_fixed_assets_to_assets=("fixed_assets_to_assets", "median"),
        median_net_margin=("net_margin", "median"),
    ).reset_index()
    by_sector_detail["debt_to_revenue"] = (
        by_sector_detail["financial_debt"] / by_sector_detail["revenue"]
    )
    by_sector_detail["lt_debt_to_revenue"] = by_sector_detail["lt_fin_debt"] / by_sector_detail["revenue"]
    by_sector_detail["st_debt_to_revenue"] = by_sector_detail["st_fin_debt"] / by_sector_detail["revenue"]
    by_sector_detail["debt_to_assets"] = by_sector_detail["financial_debt"] / by_sector_detail["assets"]
    by_sector_detail["fixed_assets_to_revenue"] = by_sector_detail["fixed_assets"] / by_sector_detail["revenue"]
    by_sector_detail["fixed_assets_to_assets"] = by_sector_detail["fixed_assets"] / by_sector_detail["assets"]
    by_sector_detail["st_debt_share"] = (
        by_sector_detail["st_fin_debt"] / by_sector_detail["financial_debt"]
    )
    by_sector_detail["share_total_debt"] = (
        by_sector_detail["financial_debt"] / by_sector_detail["financial_debt"].sum()
    )
    by_sector_detail = by_sector_detail.sort_values("debt_to_revenue", ascending=False)
    by_sector_detail.to_csv(
        TABLE_DIR / "debt_by_sector_detail.csv",
        index=False,
        encoding="utf-8-sig",
    )

    inv = make_investment_panel(clean)
    inv_sector_all = aggregate_investment(inv, ["sector", "sector_name"])
    inv_sector_all["period"] = f"{min(YEARS) + 1}-{max(YEARS)}"
    inv_sector_latest = aggregate_investment(
        inv[inv["year"] == inv["year"].max()],
        ["sector", "sector_name"],
    )
    inv_sector_latest["period"] = str(int(inv["year"].max()))
    pd.concat([inv_sector_latest, inv_sector_all], ignore_index=True).to_csv(
        TABLE_DIR / "debt_investment_by_sector.csv",
        index=False,
        encoding="utf-8-sig",
    )

    frictions = aggregate_investment(inv, ["debt_bin", "debt_bin_order"])
    frictions = frictions.sort_values("debt_bin_order")
    frictions.to_csv(
        TABLE_DIR / "debt_financial_frictions_bins.csv",
        index=False,
        encoding="utf-8-sig",
    )

    literature = aggregate_investment(
        inv[inv["profit_group"].notna()],
        ["profit_group", "debt_bin", "debt_bin_order"],
    )
    literature = literature.sort_values(["profit_group", "debt_bin_order"])
    literature.to_csv(
        TABLE_DIR / "debt_literature_current.csv",
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
    blocked.to_csv(TABLE_DIR / "debt_by_sector_detail.csv", index=False, encoding="utf-8-sig")
    blocked.to_csv(TABLE_DIR / "debt_investment_by_sector.csv", index=False, encoding="utf-8-sig")
    blocked.to_csv(TABLE_DIR / "debt_financial_frictions_bins.csv", index=False, encoding="utf-8-sig")
    blocked.to_csv(TABLE_DIR / "debt_literature_current.csv", index=False, encoding="utf-8-sig")
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
