"""Build inline Quarto facts and a compact claim ledger from saved outputs."""
import hashlib
import json
from pathlib import Path
import re
import pandas as pd
from food_drink_2026_extract import COMPANIES, DATA, OUT, ROOT, SOURCE

def main():
 d=pd.read_parquet(DATA/'headlines.parquet')
 monthly=pd.read_csv(OUT/'monthly.csv').set_index('month')
 companies=pd.read_csv(OUT/'companies.csv').set_index('company')
 topics=pd.read_csv(OUT/'topics_monthly.csv')
 macro=pd.read_csv(OUT/'macro_facts.csv').set_index('key').value.to_dict()
 cf=pd.read_csv(OUT/'company_facts.csv').set_index('key').value.to_dict()
 ma=json.loads((OUT/'macro_audit.json').read_text(encoding='utf-8'))
 sa=json.loads((OUT/'selection_audit.json').read_text(encoding='utf-8'))
 cases=pd.read_parquet(DATA/'cases.parquet')
 # Descriptive media profiles for the revised exploratory overview.
 outlet_counts=d.groupby('outlet_type').size()
 outlet_monthly=d.groupby(['month','outlet_type']).size().rename('articles').reset_index()
 outlet_monthly.to_csv(OUT/'outlet_monthly.csv',index=False)
 cm=pd.read_csv(OUT/'company_monthly.csv')
 co=pd.read_csv(OUT/'company_outlet_types.csv')
 profiles=[]
 for company,row in companies.iterrows():
  months=cm[cm.company.eq(company)].sort_values(['mentions','month'],ascending=[False,True])
  outlets=co[co.company.eq(company)].sort_values(['mentions','outlet_type'],ascending=[False,True])
  profiles.append(dict(company=company,mentions=int(row.mentions),months=int(row.months),outlets=int(row.outlets),
                       peak_month=months.month.iloc[0] if len(months) else '',
                       peak_mentions=int(months.mentions.iloc[0]) if len(months) else 0,
                       leading_outlet_type=outlets.outlet_type.iloc[0] if len(outlets) else '',
                       leading_outlet_mentions=int(outlets.mentions.iloc[0]) if len(outlets) else 0))
 pd.DataFrame(profiles).to_csv(OUT/'company_profiles.csv',index=False)
 agro=cases[cases.published.between('2026-06-22','2026-06-28')&cases.title.str.contains('bezalkohol',case=False)].copy()
 agro['producer_in_title']=agro.title.str.contains('agrolagun',case=False)
 # This evidence table contains bibliographic metadata only; no article bodies.
 agro[['doc_id','published','domain','title','url','producer_in_title']].to_csv(OUT/'agrolaguna_case.csv',index=False)
 kras=d[d.published.between('2026-02-25','2026-02-26')&d.companies.str.contains('Kraš')&d['rezultati']]
 kras[['doc_id','published','domain','title','url']].to_csv(OUT/'kras_case.csv',index=False)
 facts={**macro,**cf,
  'frame_companies':len(COMPANIES),'n_articles':len(d),'n_pairs':int(companies.mentions.sum()),
  'panel_outlets':sa['panel_outlets'],'active_outlets':sa['outlets_with_headlines'],
  'podravka_mentions':int(companies.loc['Podravka','mentions']),
  'podravka_pair_share_pct':float(companies.loc['Podravka','share_of_pairs_pct']),
  'kras_mentions':int(companies.loc['Kraš','mentions']),
  'mlinar_mentions':int(companies.loc['Mlinar','mentions']),
  'pik_mentions':int(companies.loc['PIK Vrbovec','mentions']),
  'top_three_pair_share_pct':100*float(companies.mentions.nlargest(3).sum())/float(companies.mentions.sum()),
  'food_pair_share_pct':100*float(companies[companies.sector.eq('hrana')].mentions.sum())/float(companies.mentions.sum()),
  'podravka_local_mentions':int(co[(co.company=='Podravka')&(co.outlet_type=='lokalni i regionalni')].mentions.iloc[0]),
  'podravka_local_share_pct':100*float(co[(co.company=='Podravka')&(co.outlet_type=='lokalni i regionalni')].mentions.iloc[0])/float(companies.loc['Podravka','mentions']),
  'kras_business_mentions':int(co[(co.company=='Kraš')&(co.outlet_type=='poslovni i stručni')].mentions.iloc[0]),
  'general_articles':int(outlet_counts['opći']),
  'business_articles':int(outlet_counts['poslovni i stručni']),
  'local_articles':int(outlet_counts['lokalni i regionalni']),
  'mlinar_active_months':int(companies.loc['Mlinar','months']),
  'agrolaguna_active_months':int(companies.loc['Agrolaguna','months']),
  'agrolaguna_mentions':int(companies.loc['Agrolaguna','mentions']),
  'mlinar_december_mentions':int(cm[(cm.company=='Mlinar')&(cm.month=='2025-12')].mentions.iloc[0]),
  'april_articles':int(monthly.loc['2026-04','articles']),
  'june_articles':int(monthly.loc['2026-06','articles']),
  'january_articles':int(monthly.loc['2026-01','articles']),
  'april_investment_articles':int(topics[(topics.month=='2026-04')&(topics.topic=='ulaganja i vlasništvo')].articles.iloc[0]),
  'october_articles':int(monthly.loc['2025-10','articles']),
  'november_articles':int(monthly.loc['2025-11','articles']),
  'july_articles':int(monthly.loc['2026-07','articles']),
  'august_articles':int(monthly.loc['2026-08','articles']),
  'july_rate':float(monthly.loc['2026-07','per_1000_records']),
  'august_rate':float(monthly.loc['2026-08','per_1000_records']),
  'agrolaguna_case_articles':len(agro),'agrolaguna_named_titles':int(agro.producer_in_title.sum()),
  'agrolaguna_unnamed_titles':int((~agro.producer_in_title).sum()),
  'agrolaguna_repeated_title_prefix':int(agro.title.str.startswith('Inovacija iz Agrolagune').sum()),
  'april_investment_share_pct':float(topics[(topics.month=='2026-04')&(topics.topic=='ulaganja i vlasništvo')].share_pct.iloc[0]),
  'february_results_share_pct':float(topics[(topics.month=='2026-02')&(topics.topic=='rezultati')].share_pct.iloc[0]),
  'trade_coverage_pct':ma['trade_coverage_pct'],'trade_deficit_billion':ma['trade_deficit_million_eur']/1000,
  'trade_export_growth_pct':ma['trade_export_growth_pct'],'trade_import_growth_pct':ma['trade_import_growth_pct'],
 }
 prod=pd.read_csv(OUT/'production_monthly.csv')
 for r in prod.itertuples():facts[f'production_{r.sector}_{r.month}']=r.yoy_pct
 assert len(monthly)==12 and monthly.articles.sum()==len(d)
 assert d.doc_id.is_unique and d.publisher_key.is_unique
 assert len(companies)==20 and all(companies.mentions>=0)
 assert len(agro)==10 and int(agro.producer_in_title.sum())==9
 assert monthly.articles.idxmax()=='2025-10'
 assert monthly.per_1000_records.idxmax()=='2025-10'
 assert len(prod)==24 and prod.groupby('sector').size().eq(12).all()
 assert topics.share_pct.between(0,100).all()
 assert sa['headline_articles']==len(d) and sa['company_article_pairs']==companies.mentions.sum()
 assert outlet_counts.sum()==len(d) and outlet_monthly.articles.sum()==len(d)
 assert cm.mentions.sum()==companies.mentions.sum()==co.mentions.sum()
 sensitivity=[]
 for threshold in (.75,.85,.95):
  col=f'cluster_{threshold}'
  collapsed=d.drop_duplicates(col)
  pairs=d.assign(company=d.companies.str.split('|')).explode('company').drop_duplicates(['company',col])
  rank=pairs.groupby('company').size().sort_values(ascending=False)
  sensitivity.append(dict(variant=f'collapse_representative_cosine_{threshold}',articles=len(collapsed),
                          leading_company=rank.index[0],podravka_share_pct=100*rank['Podravka']/rank.sum(),
                          peak_article_month=collapsed.groupby('month').size().idxmax()))
 pd.DataFrame(sensitivity).to_csv(OUT/'cluster_sensitivity.csv',index=False)
 manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8'))
 assert SOURCE.stat().st_size==manifest['size'] and SOURCE.stat().st_mtime_ns==manifest['mtime_ns']
 fpath=ROOT/'outputs/facts/food_drink_2026.json';fpath.parent.mkdir(parents=True,exist_ok=True)
 fpath.write_text(json.dumps(facts,ensure_ascii=False,indent=2),encoding='utf-8')
 ledger=[]
 for k,v in facts.items():
  source='macro_facts.csv' if k in macro else 'company_facts.csv' if k in cf else 'derived from saved media/macro tables'
  ledger.append(dict(key=k,value=v,source=source))
 pd.DataFrame(ledger).to_csv(OUT/'claim_ledger.csv',index=False)
 report=dict(invariants_passed=True,source_database_unchanged=True,articles=len(d),
  unique_article_identifiers=True,monthly_and_company_totals_reconcile=True,macro_dates_and_adjustments_recorded=True,
  output_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('*.csv'))},
  scope='Preliminary deterministic analysis; not a representative census and no recall estimate.')
 dest=ROOT/'quality_reports/2026-10-05_food-drink-verification.json'
 dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in facts.items() if not k.startswith('production_')},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
