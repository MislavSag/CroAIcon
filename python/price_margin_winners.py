"""Combine Croatia output-price indices with GFI margin changes.

This is a diagnostic, not a causal estimate. It identifies activities where
official output prices rose, GFI net margins rose, and net results rose from
2021 to 2024.
"""

from __future__ import annotations

import json
import math
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd


YEARS = (2021, 2024)
PRICE_DATASETS = {
    "sts_inpp_m": {
        "label": "Industrial producer prices",
        "freq": "M",
        "periods": {
            2021: [f"2021-{month:02d}" for month in range(1, 13)],
            2024: [f"2024-{month:02d}" for month in range(1, 13)],
        },
        "params": {
            "geo": "HR",
            "unit": "I21",
            "indic_bt": "PRC_PRR",
            "s_adj": "NSA",
        },
    },
    "sts_sepp_q": {
        "label": "Service producer prices",
        "freq": "Q",
        "periods": {
            2021: [f"2021-Q{quarter}" for quarter in range(1, 5)],
            2024: [f"2024-Q{quarter}" for quarter in range(1, 5)],
        },
        "params": {
            "geo": "HR",
            "unit": "I21",
            "indic_bt": "PRC_PRR",
            "s_adj": "NSA",
        },
    },
}

LEVEL_TABLES = {
    "section": "sector_margin_growth_2021_2024.csv",
    "nkd2": "sector_margin_growth_nkd2_2021_2024.csv",
    "nkd3": "sector_margin_growth_nkd3_2021_2024.csv",
    "nkd4": "sector_margin_growth_nkd4_2021_2024.csv",
}


def project_root() -> Path:
    path = Path.cwd().resolve()
    for candidate in [path, *path.parents]:
        if (candidate / "_quarto.yml").exists() and (candidate / "CroAIcon.Rproj").exists():
            return candidate
    raise RuntimeError("Cannot locate CroAIcon project root.")


ROOT = project_root()
TABLE_DIR = ROOT / "outputs" / "tables"


def eurostat_url(dataset: str, params: dict[str, str | list[str]]) -> str:
    flat_params: list[tuple[str, str]] = []
    for key, value in params.items():
        if isinstance(value, list):
            flat_params.extend((key, item) for item in value)
        else:
            flat_params.append((key, value))
    query = urllib.parse.urlencode(flat_params)
    return f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}?{query}"


def fetch_json(dataset: str, params: dict[str, str | list[str]]) -> dict:
    url = eurostat_url(dataset, params)
    with urllib.request.urlopen(url, timeout=120) as response:
        return json.load(response)


def jsonstat_to_frame(data: dict) -> pd.DataFrame:
    ids = data["id"]
    sizes = data["size"]
    dimensions = data["dimension"]
    rows = []
    for flat_index, value in data.get("value", {}).items():
        index = int(flat_index)
        coords = []
        for size in reversed(sizes):
            coords.append(index % size)
            index //= size
        coords = list(reversed(coords))
        row = {"value": value}
        for dim, coord in zip(ids, coords):
            categories = dimensions[dim]["category"]["index"]
            inverse = {int(position): code for code, position in categories.items()}
            code = inverse[coord]
            row[dim] = code
            row[f"{dim}_label"] = dimensions[dim]["category"].get("label", {}).get(code, code)
        rows.append(row)
    return pd.DataFrame(rows)


def parse_nace_level(nace_code: str) -> tuple[str | None, str | None]:
    if not isinstance(nace_code, str):
        return None, None
    if "_" in nace_code or "-" in nace_code or nace_code.endswith("_STS") or nace_code.startswith("MIG"):
        return None, None
    if len(nace_code) == 1 and nace_code.isalpha():
        return "section", nace_code
    if len(nace_code) >= 3 and nace_code[0].isalpha() and nace_code[1:].isdigit():
        digits = nace_code[1:]
        if len(digits) == 2:
            return "nkd2", digits
        if len(digits) == 3:
            return "nkd3", digits
        if len(digits) == 4:
            return "nkd4", digits
    return None, None


def load_price_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_parts = []
    annual_parts = []
    for dataset, spec in PRICE_DATASETS.items():
        periods = sorted({period for values in spec["periods"].values() for period in values})
        params = dict(spec["params"])
        params["time"] = periods
        raw = jsonstat_to_frame(fetch_json(dataset, params))
        if raw.empty:
            continue
        raw["dataset"] = dataset
        raw["dataset_label"] = spec["label"]
        raw["value"] = pd.to_numeric(raw["value"], errors="coerce")
        raw["year"] = raw["time"].astype(str).str.slice(0, 4).astype(int)
        raw[["match_level", "match_code"]] = raw["nace_r2"].apply(
            lambda code: pd.Series(parse_nace_level(code))
        )
        raw_parts.append(raw)
        annual = (
            raw[raw["match_level"].notna()]
            .groupby(
                [
                    "dataset",
                    "dataset_label",
                    "nace_r2",
                    "nace_r2_label",
                    "match_level",
                    "match_code",
                    "year",
                ],
                as_index=False,
            )
            .agg(price_index=("value", "mean"), n_periods=("value", "count"))
        )
        annual_parts.append(annual)

    raw_all = pd.concat(raw_parts, ignore_index=True)
    annual_all = pd.concat(annual_parts, ignore_index=True)
    return raw_all, annual_all


def build_price_change(annual: pd.DataFrame) -> pd.DataFrame:
    wide = annual.pivot_table(
        index=["dataset", "dataset_label", "nace_r2", "nace_r2_label", "match_level", "match_code"],
        columns="year",
        values=["price_index", "n_periods"],
        aggfunc="first",
    )
    out = pd.DataFrame(index=wide.index).reset_index()
    for year in YEARS:
        out[f"price_index_{year}"] = wide[("price_index", year)].values
        out[f"price_periods_{year}"] = wide[("n_periods", year)].values
    out["price_growth_pct"] = 100 * (out["price_index_2024"] / out["price_index_2021"] - 1)
    out = out[out["price_index_2021"].notna() & out["price_index_2024"].notna()].copy()
    return out.sort_values("price_growth_pct", ascending=False)


def load_gfi_table(level: str) -> pd.DataFrame:
    df = pd.read_csv(TABLE_DIR / LEVEL_TABLES[level])
    if level == "section":
        out = df.rename(columns={"sector": "match_code", "sector_name": "activity_name"}).copy()
        out["match_level"] = "section"
    else:
        out = df.rename(columns={"nkd_code": "match_code", "nkd_name": "activity_name"}).copy()
        out["match_level"] = level
        out["match_code"] = out["match_code"].astype(str).str.zfill({"nkd2": 2, "nkd3": 3, "nkd4": 4}[level])

    out["net_result_change"] = out["net_result_2024"] - out["net_result_2021"]
    out["net_result_change_m"] = out["net_result_change"] / 1_000_000
    out["revenue_2024_m"] = out["revenue_2024"] / 1_000_000
    return out


def combine_price_and_gfi(price_change: pd.DataFrame) -> pd.DataFrame:
    gfi = pd.concat([load_gfi_table(level) for level in LEVEL_TABLES], ignore_index=True)
    merged = price_change.merge(
        gfi,
        on=["match_level", "match_code"],
        how="inner",
        suffixes=("_price", "_gfi"),
    )
    merged["price_up"] = merged["price_growth_pct"] > 0
    merged["margin_up"] = merged["margin_change_pp"] > 0
    merged["profit_up"] = merged["net_result_change"] > 0
    merged["candidate"] = merged["price_up"] & merged["margin_up"] & merged["profit_up"]

    # Transparent diagnostic score. It rewards all three ingredients, but the
    # table exposes each component so the ranking is not a black box.
    merged["price_margin_score"] = (
        merged["price_growth_pct"].clip(lower=0)
        * merged["margin_change_pp"].clip(lower=0)
        * (merged["net_result_change_m"].clip(lower=0).map(lambda value: math.log1p(value)))
    )
    return merged.sort_values("price_margin_score", ascending=False)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    raw_prices, annual_prices = load_price_data()
    price_change = build_price_change(annual_prices)
    combined = combine_price_and_gfi(price_change)

    raw_prices.to_csv(TABLE_DIR / "eurostat_hr_output_prices_raw_2021_2024.csv", index=False, encoding="utf-8-sig")
    annual_prices.to_csv(TABLE_DIR / "eurostat_hr_output_prices_annual_2021_2024.csv", index=False, encoding="utf-8-sig")
    price_change.to_csv(TABLE_DIR / "eurostat_hr_output_price_growth_2021_2024.csv", index=False, encoding="utf-8-sig")
    combined.to_csv(TABLE_DIR / "price_margin_winners_2021_2024.csv", index=False, encoding="utf-8-sig")

    cols = [
        "match_level",
        "match_code",
        "activity_name",
        "dataset",
        "price_growth_pct",
        "margin_change_pp",
        "net_result_change_m",
        "revenue_2024_m",
        "price_margin_score",
    ]
    top = combined[combined["candidate"]].head(15).copy()
    print("=== Top price-and-margin candidates ===")
    print(top[cols].to_string(index=False, formatters={
        "price_growth_pct": lambda x: f"{x:.1f}%",
        "margin_change_pp": lambda x: f"{x:+.1f} p.b.",
        "net_result_change_m": lambda x: f"{x:,.1f}",
        "revenue_2024_m": lambda x: f"{x:,.1f}",
        "price_margin_score": lambda x: f"{x:,.1f}",
    }))
    print("\nSaved outputs/tables/price_margin_winners_2021_2024.csv")


if __name__ == "__main__":
    main()
