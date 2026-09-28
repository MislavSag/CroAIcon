"""Rebuild the pressure-side evidence from DZS CSVs and the Ministry workbook.

Run from the repository root. No scout output is an analytical input.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import openpyxl

import tourism_value_build as tv

SEED = 20260928
np.random.seed(SEED)
ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs/tables"
FACTS = ROOT / "outputs/facts"
LIT = ROOT / "data/raw/pressure_voice/lit"
KEY = ["county", "municipality"]
TYPES = {"Ukupno": "total", "Hoteli i sličan smještaj": "hotels",
         "Odmarališta i slični objekti za kraći odmor": "rooms",
         "Kampovi i prostor za kampiranje": "camps", "Ostali smještaj": "other"}


def read18(path: Path) -> pd.DataFrame:
    records, county, zagreb = [], None, False
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = csv.reader(f)
        next(rows)
        for place, year, month, measure, raw in rows:
            place = place.strip()
            if place == "Republika Hrvatska":
                level = "country"
            elif place == "Grad Zagreb županija":
                level, county, zagreb = "county", "Grad Zagreb", True
            elif place == "Grad Zagreb":
                level = "municipality" if zagreb else "region"
            elif place in tv.NUTS2:
                level = "region"
            elif place.endswith(" županija"):
                level, county = "county", place.removesuffix(" županija")
            else:
                level = "municipality"
            records.append((county, place, level, int(year), month,
                            " ".join(measure.split()), raw.strip(), tv.parse_value(raw)))
    return pd.DataFrame(records, columns=KEY + ["level", "year", "month", "measure", "raw", "value"])


def read_coastal(path: Path) -> pd.DataFrame:
    records, county, municipality = [], None, None
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = csv.reader(f)
        next(rows)
        for label, year, measure, kind, raw in rows:
            indent = len(label) - len(label.lstrip(" "))
            if indent == 0:
                county = label.strip().removesuffix(" županija")
            elif indent == 5:
                municipality = label.strip()
                records.append((county, municipality, int(year), measure, TYPES[kind], raw, tv.parse_value(raw)))
            elif indent != 10:
                raise ValueError(f"Unexpected coastal hierarchy indentation {indent}")
    return pd.DataFrame(records, columns=KEY + ["year", "measure", "type", "raw", "value"])


def short_name(name: str) -> str:
    if name.startswith("Kaštelir"):
        return "Kaštelir-Labinci"
    return name.split(" -")[0].strip()


def read_itr(path: Path) -> pd.DataFrame:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = []
    for r in wb["ITR_PO_JLS"].values:
        if len(r) >= 6 and isinstance(r[1], (int, float)) and isinstance(r[4], (int, float)):
            name = r[2].removeprefix("Grad ").removeprefix("Općina ")
            rows.append((r[3], name, float(r[4]), r[5]))
    wb.close()
    d = pd.DataFrame(rows, columns=["county", "display_name", "itr", "itr_category"])
    d["itr_rank"] = d.itr.rank(ascending=False, method="min").astype(int)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dzs-root", type=Path, default=tv.DZS_ROOT)
    args = ap.parse_args()
    tv.DZS_ROOT = args.dzs_root
    tv.ARRIVALS_DIR = args.dzs_root / "Dolasci i noćenja turista u komercijalnim smještajnim o"
    coastal_dir = args.dzs_root / "Turizam u primorskim gradovima i općinama"
    paths = [tv.ARRIVALS_DIR / "BS_TU19.csv", tv.ARRIVALS_DIR / "BS_TU18_2025.csv",
             coastal_dir / "BS_T02_2025.csv", coastal_dir / "BS_T04_2025.csv", LIT / "itr_2025.xlsx"]
    p = tv.read_municipality_panel()
    m = p[(p.level == "municipality") & (p.year == 2025)].rename(columns={"place": "municipality"})
    wide = m.pivot(index=KEY, columns="indicator", values="value")
    names = {"Broj stanovnika, Popis 2021.": "population_2021", "Površina, km2": "area_km2",
             "Broj stalnih postelja": "beds_2025", "Noćenja turista": "nights_2025",
             "Dolasci turista": "arrivals_2025", "Broj noćenja turista na 100 stanovnika": "dzs_nights_per_100"}
    d = wide[list(names)].rename(columns=names).copy()
    d["nights_2025_raw"] = m[m.indicator == "Noćenja turista"].set_index(KEY).value_raw
    month_all = read18(paths[1])
    mn = month_all[(month_all.level == "municipality") & (month_all.measure == "Noćenja turista - ukupno")]
    monthly = mn.pivot(index=KEY, columns="month", values="value")
    d["aug_nights_2025"] = monthly["08"]
    d["nights_per_resident_2025"] = d.nights_2025 / d.population_2021
    d["aug_tourists_per_resident_2025"] = d.aug_nights_2025 / 31 / d.population_2021
    d["beds_per_resident_2025"] = d.beds_2025 / d.population_2021
    d["nights_per_km2_2025"] = d.nights_2025 / d.area_km2
    n, b = read_coastal(paths[2]), read_coastal(paths[3])
    ns = n[(n.measure == "Noćenja") & (n.type == "total")].set_index(KEY)
    bp = b[b.measure == "Postelje"].pivot(index=KEY, columns="type", values="value")
    d["coastal_table"] = d.index.isin(ns.index)
    for kind in ["camps", "hotels", "rooms"]:
        d[f"share_beds_{kind}_2025"] = bp[kind] / bp.total
    d["rank_annual_national"] = d.nights_per_resident_2025.rank(ascending=False, method="min")
    for metric, rank in [("aug_tourists_per_resident_2025", "rank_aug_coast"),
                         ("nights_per_km2_2025", "rank_density_coast")]:
        d[rank] = d.loc[d.coastal_table, metric].rank(ascending=False, method="min")
    d = d.reset_index()
    d["display_name"] = d.municipality.map(short_name)
    itr = read_itr(paths[4])
    # DZS and Ministry use a different spelling for the same unit.
    itr["display_name"] = itr.display_name.replace({"Zagreb": "Grad Zagreb", "Sveta Nedjelja": "Sveta Nedelja"})
    d["join_name"] = d.display_name.str.casefold()
    itr["join_name"] = itr.display_name.str.casefold()
    d = d.merge(itr.drop(columns="display_name"), on=["county", "join_name"], how="left", validate="one_to_one").drop(columns="join_name")
    d["group"] = np.select([d.display_name.isin(["Split", "Dubrovnik"]),
                            d.coastal_table & d.nights_per_resident_2025.ge(400)], ["G1", "G2"], default="G3")
    d["half"] = np.select([d.group.eq("G2") & d.share_beds_camps_2025.ge(.6),
                           d.group.eq("G2") & d.share_beds_rooms_2025.ge(.5)], ["camps", "rooms"], default="mixed")
    coast, g2 = d[d.coastal_table].copy(), d[d.group == "G2"].copy()
    by = d.set_index("display_name")
    checks = []
    def check(rule, passed, detail):
        checks.append(dict(rule=rule, passed=bool(passed), detail=detail))
    err = (d.nights_per_resident_2025 * 100 - d.dzs_nights_per_100).abs()
    check("V01", err.max() <= .05 + 1e-8, f"Per-100 max error {err.max():.8f}; n={err.notna().sum()}")
    annual = d.set_index(KEY).nights_2025
    pairs = pd.concat([annual, monthly["01.-12."]], axis=1).dropna()
    sums = monthly[[f"{x:02}" for x in range(1, 13)]].sum(axis=1, min_count=12)
    complete = pd.concat([annual, sums], axis=1).dropna()
    check("V02", (pairs.iloc[:, 0] == pairs.iloc[:, 1]).all() and (complete.iloc[:, 0] == complete.iloc[:, 1]).all(),
          f"Annual pairs {len(pairs)}; complete 12-month sums {len(complete)}")
    pairs = pd.concat([annual.reindex(ns.index), ns.value], axis=1)
    check("V03", pairs.iloc[:, 0].isna().equals(pairs.iloc[:, 1].isna()) and
          (pairs.dropna().iloc[:, 0] == pairs.dropna().iloc[:, 1]).all(), f"Coastal keys {len(pairs)}, published {len(pairs.dropna())}")
    check("V04", len(d) == 556 and len(coast) == 149 and coast.aug_nights_2025.notna().sum() == 147,
          f"Municipalities {len(d)}; coastal {len(coast)}; August {coast.aug_nights_2025.notna().sum()}")
    county = "Splitsko-dalmatinska"
    county_annual = p[(p.level == "county") & (p.place == county + " županija") &
                      (p.year == 2025) & (p.indicator == "Noćenja turista")].value.item()
    residual = county_annual - d.loc[d.county == county, "nights_2025"].sum()
    pod_month = monthly.loc[(county, "Podgora")].drop(labels="01.-12.")
    puc_month = monthly.loc[(county, "Pučišća")].drop(labels="01.-12.")
    pod_low, pod_high = float(pod_month.sum()), float(residual - puc_month.sum())
    check("V05", 956000 <= pod_low <= pod_high <= 960000 and "Podgora" not in set(g2.display_name),
          f"Podgora interval [{pod_low:.0f}, {pod_high:.0f}], derived only; excluded from G2")
    expected = {"Funtana": (1, 1), "Dubrovnik": (102, 71), "Split": (129, 137)}
    check("V06", all((by.loc[k, "rank_aug_coast"], by.loc[k, "rank_annual_national"]) == v for k, v in expected.items()),
          "August coastal and annual national ranks checked")
    check("V07", len(itr) == 556 and d.itr.notna().all() and all(by.loc[k, "itr_rank"] == r for k, r in {"Funtana": 1, "Dubrovnik": 5, "Split": 44}.items())
          and g2.itr_category.isin(["I", "II"]).all(), f"ITR rows {len(itr)}, all-DZS joins {d.itr.notna().sum()}, G2 joins {g2.itr.notna().sum()}")
    check("G2_definition", len(g2) == 12 and set(g2[g2.half == "camps"].display_name) == {"Funtana", "Vrsar", "Tar-Vabriga", "Brtonigla"}
          and len(g2[g2.half == "rooms"]) == 6, "Group and accommodation halves reproduce")
    # Gazetteer follows the pre-specified rule and does not use any media result.
    band = coast[coast.population_2021.between(600, 7000) & coast.nights_per_resident_2025.notna()].copy()
    band["intensity_tercile"] = pd.qcut(band.nights_per_resident_2025, 3, labels=["low", "middle", "high"])
    ambiguous = {"Preko", "Blato", "Sveta Nedelja", "Marina", "Privlaka"}
    allowed = band[~band.display_name.isin(ambiguous)]
    selected = set(coast.nlargest(59, "nights_2025").municipality)
    selected.update(coast.loc[coast.nights_per_resident_2025.ge(350), "municipality"])
    selected.add("Podgora")
    for tier, count in [("low", 8), ("middle", 4)]:
        selected.update(allowed[allowed.intensity_tercile == tier].nlargest(count, "nights_2025").municipality)
    d["gazetteer_selected"] = d.coastal_table & d.municipality.isin(selected)
    pilot = set(g2.display_name) | {"Podgora", "Split", "Dubrovnik", "Rovinj", "Poreč", "Umag", "Hvar", "Makarska", "Baška Voda", "Zadar", "Pula"}
    d["pilot_selected"] = d.coastal_table & d.display_name.isin(pilot)
    check("pilot_count", d.pilot_selected.sum() == 23, "Frozen 23-unit pilot")
    ok = all(c["passed"] for c in checks)
    facts = dict(seed=SEED, year=2025, census_year=2021, august_days=31, group_threshold=400,
                 g0_passed=ok, media_validated=False, analysis_status="pilot_awaits_human_validation",
                 story_branch="F3_interim_not_a_media_gate_failure", g2_n_units=len(g2),
                 g2_nights_m=float(g2.nights_2025.sum()/1e6), g2_pop=int(g2.population_2021.sum()),
                 g2_nights_share=float(g2.nights_2025.sum()/coast.nights_2025.sum()*100),
                 coastal_published_nights=float(coast.nights_2025.sum()), rank_n_coast_aug=int(coast.aug_nights_2025.notna().sum()),
                 g2_aug_min=float(g2.aug_tourists_per_resident_2025.min()), g2_itr_cat_i_ii_n=int(g2.itr_category.isin(["I", "II"]).sum()),
                 gazetteer_n=int(d.gazetteer_selected.sum()), gazetteer_nights_share=float(d.loc[d.gazetteer_selected, "nights_2025"].sum()/coast.nights_2025.sum()*100),
                 podgora_derived_lower=pod_low, podgora_derived_upper=pod_high,
                 checks={c["rule"]:c["passed"] for c in checks}, gates={"G0": "pass" if ok else "fail", "A": "pending_human_labels", "G1": "pending", "G2": "pending", "G3": "pending", "G4": "pending"})
    for key, name in [("funtana", "Funtana"), ("dubrovnik", "Dubrovnik"), ("split", "Split")]:
        row = by.loc[name]
        for suffix, col in [("aug_per_res", "aug_tourists_per_resident_2025"), ("pop", "population_2021"),
                            ("npr", "nights_per_resident_2025"), ("rank_aug", "rank_aug_coast"),
                            ("itr_rank", "itr_rank"), ("camp_share", "share_beds_camps_2025"),
                            ("rooms_share", "share_beds_rooms_2025"), ("rank_density", "rank_density_coast")]:
            facts[f"{key}_{suffix}"] = float(row[col])
    TABLES.mkdir(parents=True, exist_ok=True)
    FACTS.mkdir(parents=True, exist_ok=True)
    d.to_csv(TABLES / "pressure_voice_municipality.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(checks).to_csv(TABLES / "pressure_voice_dzs_checks.csv", index=False)
    itr.to_csv(TABLES / "pressure_voice_itr.csv", index=False, encoding="utf-8-sig")
    band.to_csv(TABLES / "pressure_voice_size_band.csv", index=False, encoding="utf-8-sig")
    (FACTS / "pressure_voice.json").write_text(json.dumps(facts, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    provenance = [{"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "size_bytes": p.stat().st_size} for p in paths]
    (ROOT / "quality_reports/2026-10-pritisak-bez-glasa_sources.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    print(pd.DataFrame(checks).to_string(index=False))
    print(json.dumps({k: facts[k] for k in ["g0_passed", "g2_nights_share", "g2_pop", "gazetteer_n", "gazetteer_nights_share"]}))
    if not ok:
        raise SystemExit("G0 failed; inspect checks before using any result")


if __name__ == "__main__":
    main()
