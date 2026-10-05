"""Parse saved DZS releases and reproduce selected EIZ table values.

Do not mix original annual volume growth with calendar-adjusted monthly growth.
All public numeric claims are saved to outputs; EIZ transcriptions retain page/table.
"""
from pathlib import Path
import json
import hashlib
import re
import random
from lxml import html
import pandas as pd
import pymupdf
from food_drink_2026_sources import URLS

random.seed(20261005)
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw/food_drink_2026'
OUT=ROOT/'outputs/tables/food_drink_2026'

def rows(name,table):
 doc=html.fromstring((RAW/name).read_bytes())
 t=doc.xpath('//table[not(.//table)]')[table]
 return [[' '.join(c.text_content().split()) for c in r.xpath('./th|./td')] for r in t.xpath('.//tr')]

def numeric(text): return float(text.replace('.','').replace(',','.'))

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 series=[]; facts=[]
 releases=[('dzs_2026_02.html','2026-03-31',pd.period_range('2025-09','2026-02',freq='M')),
           ('dzs_2026_08.html','2026-09-30',pd.period_range('2026-03','2026-08',freq='M'))]
 for name,released,months in releases:
  for row in rows(name,1):
   if not row or row[0][:3] not in ('10 ','11 '): continue
   sector='hrana' if row[0].startswith('10 ') else 'piće'
   assert len(row)==8
   for month,value in zip(months,row[1:7]):
    series.append(dict(month=str(month),sector=sector,yoy_pct=numeric(value),
                       adjustment='calendar adjusted',release_date=released,url=URLS[name]))
   facts.append(dict(key=f'{sector}_ytd_{str(months[-1])}',value=numeric(row[-1]),unit='%',period=f'January–{str(months[-1])}',
                     definition='Calendar-adjusted production change against same period a year earlier',source=URLS[name],locator='I.2'))
 for row in rows('dzs_2025_12.html',2):
  if not row or row[0][:3] not in ('10 ','11 '):continue
  sector='hrana' if row[0].startswith('10 ') else 'piće'
  facts.append(dict(key=f'{sector}_production_2025',value=round(numeric(row[-1])-100,5),unit='%',period='2025',
                    definition='Original, unadjusted annual production growth',source=URLS['dzs_2025_12.html'],locator='II.1'))
 # Visual-checked EIZ tables. Exact source values first; any arithmetic is separate.
 source=URLS['eiz_hrana_pice_2026.pdf']
 for key,value,unit,period,definition,locator in [
  ('food_gross_wage',1646,'EUR','2025 annual average','Mean monthly gross wage, food manufacturing','Table 2, p.8'),
  ('drink_gross_wage',2192,'EUR','2025 annual average','Mean monthly gross wage, beverage manufacturing','Table 2, p.8'),
  ('food_employment',43331,'persons','December 2025','Employees in legal entities, food manufacturing','p.4'),
  ('drink_employment',5643,'persons','December 2025','Employees in legal entities, beverage manufacturing','p.5'),
  ('food_employment_yoy',-5.7,'%','December 2025/December 2024','Employment change; endpoint, not annual average','p.4'),
  ('drink_employment_yoy',-2.3,'%','December 2025/December 2024','Employment change; endpoint, not annual average','p.5'),
  ('exports_2024',2501738,'thousand EUR','2024','Exports of food, beverages AND tobacco','Table 4, p.9'),
  ('imports_2024',5043765,'thousand EUR','2024','Imports of food, beverages AND tobacco','Table 4, p.9'),
  ('exports_2025',2655362,'thousand EUR','2025','Exports of food, beverages AND tobacco','Table 4, p.9'),
  ('imports_2025',5486926,'thousand EUR','2025','Imports of food, beverages AND tobacco','Table 4, p.9'),
 ]: facts.append(dict(key=key,value=value,unit=unit,period=period,definition=definition,source=source,locator=locator))
 df=pd.DataFrame(facts)
 df.to_csv(OUT/'macro_facts.csv',index=False)
 pd.read_csv(ROOT/'data/reference/food_drink_company_facts.csv').to_csv(OUT/'company_facts.csv',index=False)
 pd.DataFrame(series).to_csv(OUT/'production_monthly.csv',index=False)
 # Match EIZ first, then extend. Extract the printed table to check annual values.
 pdf=pymupdf.open(RAW/'eiz_hrana_pice_2026.pdf')
 text=pdf[2].get_text()
 assert '1,6' in text and '8,5' in text
 f=df.set_index('key').value.to_dict()
 assert abs(f['hrana_production_2025']-1.6)<1e-8 and abs(f['piće_production_2025']-8.5)<1e-8
 audit=dict(eiz_annual_production_reproduced_from_dzs=True,
  trade_export_growth_pct=100*(f['exports_2025']/f['exports_2024']-1),
  trade_import_growth_pct=100*(f['imports_2025']/f['imports_2024']-1),
  trade_coverage_pct=100*f['exports_2025']/f['imports_2025'],
  trade_deficit_million_eur=(f['imports_2025']-f['exports_2025'])/1000,
  wage_gap_eur=f['drink_gross_wage']-f['food_gross_wage'],
  source_issues_excluded=[
   'EIZ p.2 says top-ten food employment fell 2.8%; Table 5 and p.10 say it rose 2.8%.',
   'EIZ p.5 gives April 2026 producer prices inside a report dated April; release/vintage not established.',
   'EIZ p.5 productivity text does not reconcile with Table 3; not used.'
  ], inputs={n:hashlib.sha256((RAW/n).read_bytes()).hexdigest() for n in URLS if (RAW/n).exists()})
 (OUT/'macro_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
 print(df[['key','value']].to_string(index=False))
 print(pd.DataFrame(series).pivot(index='month',columns='sector',values='yoy_pct').to_string())

if __name__=='__main__':main()
