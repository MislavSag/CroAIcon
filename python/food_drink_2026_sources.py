"""Cache public sources. No vendor data leaves the local machine."""
from pathlib import Path
import hashlib
import json
from urllib.request import urlopen
from urllib.error import HTTPError

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'data/raw/food_drink_2026'
URLS={
 'eiz_hrana_pice_2026.pdf':'https://www.eizg.hr/userdocsimages/publikacije/serijske-publikacije/sektorske-analize/SA_Hrana-i-pice_2026_HR_f.pdf',
 'dzs_2025_12.html':'https://podaci.dzs.hr/2025/hr/97267',
 'dzs_2026_02.html':'https://podaci.dzs.hr/2026/hr/121409',
 'dzs_2026_08.html':'https://podaci.dzs.hr/2026/hr/120999',
 'kras_february.html':'https://www.kras.hr/hr/novosti/kras-zavrsio-godinu-s-prvim-znakovima-oporavka-uz-fokus-na-kvalitetu-i-dugorocni-rast',
 'kras_july.html':'https://www.kras.hr/hr/novosti/kras-u-prvoj-polovici-2026-biljezi-rast-prihoda',
 'agrolaguna.html':'https://agrolaguna.hr/',
}

if __name__=='__main__':
 DEST.mkdir(parents=True,exist_ok=True)
 rows=[]
 for name,url in URLS.items():
  p=DEST/name
  if not p.exists():
   try:
    with urlopen(url,timeout=60) as response: p.write_bytes(response.read())
   except HTTPError as error:
    rows.append(dict(file=name,url=url,status=error.code,note='Use web retrieval evidence / attributed transcription; no local HTML cache.'))
    print(name,error.code,flush=True)
    continue
  rows.append(dict(file=name,url=url,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size))
  print(name,p.stat().st_size,flush=True)
 (DEST/'sources.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
