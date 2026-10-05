"""Read-only, bounded media extraction; vendor article text stays in ignored data/.

The company frame is EIZ, Sektorske analize 130, tables 6 and 8 (2024 firms).
This is a purposive panel, not the whole industry or a census of media.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import random
import re
import time
from urllib.parse import urlsplit
import duckdb
import pandas as pd

random.seed(20261005)
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/processed/food_drink_2026'
OUT = ROOT / 'outputs/tables/food_drink_2026'
SOURCE = Path(os.environ.get('DETERMDB_MERGED', 'C:/Users/lsikic/Luka C/DetermDB/determDB_merged.duckdb'))
START, END = '2025-09-01', '2026-09-01'
COMPANIES = {
 'Podravka': ('hrana', r'podravk\w*'),
 'Vindija': ('hrana', r'vindij\w*'),
 'Dukat': ('hrana', r'dukat\w*'),
 'Pivac': ('hrana', r'pivac\w*|pivca|pivcu|pivcem'),
 'PIK Vrbovec': ('hrana', r'pik[ -]+vrbov\w*'),
 'PPK': ('hrana', r'ppk'),
 'Arivera fruit': ('hrana', r'ariver\w*'),
 'Ledo': ('hrana', r'ledo\w*'),
 'Kraš': ('hrana', r'kraš\w*|kras(?:a|u|em)?'),
 'Mlinar': ('hrana', r'mlinar\w*'),
 'Coca-Cola': ('piće', r'coca[ -]?col\w*'),
 'Jamnica': ('piće', r'jamnic\w*'),
 'Zagrebačka pivovara': ('piće', r'zagrebačk\w* pivovar\w*'),
 'Heineken': ('piće', r'heineken\w*'),
 'Badel 1862': ('piće', r'badel\w*'),
 'Carlsberg': ('piće', r'carlsberg\w*'),
 'Slavonija slad': ('piće', r'slavonij\w* slad\w*'),
 'Agrolaguna': ('piće', r'agrolagun\w*'),
 'Maraska': ('piće', r'marask\w*'),
 'Pivovara Daruvar': ('piće', r'pivovar\w* daruvar\w*|daruvarsk\w* pivovar\w*'),
}
# Explicit editorial types, not inferred from traffic, location or vendor labels.
OUTLETS = {
 'opći': '24sata.hr index.hr jutarnji.hr vecernji.hr tportal.hr dnevnik.hr net.hr danas.hr rtl.hr hrt.hr n1info.hr hr.n1info.com telegram.hr nacional.hr dnevno.hr direktno.hr hina.hr'.split(),
 'poslovni i stručni': 'poslovni.hr lider.media lidermedia.hr hr.bloombergadria.com financije.hr tockanai.hr jatrgovac.com jatrgovac.hr agroklub.com agroportal.hr plavakamenica.hr hrturizam.hr poslovni-savjetnik.com poslovnipuls.com'.split(),
 'lokalni i regionalni': 'slobodnadalmacija.hr novilist.hr glasistre.hr glas-slavonije.hr glas-slavonije.com glaspodravine.hr podravski.hr epodravina.hr klikaj.hr danica.hr evarazdin.hr varazdinske-vijesti.hr dalmatinskiportal.hr dalmacijadanas.hr dubrovackidnevnik.hr dulist.hr sibenik.in sibenskiportal.hr zadarskilist.novilist.hr parentium.com porestina.info istra24.hr istrain.hr regionalexpress.hr ipress.hr istarski.hr kaportal.hr karlovacki.hr ka-portal.hr icv.hr osijek031.com'.split(),
}

def main():
 DATA.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
 before = (SOURCE.stat().st_size, SOURCE.stat().st_mtime_ns)
 con = duckdb.connect(str(SOURCE), read_only=True)
 con.execute("SET threads=3"); con.execute("SET memory_limit='3GB'")
 scratch = ROOT/'tmp/food_drink_2026/duckdb'; scratch.mkdir(parents=True,exist_ok=True)
 con.execute(f"SET temp_directory='{scratch.as_posix()}'")
 domains = pd.DataFrame([(d,t) for t, ds in OUTLETS.items() for d in ds], columns=['domain','outlet_type'])
 con.register('outlets', domains)
 host = "regexp_replace(lower(regexp_extract(URL, '^https?://([^/:]+)', 1)), '^www\\.', '')"
 # Longest suffix wins, so a separately defined regional subdomain remains distinct.
 scoped = f"""SELECT m.*, o.domain, o.outlet_type FROM media_data_all m
 JOIN outlets o ON ({host} = o.domain OR ends_with({host}, '.' || o.domain))
 WHERE DATE >= '{START}' AND DATE < '{END}' AND SOURCE_TYPE='web'
 QUALIFY row_number() OVER (PARTITION BY SOURCE_TYPE, ITEM_ID, URL, DATE ORDER BY length(o.domain) DESC)=1"""
 # Aggregate original date strings; no DATE/DATETIME mixing.
 print('Monthly outlet coverage', flush=True)
 coverage_path=OUT/'outlet_coverage.csv'
 old_manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8')) if (DATA/'manifest.json').exists() else {}
 cached=(coverage_path.exists() and old_manifest.get('size')==before[0] and old_manifest.get('mtime_ns')==before[1]
         and old_manifest.get('outlets')==OUTLETS and old_manifest.get('start')==START and old_manifest.get('end_exclusive')==END)
 coverage = pd.read_csv(coverage_path) if cached else con.sql(f"SELECT substr(DATE,1,7) AS month, domain, outlet_type, count(*) AS records, count(DISTINCT DATE) AS observed_days FROM ({scoped}) GROUP BY ALL ORDER BY 1,2").df()
 coverage.to_csv(OUT/'outlet_coverage.csv', index=False)
 pattern = r'(?i)(?:' + '|'.join(x[1] for x in COMPANIES.values()) + r')'
 # Main sample is headline visibility. Separately include the brief's alcohol-free
 # wine case via its product words, to check whether the producer name disappears.
 # Deliberately loose candidate screen. Exact Unicode boundaries and inflections
 # are applied in Python; RE2 Unicode-boundary expansion is prohibitively slow.
 print('Extracting company candidates', flush=True)
 query = f"""SELECT DATE published, TITLE title, URL url, FULL_TEXT body, ITEM_ID item_id,
 LANGUAGES languages, LOCATIONS locations
 FROM media_data_all WHERE DATE >= '{START}' AND DATE < '{END}' AND SOURCE_TYPE='web'
 AND (regexp_matches(coalesce(TITLE,''), ?) OR (DATE >= '2026-06-01' AND DATE < '2026-07-01'
 AND regexp_matches(lower(TITLE),'bezalkohol') AND regexp_matches(lower(TITLE),'vin')))"""
 candidates = con.execute(query, [pattern]).df()
 domain_types=dict(zip(domains.domain,domains.outlet_type))
 ordered=sorted(domain_types,key=len,reverse=True)
 def identify(url):
  host=(urlsplit(url or '').hostname or '').removeprefix('www.')
  return next((d for d in ordered if host==d or host.endswith('.'+d)),None)
 candidates['domain']=candidates.url.map(identify)
 candidates=candidates[candidates.domain.notna()].copy()
 candidates['outlet_type']=candidates.domain.map(domain_types)
 candidates.to_parquet(DATA/'candidates.parquet',index=False)
 con.close()
 after = (SOURCE.stat().st_size, SOURCE.stat().st_mtime_ns)
 assert before == after, 'Source DB metadata changed during extraction'
 manifest = dict(source=str(SOURCE), size=before[0], mtime_ns=before[1], table='media_data_all',
                 start=START, end_exclusive=END, source_type='web', companies=COMPANIES,
                 outlets=OUTLETS, candidate_rule='company name in title; extra June alcohol-free wine titles for case analysis only',
                 candidates=len(candidates), source_unchanged=True, seed=20261005,
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (DATA/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'candidates':len(candidates), 'domains':coverage.domain.nunique(),
                   'coverage_records':int(coverage.records.sum())}),flush=True)
 print(candidates.groupby('domain').size().sort_values(ascending=False).head(15).to_string())

if __name__ == '__main__': main()
