"""Historical tourism-context matches. Raw vendor text stays local and in memory.

Separate resumable output; the frozen pilot and its human packs are read-only.
The optimized window matcher is checked against the existing lexicon on synthetic
texts. Shards retain only hashes, place labels, dates and private publisher fields.
"""
from __future__ import annotations

import argparse
import bisect
from collections import deque
from concurrent.futures import ProcessPoolExecutor
import datetime as dt
import hashlib
import json
from pathlib import Path
import time

import duckdb
import pandas as pd
import regex

import pressure_voice_lexicon as lex
from pressure_voice_attention import STRICT
from pressure_voice_extract import SOURCE, MANIFEST, SQL_PLACES, domain, digest, month_end, verify_manifest
from pressure_voice_coding import hash_text

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "data/processed/pressure_voice/history_v3"
PLACES = list(lex.PLACE_PATTERNS)
LANGUAGE = lex.rx(r"(?<!\p{L})(?:je|su|se|za|na|od|koji|koja|ali|te|u|i)(?!\p{L})")
STANDALONE_I = lex.rx(r"(?<!\p{L})i(?!\p{L})")
COLUMNS = ["doc_id", "place", "published", "domain", "passage_hash", "url_hash", "body_hash", "syndication_hash", "traffic"]


def strict_windows(text):
    """Same centred windows as lex.windows, splitting shared text only once."""
    stripped = lex.STRIPS.sub(lambda m: " " * len(m.group()), text)
    sentence_cache = {}
    for name, pattern in lex.PLACES.items():
        unstripped = name == "Baška Voda"
        target = text if unstripped else stripped
        hits = list(pattern.finditer(target))
        if not hits:
            continue
        if unstripped not in sentence_cache:
            sentences = list(regex.finditer(r"[^.!?\n]+[.!?]?", target))
            sentence_cache[unstripped] = sentences, [s.end() for s in sentences]
        sentences, ends = sentence_cache[unstripped]
        seen = set()
        for match in hits:
            j = min(bisect.bisect_right(ends, match.start()), len(sentences) - 1)
            center = (match.start() + match.end()) // 2
            start = max(sentences[max(0, j - 1)].start(), center - 150)
            end = min(sentences[min(len(sentences) - 1, j + 1)].end(), center + 150)
            window = target[start:end].strip()
            key = (name, window)
            if key not in seen and STRICT.search(window):
                seen.add(key)
                yield name, window, bool(lex.TRAFFIC.search(window))


def process_batch(batch, allowed):
    """CPU workers process local text and return hashes only."""
    records, scanned = {}, {}
    for published, title, body, url in batch:
        month = published.strftime("%Y-%m")
        scanned[month] = scanned.get(month, 0) + 1
        host = domain(url or "")
        if host not in allowed:
            continue
        bodyclean, titleclean = lex.clean(body), lex.clean(title)
        text = titleclean + ".\n" + bodyclean
        if not STANDALONE_I.search(text) or len(set(LANGUAGE.findall(text.lower()))) < 2:
            continue
        windows = list(strict_windows(text))
        if not windows:
            continue
        doc_id = digest((url or "") + "|" + str(published) + "|" + bodyclean)
        body_hash = digest(regex.sub(r"\W+", " ", bodyclean.lower()))
        syndication_hash = digest(regex.sub(r"\W+", " ", titleclean.lower()) + "|" + " ".join(regex.findall(r"\w+", bodyclean.lower())[:240]))
        url_hash = digest(url or doc_id)
        records.setdefault(month, []).extend((doc_id, name, published.date(), host, hash_text(window), url_hash, body_hash, syndication_hash, traffic) for name, window, traffic in windows)
    return records, scanned


def extract(months):
    manifest = verify_manifest()
    RUN.mkdir(parents=True, exist_ok=True)
    allowed = set(manifest["allowlist"]) - set(manifest["aggregators"])
    coverage = pd.read_csv(ROOT / "outputs/tables/pressure_voice_history_media_coverage.csv")
    run_manifest = {
        "source_size": SOURCE.stat().st_size, "source_mtime_ns": SOURCE.stat().st_mtime_ns,
        "frozen_pilot_sha": MANIFEST.with_suffix(".sha256").read_text().strip(),
        "extractor_sha": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "definition": "strict tourism-context windows; same language and place rules across all years",
    }
    path = RUN / "manifest.json"
    if path.exists():
        assert json.loads(path.read_text()) == run_manifest, "Historical run inputs changed; use a new run directory"
    else:
        path.write_text(json.dumps(run_manifest, indent=2), encoding="utf-8")
    con = duckdb.connect(str(SOURCE), read_only=True)
    con.execute("SET threads=2")
    con.execute("SET memory_limit='2GB'")
    pending = []
    for month in months:
        final = RUN / f"mentions_{month}.parquet"
        audit_path = RUN / f"audit_{month}.json"
        if final.exists() and audit_path.exists():
            print(month, "cached", flush=True)
            continue
        started = time.monotonic()
        original = ROOT / f"data/processed/pressure_voice/pilot_{month}.duckdb"
        if original.exists():
            pilot = duckdb.connect(str(original), read_only=True)
            w = pilot.execute("SELECT * FROM windows").df()
            pilot.close()
            w = w[w.passage.map(lambda t: bool(STRICT.search(t)))].copy()
            w["passage_hash"] = w.passage.map(hash_text)
            frame = w[COLUMNS].copy()
            method = "existing_frozen_pilot"
            scanned = None
        else:
            pending.append(month)
            continue
        frame = frame.drop_duplicates(["doc_id", "place", "passage_hash"])
        temp = RUN / f"mentions_{month}.partial.parquet"
        frame.to_parquet(temp, index=False)
        temp.replace(final)
        audit = {"month": month, "method": method, "source_rows": int(coverage.loc[coverage.month.eq(month), "records"].sum()),
                 "prefilter_rows": scanned, "windows": len(frame), "documents": int(frame.doc_id.nunique()),
                 "seconds": round(time.monotonic() - started, 2)}
        audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
        print(json.dumps(audit), flush=True)
    # Legacy rows are not sorted by date: one scan per month rereads the same
    # large row groups. Stream each source batch once and route matches by month.
    for source_batch in coverage.batch.unique():
        todo = coverage[coverage.month.isin(pending) & coverage.batch.eq(source_batch)].month.tolist()
        if not todo:
            continue
        started = time.monotonic()
        print("Scanning", source_batch, "for", len(todo), "months", flush=True)
        rows = con.execute("""SELECT DATETIME,TITLE,FULL_TEXT,URL
            FROM media_data_all WHERE SOURCE_TYPE='web' AND SOURCE_BATCH=?
            AND strftime(DATETIME, '%Y-%m') IN (SELECT unnest(?))
            AND regexp_matches(lower(coalesce(TITLE,'') || ' ' || coalesce(FULL_TEXT,'')),?)
            AND regexp_matches(lower(coalesce(TITLE,'') || ' ' || coalesce(FULL_TEXT,'')),?)""",
            [source_batch, todo, lex.SQL_TOURISM, SQL_PLACES])
        records = {month: [] for month in todo}
        scanned = {month: 0 for month in todo}
        total = 0
        def collect(future):
            nonlocal total
            hits, counts = future.result()
            for month, values in hits.items():
                records[month].extend(values)
            for month, count in counts.items():
                scanned[month] += count
                total += count
            if total % 10000 == 0:
                print(source_batch, "processed", total, "candidates", flush=True)
        with ProcessPoolExecutor(max_workers=4) as pool:
            waiting = deque()
            while batch := rows.fetchmany(1000):
                waiting.append(pool.submit(process_batch, batch, allowed))
                if len(waiting) >= 8:
                    collect(waiting.popleft())
            while waiting:
                collect(waiting.popleft())
        elapsed = round(time.monotonic() - started, 2)
        for month in todo:
            frame = pd.DataFrame(records[month], columns=COLUMNS).drop_duplicates(["doc_id", "place", "passage_hash"])
            temp = RUN / f"mentions_{month}.partial.parquet"
            frame.to_parquet(temp, index=False)
            temp.replace(RUN / f"mentions_{month}.parquet")
            audit = {"month": month, "method": "historical_source_batch_scan", "source_rows": int(coverage.loc[coverage.month.eq(month), "records"].sum()),
                     "prefilter_rows": scanned[month], "windows": len(frame), "documents": int(frame.doc_id.nunique()), "seconds": elapsed / len(todo)}
            (RUN / f"audit_{month}.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
            print(json.dumps(audit), flush=True)
    con.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--months", nargs="*")
    args = parser.parse_args()
    months = args.months or pd.read_csv(ROOT / "outputs/tables/pressure_voice_history_media_coverage.csv").month.tolist()
    extract(months)
