"""Exploratory tourism-context mentions. No pressure or sentiment labels.

Only aggregate counts leave private storage. Original frozen rules and human
coding packs are read-only. Main definition fixed in the revision plan before
group results: strict tourism vocabulary, excluding flagged repeated passages.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import regex

from pressure_voice_dzs import read18
from pressure_voice_extract import verify_manifest
import tourism_value_build as tv

ROOT=Path(__file__).resolve().parents[1]
np.random.seed(20260928)
STRICT=regex.compile(
    r"(?<!\p{L})(?:turis\p{L}*|turiz\p{L}*|no[ćc]enj\p{L}*|apartman\p{L}*|"
    r"iznajmlj\p{L}*|hotel\p{L}*|kruzer\p{L}*|smje[šs]taj\p{L}*|booking|airbnb|"
    r"kamp(?:a|u|om|ovi|ova|ovima|ove|iranje|iranja|iranju|iranjem)?)"
    r"(?!\p{L})",regex.I|regex.V1)


def count_pairs(w,doc_key="canonical_doc_id",fractional=False):
    pairs=w[[doc_key,"place"]].drop_duplicates().copy()
    pairs["weight"]=1.0
    if fractional:
        pairs["weight"]=1/pairs.groupby(doc_key).place.transform("size")
        assert np.isclose(pairs.groupby(doc_key).weight.sum(),1).all()
    counts=pairs.groupby("place").weight.sum()
    return counts,len(pairs),pairs[doc_key].nunique()


def main():
    manifest=verify_manifest()
    municipality=pd.read_csv(ROOT/"outputs/tables/pressure_voice_municipality.csv")
    selected=municipality[municipality.pilot_selected].copy()
    source=tv.ARRIVALS_DIR/"BS_TU18_2025.csv"
    monthly=read18(source)
    monthly=monthly[(monthly.level=="municipality")&(monthly.measure=="Noćenja turista - ukupno")]
    months=["08"]
    wide=monthly.pivot(index=["county","municipality"],columns="month",values="value")
    period=wide[months].sum(axis=1,min_count=len(months)).rename("nights_period")
    selected=selected.merge(period,on=["county","municipality"],how="left",validate="one_to_one")
    # Same-place, same-period main comparison; no imputation of suppressed data.
    frame=selected[selected.nights_period.notna()].copy()
    excluded=sorted(set(selected.display_name)-set(frame.display_name))
    assert len(frame)==23 and excluded==[]
    assert frame.group.eq("G2").sum()==12
    for total in [frame.nights_period.sum(),frame.nights_2025.sum()]:assert total>0
    input_path=ROOT/"data/processed/pressure_voice/pilot_windows_clean.parquet"
    w=pd.read_parquet(input_path)
    w=w[w.place.isin(frame.display_name)].copy()
    w["published"]=pd.to_datetime(w.published)
    w["strict_tourism"]=w.passage.map(lambda t:bool(STRICT.search(t)))
    overlap=w[w.published.between("2025-08-01","2025-08-31")].copy()
    strict=overlap[overlap.strict_tourism]
    main_windows=strict[~strict.boilerplate_review]
    variants=[
        ("main_strict_no_repeated",main_windows,"canonical_doc_id",False),
        ("strict_keep_repeated",strict,"canonical_doc_id",False),
        ("broad_keep_repeated",overlap,"canonical_doc_id",False),
        ("broad_no_repeated",overlap[~overlap.boilerplate_review],"canonical_doc_id",False),
        ("strict_no_traffic",main_windows[~main_windows.traffic],"canonical_doc_id",False),
        ("strict_fractional_documents",main_windows,"canonical_doc_id",True),
        ("strict_without_dedup",main_windows,"doc_id",False),
        ("april_december_strict",w[w.published.lt("2026-01-01")&w.strict_tourism&~w.boilerplate_review],"canonical_doc_id",False),
        ("full_pilot_strict",w[w.strict_tourism&~w.boilerplate_review],"canonical_doc_id",False),
    ]
    unitrows=[];grouprows=[];summary=[]
    for name,windows,doc_key,fractional in variants:
        counts,pairs,documents=count_pairs(windows,doc_key,fractional)
        u=frame[["display_name","group","nights_period","nights_2025","population_2021"]].copy()
        u["mention_weight"]=u.display_name.map(counts).fillna(0)
        u["mention_share_pct"]=100*u.mention_weight/u.mention_weight.sum()
        u["nights_share_pct"]=100*u.nights_period/u.nights_period.sum()
        u["variant"]=name
        assert np.isclose(u.mention_share_pct.sum(),100)
        assert np.isclose(u.nights_share_pct.sum(),100)
        assert np.isclose(u.mention_weight.sum(),documents if fractional else pairs)
        unitrows.append(u)
        g=u.groupby("group").agg(n_units=("display_name","size"),
            mention_weight=("mention_weight","sum"),mention_share_pct=("mention_share_pct","sum"),
            nights_period=("nights_period","sum"),nights_share_pct=("nights_share_pct","sum")).reset_index()
        g["variant"]=name;grouprows.append(g)
        s=g.set_index("group")
        summary.append(dict(variant=name,windows=len(windows),document_place_pairs=pairs,
            documents=documents,g2_mention_share_pct=float(s.loc["G2","mention_share_pct"]),
            g2_nights_share_pct=float(s.loc["G2","nights_share_pct"]),
            g1_mention_share_pct=float(s.loc["G1","mention_share_pct"]),
            g1_nights_share_pct=float(s.loc["G1","nights_share_pct"]),
            aligned_dates=name not in ["full_pilot_strict","april_december_strict"],
            media_start="2025-04-01" if name in ["full_pilot_strict","april_december_strict"] else "2025-08-01",
            media_end={"full_pilot_strict":"2026-03-31","april_december_strict":"2025-12-31"}.get(name,"2025-08-31"),
            night_start="2025-08-01",night_end="2025-08-31"))
    tabledir=ROOT/"outputs/tables"
    pd.concat(unitrows).to_csv(tabledir/"pressure_voice_attention_units.csv",index=False,encoding="utf-8-sig")
    pd.concat(grouprows).to_csv(tabledir/"pressure_voice_attention_groups.csv",index=False)
    sensitivity=pd.DataFrame(summary)
    sensitivity.to_csv(tabledir/"pressure_voice_attention_checks.csv",index=False)
    primary=summary[0]
    aligned=sensitivity[sensitivity.aligned_dates]
    # Month-by-month comparisons use their own, aligned DZS denominators.
    monthlyrows=[]
    for month in months:
        sub=main_windows[main_windows.published.dt.month.eq(int(month))]
        count,pairs,docs=count_pairs(sub)
        u=frame[["county","municipality","display_name","group"]].merge(wide[[month]],on=["county","municipality"],validate="one_to_one")
        u["mention_weight"]=u.display_name.map(count).fillna(0)
        assert u[month].notna().all()
        g2=u[u.group.eq("G2")]
        monthlyrows.append(dict(month=f"2025-{month}",documents=docs,pairs=pairs,
            g2_mention_share_pct=100*g2.mention_weight.sum()/u.mention_weight.sum(),
            g2_nights_share_pct=100*g2[month].sum()/u[month].sum()))
    monthlytable=pd.DataFrame(monthlyrows)
    monthlytable.to_csv(tabledir/"pressure_voice_attention_monthly.csv",index=False)
    facts=dict(analysis="exploratory_rule_defined_mentions",source="Determ web pilot",
        pressure_classification_validated=False,place_precision_validated=False,
        public_final_claim_allowed=False,preliminary_draft_measure_allowed=True,
        frame_units=len(frame),high_intensity_units=int(frame.group.eq("G2").sum()),excluded=excluded,
        year=2025,start_month=8,end_month=8,calendar_months=1,
        window_chars=manifest["max_window_characters"],
        source_rows=int(pd.read_csv(tabledir/"pressure_voice_pilot_audit.csv").query("month == '2025-08'").n_raw.sum()),
        frame_nights=float(frame.nights_period.sum()),**primary,
        g2_mention_share_min=float(sensitivity.g2_mention_share_pct.min()),
        g2_mention_share_max=float(sensitivity.g2_mention_share_pct.max()),
        n_variants=len(variants),n_aligned_variants=len(aligned),
        aligned_g2_share_min=float(aligned.g2_mention_share_pct.min()),
        aligned_g2_share_max=float(aligned.g2_mention_share_pct.max()),
        aligned_direction_consistent=bool((aligned.g2_mention_share_pct<aligned.g2_nights_share_pct).all()),
        month_direction_passes=int((monthlytable.g2_mention_share_pct<monthlytable.g2_nights_share_pct).sum()),
        semantics="Each document counts once for each matched place; same 23 places and August 2025 for both main shares. Not a share of all Croatian articles.",
        limitations=["Rule-based place/tourism matching not yet hand validated", "Captured outlet frame, not all media or audience exposure", "23 pilot places are selected, not a representative coastal sample", "Exact dedup only; near-syndication may remain", "Mentions include promotion, business, infrastructure and events, not just resident complaints", "Main finding is an August snapshot; other months have suppressed DZS values"],
        input_sha256=hashlib.sha256(input_path.read_bytes()).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        dzs_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        frozen_manifest_version=manifest["version"])
    (ROOT/"outputs/facts/pressure_voice_attention.json").write_text(json.dumps(facts,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(sensitivity[["variant","documents","g2_mention_share_pct","g2_nights_share_pct","g1_mention_share_pct","g1_nights_share_pct"]].to_string(index=False))
    print(json.dumps({k:facts[k] for k in ["frame_units","excluded","frame_nights","source_rows","month_direction_passes"]}))


if __name__=="__main__":main()
