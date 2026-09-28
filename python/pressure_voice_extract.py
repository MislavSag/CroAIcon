"""Local-only pilot extraction; no vendor text is printed or exported publicly.

Frozen rules create a human validation workload, not final media estimates.
Read-only input DB; resumable monthly private DuckDB shards. Confirmatory
extraction intentionally is not implemented before Gate A can be assessed.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import time
from urllib.parse import urlsplit

import duckdb
import pandas as pd
import regex
import xlrd

import pressure_voice_lexicon as lex

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "data/processed/pressure_voice"
MANIFEST = ROOT / "data/reference/pressure_voice_manifest_v1.json"
SOURCE = Path("C:/Users/lsikic/Luka C/DetermDB/determDB_merged.duckdb")
SEED = 20260928
NATIONAL = {"index.hr", "24sata.hr", "jutarnji.hr", "vecernji.hr", "tportal.hr", "dnevnik.hr", "net.hr",
            "hrt.hr", "vijesti.hrt.hr", "n1info.hr", "hr.n1info.com", "rtl.hr", "novilist.hr", "slobodnadalmacija.hr",
            "glasistre.hr", "dalmacijadanas.hr", "dalmatinskiportal.hr", "dubrovackidnevnik.net.hr", "dubrovackidnevnik.hr",
            "dubrovniknet.hr", "porestina.info", "parentium.com", "istrain.hr", "regionalexpress.hr", "zadarskilist.novilist.hr"}
AGGREGATORS = {"naslovi.net", "hrvatska-danas.com", "vijesti.hrs", "novine.hr", "klik.hr", "najnovijevijesti.net", "crovijesti.com"}
SQL_PLACES = r"funtan|vrsar|vabrig|lopar|ba[šs]k|novalj|zr[ćc]|povljan|brtonigl|tu[čc]ep|nin|brel|medulin|premantur|banjol|kamenjak|podgor|split|dubrov|stradun|rovinj|pore[čc]|umag|uma[šs]k|hvar|makar|zadar|zadra|zadru|zadrom|zadarsk|zadran|pula|pule|puli|pulu|pulom|pulsk|puljan"


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def domain(url):
    try:
        return (urlsplit(url if "://" in url else "https://"+url).hostname or "").lower().removeprefix("www.")
    except ValueError:
        return ""


def allowlist():
    path=ROOT/"data/raw/aem/PopisMedijskihUslugaEP_2026-09-18.xls"
    sheet=xlrd.open_workbook(str(path),encoding_override="cp1250").sheet_by_name("RPT022")
    col=sheet.row_values(3).index("Web")
    domains=set(NATIONAL)
    for i in range(4,sheet.nrows):
        val=str(sheet.cell_value(i,col)).strip()
        if val:
            domains.add(domain(val.split()[0]))
    return sorted(domains-{ "" })


def freeze():
    if MANIFEST.exists():
        verify_manifest()
        print("Existing frozen manifest verified")
        return
    facts=json.loads((ROOT/"outputs/facts/pressure_voice.json").read_text(encoding="utf-8"))
    if not facts["g0_passed"]:
        raise SystemExit("G0 must pass before freeze")
    d=pd.read_csv(ROOT/"outputs/tables/pressure_voice_municipality.csv")
    p=d[d.pilot_selected]
    if set(p.display_name)!=set(lex.PLACES):
        raise SystemExit("Pilot gazetteer mismatch")
    files=["python/pressure_voice_lexicon.py","python/pressure_voice_extract.py","python/test_pressure_voice_lexicon.py",
           "research/pritisak-bez-glasa/power_sim.py","outputs/tables/pressure_voice_power.csv"]
    obj=dict(version=1,created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),seed=SEED,
             authorization="User requested execution according to the saved plan on 2026-09-28",
             window_start="2025-04-01",window_end_exclusive="2026-04-01",confirmatory_start="2024-04-01",
             confirmatory_status="not_extracted_before_Gate_A",coding="human_only_local",
             article_table="media_data_all",source_batch="mediaspace_full",i_filtered=True,platform="web",
             gazetteer=p[["county","municipality","display_name","group","half"]].to_dict("records"),
             place_patterns=lex.PLACE_PATTERNS,family_patterns=lex.FAMILY_PATTERNS,
             context_rules=[vars(r) for r in lex.CONTEXT_RULES],max_window_characters=300,context_each_side=500,
             allowlist=allowlist(),aggregators=sorted(AGGREGATORS),
             language_rule="standalone i and >=2 distinct Croatian function words; partial language blinding audited by humans",
             d_floor=30,story_run_days=14,dedup_days=7,
             boilerplate_rule="sentence fingerprint in >=20 distinct documents; candidate removals require validation",
             dedup_rule="same URL, normalized full text, or same normalized title and first 240 body words within 7 days",
             gates=dict(A="place precision >=.90 for >=9 of12; candidate precision validated; corrected point RR<1",
                        G1="precision>=.80 overall,.70 strata; place>=.90 individual,.95 pooled;kappa>=.70;weighted recall CI",
                        G2="both documents and clusters: upper95RR<.5 strong,<1 pass; share ordering and leave-one-out",
                        G3=">=5 units D>=30 in low and middle size terciles before testing",
                        G4="nonoverlapping half CIs required to split C2"),
             model="NB2, log D offset; 2000 joint bootstrap draws over units and labels; pooled and unit-averaged estimands",
             robustness_spec="quality_reports/plans/2026-09-28_pritisak-bez-glasa_spec.md#robustness-suite",
             full_gazetteer_note="Literal top59+>=350+Podgora+8low+4middle rule selects70,88.65% nights; provisional until v2",
             sources={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
             source_db_size=SOURCE.stat().st_size,source_db_mtime_ns=SOURCE.stat().st_mtime_ns)
    MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    MANIFEST.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    sha=hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    MANIFEST.with_suffix(".sha256").write_text(sha+"\n",encoding="ascii")
    print("Manifest v1 frozen",sha)


def verify_manifest():
    obj=json.loads(MANIFEST.read_text(encoding="utf-8"))
    if hashlib.sha256(MANIFEST.read_bytes()).hexdigest()!=MANIFEST.with_suffix(".sha256").read_text().strip():
        raise SystemExit("Manifest hash mismatch")
    for f,sha in obj["sources"].items():
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=sha:
            raise SystemExit(f"Frozen source changed: {f}. Record a new version before extracting.")
    if SOURCE.stat().st_size!=obj["source_db_size"] or SOURCE.stat().st_mtime_ns!=obj["source_db_mtime_ns"]:
        raise SystemExit("Source database changed since freeze")
    return obj


def month_end(start):
    return dt.date(start.year+start.month//12,start.month%12+1,1)


def extract(months):
    manifest=verify_manifest()
    allowed=set(manifest["allowlist"])
    PRIVATE.mkdir(parents=True,exist_ok=True)
    con=duckdb.connect(str(SOURCE),read_only=True)
    con.execute("SET threads=2")
    con.execute("SET memory_limit='2GB'")
    con.execute("SET preserve_insertion_order=false")
    expected=pd.read_csv(ROOT/"research/pritisak-bez-glasa/evidence/WM_web_month_totals.csv")
    function_words=lex.rx(r"(?<!\p{L})(?:je|su|se|za|na|od|koji|koja|ali|te|u|i)(?!\p{L})")
    standalone_i=lex.rx(r"(?<!\p{L})i(?!\p{L})")
    for month in months:
        start=dt.date.fromisoformat(month+"-01");end=month_end(start)
        if not dt.date(2025,4,1)<=start<dt.date(2026,4,1):
            raise SystemExit("Only pre-specified pilot months allowed")
        final=PRIVATE/f"pilot_{month}.duckdb"
        if final.exists():
            print(month,"already extracted",flush=True);continue
        t=time.monotonic()
        base="SOURCE_TYPE='web' AND SOURCE_BATCH='mediaspace_full' AND DATETIME>=? AND DATETIME<?"
        total,body,filtered=con.execute(f"SELECT count(*),count(*) FILTER(WHERE length(trim(coalesce(FULL_TEXT,'')))>0), count(*) FILTER(WHERE I_FILTERED) FROM media_data_all WHERE {base}",[start,end]).fetchone()
        exp=expected[(expected.month==month)&(expected.batch=="mediaspace_full")].n_web.item()
        if total!=exp or filtered!=total or body/total<.99:
            raise SystemExit(f"Source integrity gate failed {month}: totals {total}/{exp}, filtered {filtered}, body {body}")
        target=PRIVATE/f"pilot_{month}.partial.duckdb"
        local=duckdb.connect(str(target))
        local.execute("CREATE OR REPLACE TABLE windows(window_id VARCHAR,doc_id VARCHAR,place VARCHAR,published DATE,domain VARCHAR,passage VARCHAR,masked_window VARCHAR,context VARCHAR,families VARCHAR,candidate BOOLEAN,traffic BOOLEAN,recall_score INTEGER,url_hash VARCHAR,body_hash VARCHAR,syndication_hash VARCHAR)")
        rows=con.execute(f"SELECT DATETIME,TITLE,FULL_TEXT,URL FROM media_data_all WHERE {base} AND I_FILTERED AND regexp_matches(lower(coalesce(TITLE,'')||' '||coalesce(FULL_TEXT,'')),?) AND regexp_matches(lower(coalesce(TITLE,'')||' '||coalesce(FULL_TEXT,'')),?)",[start,end,lex.SQL_TOURISM,SQL_PLACES])
        out=[]; n_prefilter=0;n_allowed=0;n_language=0;n_windows=0
        while batch:=rows.fetchmany(1000):
            for published,title,bodytext,url in batch:
                n_prefilter+=1
                host=domain(url or "")
                if host not in allowed or host in AGGREGATORS:
                    continue
                n_allowed+=1
                bodyclean=lex.clean(bodytext);titleclean=lex.clean(title)
                text=titleclean+".\n"+bodyclean
                if not standalone_i.search(text) or len(set(function_words.findall(text.lower())))<2:
                    continue
                n_language+=1
                doc_id=digest((url or "")+"|"+str(published)+"|"+bodyclean)
                body_hash=digest(regex.sub(r"\W+"," ",bodyclean.lower()))
                syndication_hash=digest(regex.sub(r"\W+"," ",titleclean.lower())+"|"+" ".join(regex.findall(r"\w+",bodyclean.lower())[:240]))
                for place,pattern in lex.PLACES.items():
                    if not pattern.search(text):
                        continue
                    for w in lex.windows(text,place):
                        wid=digest(doc_id+"|"+place+"|"+w["window"])
                        out.append((wid,doc_id,place,published.date(),host,w["window"],w["masked_window"],w["context"],w["families"],w["candidate"],w["traffic"],w["recall_score"],digest(url or doc_id),body_hash,syndication_hash))
            if out:
                frame=pd.DataFrame(out,columns=[r[0] for r in local.execute("DESCRIBE windows").fetchall()])
                local.register("batch",frame);local.execute("INSERT INTO windows SELECT * FROM batch");local.unregister("batch")
                n_windows+=len(out);out=[]
            if n_prefilter and n_prefilter%10000<1000:
                print(month,"processed",n_prefilter,"rows",flush=True)
        audit=dict(month=month,n_raw=total,n_body=body,n_filtered=filtered,n_prefilter=n_prefilter,n_allowlist=n_allowed,n_language=n_language,n_windows=n_windows,seconds=round(time.monotonic()-t,2))
        local.execute("CREATE TABLE metadata(key VARCHAR,value VARCHAR)")
        local.executemany("INSERT INTO metadata VALUES(?,?)",[("manifest_sha",MANIFEST.with_suffix(".sha256").read_text().strip()),("audit",json.dumps(audit))])
        local.close();target.replace(final)
        (PRIVATE/f"audit_{month}.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
        print(json.dumps(audit),flush=True)
    con.close()


if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--freeze",action="store_true");ap.add_argument("--months",nargs="*")
    args=ap.parse_args()
    if args.freeze:freeze()
    if args.months:extract(args.months)
