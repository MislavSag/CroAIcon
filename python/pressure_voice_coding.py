"""Prepare reproducible blinded local human coding packs from pilot shards.

Candidate and denominator counts here are provisional diagnostic counts.
Text-bearing files are written exclusively under data/processed/pressure_voice.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import regex

from pressure_voice_extract import PRIVATE, ROOT, MANIFEST, verify_manifest

SEED = 20260928
RNG = np.random.default_rng(SEED)


def hash_text(s):
    return hashlib.sha256(regex.sub(r"\W+", " ", s.lower()).strip().encode()).hexdigest()


def deduplicate(w):
    docs=w.drop_duplicates("doc_id").sort_values(["published","doc_id"])
    recent={};canonical={}
    for r in docs.itertuples():
        date=pd.Timestamp(r.published)
        keys=[("url",r.url_hash),("body",r.body_hash),("syndication",r.syndication_hash)]
        dup=None
        for key in keys:
            if key in recent and (date-recent[key][0]).days<=7:
                dup=recent[key][1];break
        chosen=dup or r.doc_id
        canonical[r.doc_id]=chosen
        for key in keys:
            recent[key]=(date,chosen)
    w=w.copy();w["canonical_doc_id"]=w.doc_id.map(canonical)
    # Retain a unique passage from each syndicated story. A materially different
    # place passage is preserved even if an outlet copied the title and opening.
    w["passage_hash"]=w.passage.map(hash_text)
    w=w.drop_duplicates(["canonical_doc_id","place","passage_hash"])
    w["repeated_passage_docs"]=w.groupby("passage_hash").canonical_doc_id.transform("nunique")
    w["boilerplate_review"]=w.repeated_passage_docs.ge(20)
    return w,len(docs),len(set(canonical.values()))


def draw(frame,n,task,stratum):
    if frame.empty:return []
    n=min(n,len(frame))
    chosen=RNG.choice(frame.index.to_numpy(),size=n,replace=False)
    return [dict(window_id=frame.loc[i,"window_id"],task=task,stratum=stratum,
                 population_n=len(frame),sample_n=n,inclusion_probability=n/len(frame)) for i in chosen]


def render_pack(rows,role,private_dir):
    """Standalone local UI with no network calls and text-free JSON export."""
    payload=json.dumps(rows,ensure_ascii=False).replace("<","\\u003c").replace("&","\\u0026")
    template=(ROOT/"python/templates/pressure_voice_coding.html").read_text(encoding="utf-8")
    page=template.replace("__ROWS_JSON__",payload).replace("__ROLE_JSON__",json.dumps(role))
    (private_dir/f"review_{role}.html").write_text(page,encoding="utf-8")


def prepare(allow_partial=False):
    manifest=verify_manifest()
    shards=sorted(PRIVATE.glob("pilot_????-??.duckdb"))
    expected={f"2025-{m:02}" for m in range(4,13)}|{f"2026-{m:02}" for m in range(1,4)}
    found={p.stem.removeprefix("pilot_") for p in shards}
    if found!=expected and not allow_partial:
        raise SystemExit(f"Pilot incomplete: {len(found)}/12 months. No final coding pack created.")
    frames=[];audits=[]
    for path in shards:
        con=duckdb.connect(str(path),read_only=True)
        meta=dict(con.execute("SELECT * FROM metadata").fetchall())
        if meta["manifest_sha"]!=MANIFEST.with_suffix(".sha256").read_text().strip():
            raise SystemExit("Mixed manifest hashes in pilot")
        frames.append(con.execute("SELECT * FROM windows").df());audits.append(json.loads(meta["audit"]));con.close()
    w=pd.concat(frames,ignore_index=True).drop_duplicates("window_id")
    w,raw_docs,dedup_docs=deduplicate(w)
    units=pd.read_csv(ROOT/"outputs/tables/pressure_voice_municipality.csv")
    units=units[units.pilot_selected].copy()
    assert units.display_name.is_unique, "Pilot alias keys must be unique"
    w=w.merge(units[["display_name","group","population_2021"]],left_on="place",right_on="display_name",validate="many_to_one")
    w["family_tier"]=np.where(w.families.str.contains("F1|F2|F3|F5|F6|F7",regex=True),"core","sensitivity")
    w["precision_stratum"]=np.where(w.group.eq("G1"),"G1",np.where(w.population_2021.ge(20000),"G3_large","G3_small"))+"_"+w.family_tier
    w=w.reset_index(drop=True)
    selections=[]
    cand=w[w.candidate]
    g2=cand[cand.group=="G2"]
    selections+=draw(g2,len(g2) if len(g2)<=400 else int(np.ceil(len(g2)/2)),"candidate","G2")
    rest=cand[cand.group!="G2"]
    strata=list(rest.precision_stratum.unique())
    # 400 proportionally balanced by fixed strata; unused slots redistributed.
    allocations={s:min(len(rest[rest.precision_stratum==s]),400//max(1,len(strata))) for s in strata}
    remaining=min(400,len(rest))-sum(allocations.values())
    while remaining:
        for s in sorted(strata):
            if allocations[s]<len(rest[rest.precision_stratum==s]) and remaining:
                allocations[s]+=1;remaining-=1
    for s,n in allocations.items():selections+=draw(rest[rest.precision_stratum==s],n,"candidate",s)
    neg=w[~w.candidate]
    for group in ["G2","rest"]:
        frame=neg[neg.group.eq("G2") if group=="G2" else neg.group.ne("G2")]
        high=frame.nlargest(min(100,len(frame)),"recall_score",keep="first")
        low=frame.drop(index=high.index)
        if group=="G2":
            selections+=draw(high,100,"recall","G2_high")
            selections+=draw(low,150,"recall","G2_rest")
        else:
            selections+=draw(high,75,"recall","rest_high")
            selections+=draw(low,75,"recall","rest_low")
    d=w.drop_duplicates(["canonical_doc_id","place"])
    top20=set(d.groupby("place").size().nlargest(20).index)
    named=set(units.loc[units.group=="G2","display_name"])|top20
    for place in sorted(named):selections+=draw(w[w.place==place],20,"place",place)
    selections+=draw(w[~w.place.isin(named)],200,"place","pooled_other")
    # Topic sample is document-place based, with fixed equal group allocation.
    selections+=draw(d[d.group=="G2"],150,"topic","G2")
    selections+=draw(d[d.group!="G2"],150,"topic","rest")
    sampling=pd.DataFrame(selections)
    ids=list(sampling.window_id.unique());RNG.shuffle(ids)
    lookup=w.set_index("window_id")
    roles=sampling.groupby("window_id").task.agg(lambda s:sorted(set(s)))
    # Class coding is blinded. Place attribution is a separate local audit where
    # the target must be disclosed to make correctness assessable. It never shows
    # group, intensity, population or publisher.
    primary=[]
    for wid in ids:
        tasks=roles[wid]
        if tasks == ["place"]:
            continue
        primary.append(dict(window_id=wid,passage=lookup.loc[wid,"masked_window"],tasks=tasks,
                            place_check=None))
    primary_ids=[r["window_id"] for r in primary]
    double_ids=RNG.choice(primary_ids,size=min(100,len(primary_ids)),replace=False).tolist()
    secondary=[dict(window_id=wid,passage=lookup.loc[wid,"masked_window"],tasks=["agreement"],place_check=None) for wid in double_ids]
    place_ids=sampling.loc[sampling.task=="place","window_id"].drop_duplicates().tolist();RNG.shuffle(place_ids)
    place_rows=[dict(window_id=wid,passage=lookup.loc[wid,"context"],tasks=["place_only"],place_check=lookup.loc[wid,"place"]) for wid in place_ids]
    pack=PRIVATE/("coding_pilot" if found==expected else "coding_partial")
    pack.mkdir(parents=True,exist_ok=True)
    sampling.to_csv(pack/"sampling_frame.csv",index=False)
    pd.DataFrame(primary).to_json(pack/"primary_windows.json",orient="records",force_ascii=False)
    pd.DataFrame(secondary).to_json(pack/"secondary_windows.json",orient="records",force_ascii=False)
    w.to_parquet(PRIVATE/"pilot_windows_clean.parquet",index=False)
    for role,rows in [("primary",primary),("secondary",secondary),("place",place_rows)]:render_pack(rows,role,pack)
    task_summary=sampling.groupby("task").agg(n_tasks=("window_id","size"),n_unique=("window_id","nunique")).reset_index()
    task_summary.to_csv(ROOT/"outputs/tables/pressure_voice_coding_workload.csv",index=False)
    pd.DataFrame(audits).sort_values("month").to_csv(ROOT/"outputs/tables/pressure_voice_pilot_audit.csv",index=False)
    summary=dict(months=len(found),source_rows=sum(a["n_raw"] for a in audits),raw_eligible_documents=raw_docs,
                 deduplicated_documents=dedup_docs,document_place_pairs=len(d),windows=len(w),
                 repeated_passage_review_windows=int(w.boilerplate_review.sum()),
                 primary_windows=len(primary),secondary_windows=len(secondary),place_windows=len(place_rows),
                 g2_candidate_windows=len(g2),candidate_windows=len(cand),labels_completed=0,
                 status="pending_human_validation",media_claims_allowed=False,manifest_sha=MANIFEST.with_suffix(".sha256").read_text().strip())
    (ROOT/"outputs/facts/pressure_voice_pilot.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    (pack/"README.md").write_text(
        "# Local pilot review\n\nOpen review_primary.html locally. The independent second coder opens review_secondary.html without seeing the primary labels. "
        "The author must not be the independent second coder. Use a stable coder ID. Export JSON when done, and keep it in this ignored folder. "
        "The export contains IDs and labels only. Do not send passages, screenshots or this folder to an external service.\n\n"
        "Code a only when the passage asserts tourism pressure affecting residents in the target place; b transport; c elsewhere/general; d promotion/without crowds; e other. "
        "General carrying-capacity plans (G) and construction (S) are separate sensitivity subcodes, not automatic core pressure. "
        "Use uncertain rather than guessing when the window is insufficient. The source contexts can be checked locally. "
        "review_place.html is a separate unblinded place audit; it reveals the target place but no group, size, intensity or publisher. "
        "Masking is partial because landmarks may identify places.\n\n"
        "All media estimates and Gate A remain pending. Dedup is exact/fingerprint only; residual syndication, boilerplate, outlet allowlist, language and aliases need review before v2.\n",
        encoding="utf-8")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--allow-partial",action="store_true");args=ap.parse_args();prepare(args.allow_partial)
