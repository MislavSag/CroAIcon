"""Build aligned annual and latest-YTD tourism/media comparisons from all shards."""
from __future__ import annotations

import calendar
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from pressure_voice_history_extract import ROOT, RUN

SEED = 20260928
np.random.seed(SEED)
OUT = ROOT / "outputs/tables"


def deduplicate_hashes(w):
    w = w.copy()
    w["published"] = pd.to_datetime(w.published)
    docs = w.drop_duplicates("doc_id").sort_values(["published", "doc_id"])
    recent, canonical, dates = {}, {}, {}
    empty_body = hashlib.sha256(b"").hexdigest()
    for row in docs.itertuples():
        keys = [("url", row.url_hash), ("syndication", row.syndication_hash)]
        if row.body_hash != empty_body:
            keys.append(("body", row.body_hash))
        chosen = row.doc_id
        for key in keys:
            if key in recent and (row.published - recent[key][0]).days <= 7:
                chosen = recent[key][1]
                break
        canonical[row.doc_id] = chosen
        dates.setdefault(chosen, row.published)
        for key in keys:
            recent[key] = (row.published, chosen)
    w["canonical_doc_id"] = w.doc_id.map(canonical)
    w["published"] = w.canonical_doc_id.map(dates)
    w["year"] = w.published.dt.year
    w = w.drop_duplicates(["canonical_doc_id", "place", "passage_hash"])
    w["repeated_passage_docs"] = w.groupby(["year", "passage_hash"]).canonical_doc_id.transform("nunique")
    w["repeated"] = w.repeated_passage_docs.ge(20)
    return w


def balanced_names(table, years, expected_months=None):
    selected = table[table.year.isin(years)]
    if expected_months is None:
        counts = selected.groupby("display_name").nights.count()
        expected = len(years)
    else:
        selected = selected[selected.month.isin(expected_months)]
        assert not selected.duplicated(["display_name", "year", "month"]).any()
        counts = selected.groupby("display_name").nights.count()
        expected = len(years) * len(expected_months)
    return sorted(counts[counts.eq(expected)].index)


def latest_observed_month(coverage, year):
    observed = coverage[coverage.year.eq(year) & coverage.month.str.fullmatch(r"\d{2}") & coverage.value.gt(0)]
    if observed.empty:
        raise ValueError(f"No observed national tourism month in {year}")
    return int(observed.month.max())


def period_table(w, tourism, start, end, period, variant):
    assert tourism.display_name.is_unique
    assert tourism.nights.notna().all()
    mentions = w[w.published.between(pd.Timestamp(start), pd.Timestamp(end)) & w.place.isin(tourism.display_name)]
    pairs = mentions.drop_duplicates(["canonical_doc_id", "place"])
    unit = tourism[["display_name", "group", "population_2021", "nights"]].copy()
    unit["mentions"] = unit.display_name.map(pairs.groupby("place").size()).fillna(0).astype(int)
    unit["nights_share_pct"] = 100 * unit.nights / unit.nights.sum()
    unit["mention_share_pct"] = 100 * unit.mentions / unit.mentions.sum()
    unit["period"], unit["variant"] = period, variant
    unit["start"], unit["end"] = start, end
    group = unit.groupby("group").agg(n_units=("display_name", "size"), nights=("nights", "sum"), mentions=("mentions", "sum"), nights_share_pct=("nights_share_pct", "sum"), mention_share_pct=("mention_share_pct", "sum")).reset_index()
    group["period"], group["variant"] = period, variant
    group["start"], group["end"] = start, end
    group["documents"] = pairs.canonical_doc_id.nunique()
    group["frame_units"] = len(unit)
    assert np.isclose(group.nights_share_pct.sum(), 100)
    assert np.isclose(group.mention_share_pct.sum(), 100)
    assert unit.mentions.sum() == len(pairs)
    return unit, group


def main():
    coverage = pd.read_csv(OUT / "pressure_voice_history_media_coverage.csv")
    required = set(coverage.month)
    found = {p.stem.removeprefix("mentions_") for p in RUN.glob("mentions_????-??.parquet")}
    assert found == required, f"Historical extraction incomplete: {len(found)} of {len(required)} months"
    shards = [RUN / f"mentions_{month}.parquet" for month in sorted(required)]
    raw = pd.concat([pd.read_parquet(path) for path in shards], ignore_index=True)
    windows = deduplicate_hashes(raw)
    windows.to_parquet(RUN / "windows_hashed_clean.parquet", index=False)
    annual = pd.read_csv(OUT / "pressure_voice_history_tourism_annual.csv")
    monthly = pd.read_csv(OUT / "pressure_voice_history_tourism_monthly.csv", dtype={"month": str})
    tourism_coverage = pd.read_csv(OUT / "pressure_voice_history_tourism_coverage.csv", dtype={"month": str})
    years = sorted(annual.year.unique().tolist())
    annual_names = balanced_names(annual, years)
    assert len(annual_names) == 22 and "Podgora" not in annual_names
    annual_check = annual[annual.display_name.isin(annual_names)].merge(
        monthly[monthly.month.eq("01.-12.")][["display_name", "year", "nights"]],
        on=["display_name", "year"], validate="one_to_one", suffixes=("_annual", "_monthly_table"))
    assert len(annual_check) == len(annual_names) * len(years)
    assert annual_check.nights_annual.equals(annual_check.nights_monthly_table)
    latest_year = int(tourism_coverage.year.max())
    latest_month = latest_observed_month(tourism_coverage, latest_year)
    ytd_years = [latest_year - 2, latest_year - 1, latest_year]
    ytd_months = [f"{month:02}" for month in range(1, latest_month + 1)]
    ytd_names = balanced_names(monthly, ytd_years, ytd_months)
    assert len(ytd_names) == 13
    eligible = windows[~windows.repeated]
    # Publisher intersection is a sensitivity calculation, not a changed main frame.
    publishers = eligible[eligible.year.isin(years)].groupby("domain").year.nunique()
    stable = set(publishers[publishers.eq(len(years))].index)
    variants = {"main": eligible, "keep_repeated": windows, "no_traffic": eligible[~eligible.traffic],
                "common_publishers": eligible[eligible.domain.isin(stable)]}
    units, groups = [], []
    for variant, frame in variants.items():
        for year in years:
            tourism = annual[annual.year.eq(year) & annual.display_name.isin(annual_names)]
            unit, group = period_table(frame, tourism, f"{year}-01-01", f"{year}-12-31", str(year), variant)
            units.append(unit); groups.append(group)
        for year in ytd_years:
            tourism = monthly[monthly.year.eq(year) & monthly.month.isin(ytd_months) & monthly.display_name.isin(ytd_names)]
            assert tourism.nights.notna().all()
            tourism = tourism.groupby(["display_name", "group", "population_2021"], as_index=False).nights.sum(min_count=latest_month)
            end = f"{year}-{latest_month:02}-{calendar.monthrange(year, latest_month)[1]}"
            unit, group = period_table(frame, tourism, f"{year}-01-01", end, f"{year}_ytd", variant)
            units.append(unit); groups.append(group)
    units, groups = pd.concat(units, ignore_index=True), pd.concat(groups, ignore_index=True)
    units.to_csv(OUT / "pressure_voice_history_units.csv", index=False, encoding="utf-8-sig")
    groups.to_csv(OUT / "pressure_voice_history_groups.csv", index=False)
    # Archive-wide monthly aggregates retain even the latest partial media month.
    pairs = eligible.drop_duplicates(["canonical_doc_id", "place"]).copy()
    pairs["month"] = pairs.published.dt.strftime("%Y-%m")
    counts = pairs.groupby(["month", "place"]).size().rename("mentions").reset_index()
    counts.to_csv(OUT / "pressure_voice_history_media_monthly.csv", index=False, encoding="utf-8-sig")
    audits = [json.loads((RUN / f"audit_{month}.json").read_text()) for month in sorted(required)]
    pd.DataFrame(audits).to_csv(OUT / "pressure_voice_history_extraction.csv", index=False)
    main = groups[groups.variant.eq("main")]
    annual_main = main[main.period.isin([str(y) for y in years])]
    g2 = annual_main[annual_main.group.eq("G2")]
    g1 = annual_main[annual_main.group.eq("G1")]
    latest = units[units.variant.eq("main") & units.period.eq(str(max(years)))].copy()
    latest["nights_per_resident"] = latest.nights / latest.population_2021
    latest.to_csv(OUT / "pressure_voice_history_latest_annual.csv", index=False, encoding="utf-8-sig")
    facts = {
        "seed": SEED, "start_year": min(years), "end_year": max(years), "n_years": len(years),
        "annual_frame_n": len(annual_names), "annual_frame": annual_names,
        "high_intensity_n": int(latest.group.eq("G2").sum()),
        "high_intensity_population": int(latest[latest.group.eq("G2")].population_2021.sum()),
        "annual_group_threshold": 400, "census_year": 2021,
        "ytd_years": ytd_years, "ytd_year": latest_year, "ytd_end_month": latest_month,
        "ytd_frame_n": len(ytd_names), "ytd_frame": ytd_names,
        "media_first": str(coverage.first_day.min()), "media_last": str(coverage.last_day.max()),
        "media_months": len(required), "source_web_records": int(coverage.records.sum()),
        "raw_matched_documents": int(raw.doc_id.nunique()),
        "deduplicated_matched_documents": int(eligible.canonical_doc_id.nunique()),
        "archive_mention_pairs": len(pairs), "stable_publishers_n": len(stable),
        "g2_nights_share_min": float(g2.nights_share_pct.min()), "g2_nights_share_max": float(g2.nights_share_pct.max()),
        "g2_mentions_share_min": float(g2.mention_share_pct.min()), "g2_mentions_share_max": float(g2.mention_share_pct.max()),
        "annual_g2_direction_consistent": bool(g2.nights_share_pct.gt(g2.mention_share_pct).all()),
        "annual_g1_direction_consistent": bool(g1.mention_share_pct.gt(g1.nights_share_pct).all()),
        "annual_years": years,
        "group_values": main.to_dict("records"),
        "latest_place_values": latest.to_dict("records"),
        "aligned_dates_and_geographies": True,
        "source_regimes": {"2021-2023": "luka_opce", "2024-2026": "mediaspace_full"},
        "annual_tourism_tables_agree": True,
        "tourism_input_sha256": {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in [
            "pressure_voice_history_tourism_annual.csv", "pressure_voice_history_tourism_monthly.csv"]},
        "provenance": json.loads((RUN / "manifest.json").read_text()),
    }
    path = ROOT / "outputs/facts/pressure_voice_history.json"
    path.write_text(json.dumps(facts, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(main[["period", "group", "frame_units", "nights_share_pct", "mention_share_pct", "documents"]].to_string(index=False))
    print(json.dumps({k: facts[k] for k in ["annual_frame_n", "ytd_frame_n", "media_months", "source_web_records", "raw_matched_documents"]}))


if __name__ == "__main__":
    main()
