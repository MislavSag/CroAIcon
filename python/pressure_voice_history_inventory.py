"""Inventory local tourism/media dates; exports aggregate coverage only."""
from __future__ import annotations
import json
from pathlib import Path

import duckdb
import pandas as pd

import tourism_value_build as tv
from pressure_voice_dzs import read18
from pressure_voice_extract import SOURCE

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/tables"


def main():
    selected = pd.read_csv(OUT / "pressure_voice_municipality.csv")
    selected = selected[selected.pilot_selected][["county", "municipality", "display_name", "group", "population_2021"]]
    panel = tv.read_municipality_panel()
    annual = panel[(panel.level == "municipality") & (panel.indicator == "Noćenja turista")]
    annual = annual.rename(columns={"place": "municipality", "value": "nights", "value_raw": "raw"})
    annual = selected.merge(annual[["county", "municipality", "year", "nights", "raw"]], on=["county", "municipality"], validate="one_to_many")
    annual.to_csv(OUT / "pressure_voice_history_tourism_annual.csv", index=False, encoding="utf-8-sig")
    monthly = []
    coverage = []
    for path in sorted(tv.ARRIVALS_DIR.glob("BS_TU18_*.csv")):
        table = read18(path)
        table = table[table.measure.eq("Noćenja turista - ukupno")]
        national = table[table.level.eq("country")]
        coverage.extend(national[["year", "month", "raw", "value"]].to_dict("records"))
        units = table[table.level.eq("municipality")]
        units = selected.merge(units[["county", "municipality", "year", "month", "raw", "value"]], on=["county", "municipality"], validate="one_to_many")
        monthly.append(units.rename(columns={"value": "nights"}))
    monthly = pd.concat(monthly, ignore_index=True)
    monthly.to_csv(OUT / "pressure_voice_history_tourism_monthly.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(coverage).to_csv(OUT / "pressure_voice_history_tourism_coverage.csv", index=False)
    print("ANNUAL", annual.groupby("year").agg(units=("nights", "size"), available=("nights", "count")).to_json())
    print("ANNUAL UNAVAILABLE", annual[annual.nights.isna()][["display_name", "year", "raw"]].to_json(orient="records"))
    print("LATEST TOURISM", pd.DataFrame(coverage).tail(13).to_json(orient="records"))
    recent = monthly[monthly.year.eq(monthly.year.max())]
    print("LATEST MUNICIPAL AVAILABILITY", recent.groupby("month").agg(available=("nights", "count"), total=("nights", "sum")).to_json())
    con = duckdb.connect(str(SOURCE), read_only=True)
    con.execute("SET threads=2")
    con.execute("SET memory_limit='2GB'")
    media = con.execute("""SELECT strftime(DATETIME, '%Y-%m') AS month,
        SOURCE_BATCH AS batch, count(*) AS records,
        min(CAST(DATETIME AS DATE)) AS first_day, max(CAST(DATETIME AS DATE)) AS last_day,
        count(DISTINCT CAST(DATETIME AS DATE)) AS days
        FROM media_data_all WHERE SOURCE_TYPE='web' GROUP BY 1,2 ORDER BY 1,2""").df()
    con.close()
    media.to_csv(OUT / "pressure_voice_history_media_coverage.csv", index=False)
    print("MEDIA", media.groupby("batch").agg(first=("month", "min"), last=("month", "max"), records=("records", "sum")).to_json())
    print("LATEST MEDIA", media.tail(2).to_json(orient="records", date_format="iso"))
    print("SOURCE", json.dumps({"size": SOURCE.stat().st_size, "mtime_ns": SOURCE.stat().st_mtime_ns}))


if __name__ == "__main__":
    main()
