"""Exploratory headline analysis. Fixed producer frame, explicit exclusions.

Headline company mentions are the main sample. Extra lead matches support case
discovery, not a full-text census or headline visibility. Topic labels are
overlapping lexical signals, not human judgments of tone or article purpose.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import random
import re
from urllib.parse import urlsplit, urlunsplit
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from food_drink_2026_extract import COMPANIES, DATA, OUT, ROOT

random.seed(20261005); np.random.seed(20261005)
RX={k:re.compile(r'(?<!\w)(?:'+v[1]+r')(?!\w)',re.I) for k,v in COMPANIES.items()}
RX['Podravka']=re.compile(r'(?<!\w)podrav(?:ka|ke|ki|ku|kom|kin(?:a|e|i|o|u|ih|im|og|oj|om)?)(?!\w)',re.I)
# Broad SQL candidates are refined to actual company inflections here.
RX['Kraš']=re.compile(r'(?<!\w)(?:kraš(?:a|u|em|ev(?:a|e|i|o|u|ih|im|og|oj|om)?)?|kras(?:a|u|em)?)(?!\w)',re.I)
RX['Ledo']=re.compile(r'(?<!\w)ledo(?:v(?:a|e|i|o|u|ih|im|og|oj|om)?)?(?!\w)',re.I)
RX['Mlinar']=re.compile(r'(?<!\w)mlinar(?:a|u|om|ov(?:a|e|i|o|u|ih|im|og|oj|om)?)?(?!\w)',re.I)
RX['Badel 1862']=re.compile(r'(?<!\w)badel(?:a|u|om|ov(?:a|e|i|o|u|ih|im|og|oj|om)?)?(?!\w)',re.I)
RX['Dukat']=re.compile(r'(?<!\w)dukat(?:a|u|om|ov(?:a|e|i|o|u|ih|im|og|oj|om)?)?(?!\w)',re.I)
RX['Maraska']=re.compile(r'(?<!\w)marask(?:a|e|i|u|om|in(?:a|e|i|u|ih|im|og|oj|om)?)(?!\w)',re.I)
TOPICS={
 'rezultati': r'\b(?:dobit(?:i|ak|ka|ku|kom)?\b|prihod\w*|rashod\w*|ebit\w*|profit\w*|marž\w*|rezultat\w*|poslovanj\w*)',
 'ulaganja i vlasništvo': r'\b(?:invest\w*|ulaga\w*|ulož\w*|kapacitet\w*|akvizic\w*|preuzimanj\w*|preuzima\s+(?:jamnic\w*|pik|kraš\w*|mlinar\w*|tvrtk\w*|kompanij\w*)|vlasni\w*|prodaja tvrtke|dionic\w*|burz\w*|dividend\w*|nov\w*\s+(?:tvornic\w*|pogon\w*))',
 'cijene i troškovi': r'\b(?:cijen\w*|poskup\w*|pojeft\w*|inflac\w*|bojkot\w*|kaka\w*|sirovin\w*|troškov\w*)',
 'rad i plaće': r'\b(?:plać\w*|radni[ckč]\w*|radnik\w*|zaposl\w*|otkaz\w*|štrajk\w*|kolektivn\w*)',
 'proizvodi i promocija': r'\b(?:predstav\w*|lansir\w*|inovac\w*|bezalkohol\w*|ambalaž\w*|okus\w*|brend\w*|nagrad\w*|festival\w*|sponzor\w*|donac\w*|donir\w*|nov\w* proizvod\w*)',
}
TRX={k:re.compile(v,re.I) for k,v in TOPICS.items()}
SPORT=re.compile(r'\b(?:rukomet\w*|nogomet\w*|utakmic\w*|prvenstv\w*|prvakinj\w*|prvac\w*|golov\w*|trener\w*|igrač\w*|pobjed\w*|liga|ligi|lige|ligu|osmin\w*|četvrtfinal\w*|final\w*|sport\w*|navijač\w*|veznjak\w*|derbi\w*|hrvač\w*|ribič\w*|ribolov\w*|žrk|kugla\w*|strijel\w*|košarka\w*|tenis\w*|triatlon\w*|karat\w*|badminton\w*|baseball\w*|bejzbol\w*|turnir\w*|atlet\w*)',re.I)
BUSINESS=re.compile(r'\b(?:tvrtk\w*|kompanij\w*|proizvo\w*|poslov\w*|prihod\w*|dobit\w*|pogon\w*|invest\w*|ulag\w*|radnik\w*|zaposl\w*|plać\w*|sponzor\w*|donir\w*|donac\w*|brend\w*|mlijek\w*|mliječ\w*|mesn\w*|pekar\w*|čokol\w*|sladoled\w*)',re.I)
DOMESTIC=re.compile(r'hrvatsk|zagre[bp]|koprivni|karlov|varaždin|vrbov|daruvar|istra|istarsk|poreč|marask|badel|jamnic',re.I)

def clean(s):return re.sub(r'\s+',' ',html.unescape(s or '')).strip()
def normalize(s):return ' '.join(re.findall(r'\w+',clean(s).lower()))
def canonical(url):
 p=urlsplit(url); return urlunsplit((p.scheme.lower(),p.netloc.lower().removeprefix('www.'),p.path.rstrip('/'),'', ''))

def publisher_key(url,domain):
 path=urlsplit(url).path
 if domain=='index.hr':
  match=re.search(r'/([0-9]+)\.aspx$',path)
  if match:return domain+'/'+match[1]
 if domain in {'jutarnji.hr','vecernji.hr','24sata.hr','slobodnadalmacija.hr'}:
  match=re.search(r'-([0-9]{6,})$',path)
  if match:return domain+'/'+match[1]
 return canonical(url)

def allowed(name,title,lead):
 if name=='Podravka' and re.search(r'sel\w* podravk',title,re.I):return False,'place_name_typo'
 if name=='Podravka' and re.search(r'podvožnjak|podvoznjak|raskriž|semafor',title,re.I):return False,'landmark_in_traffic_news'
 if name=='Kraš' and re.search(r'\b(?:an[aeiu]|mart[aeiu]|josip[auei]?) kraš',title,re.I):return False,'unrelated_person'
 if name=='Kraš' and re.search(r'krašev\w* ulic|ulic\w* krašev',title,re.I):return False,'street_name'
 if name=='Vindija' and re.search(r'[šs]pilj|neandertal|arheolo|pećin|prapovij|balet|lokalitet',title+' '+lead[:500],re.I):return False,'cave_or_ballet'
 if name=='Dukat' and re.search(r'zlatn\w* dukat|srebrn\w* dukat|dukat\w* zlata',title,re.I):return False,'coin'
 if name=='Dukat' and not re.search(r'Dukat|DUKAT',title) and not re.search(r'mlijek|mliječ|mljek|lactalis',lead[:700],re.I):return False,'coin'
 if name=='Maraska' and re.search(r'^višnja maraska|^maraska, varoš',title,re.I):return False,'fruit_or_neighborhood'
 if name=='Badel 1862' and re.search(r'parkirališt|blok\w* badel|badel\w* blok',title,re.I):return False,'site_name'
 if name=='Zagrebačka pivovara' and not re.search(r'Zagrebačk\w* pivovar|Ožujsko|Molson',title+' '+lead[:700]):return False,'generic_zagreb_brewery'
 if name=='PPK' and (re.search(r'ppk\s+velebit',title+' '+lead[:500],re.I) or not re.search(r'karlov|mesn|kobasic|salama|pivac',title+' '+lead[:500],re.I)):return False,'ppk_other_meaning'
 if SPORT.search(title+' '+lead[:900]) and not BUSINESS.search(title):return False,'sport'
 if name in {'Dukat','Pivac','PPK','Mlinar'} and not BUSINESS.search(title+' '+lead):return False,'ambiguous_name'
 if name=='Kraš' and re.search(r'\bkras(?:a|u|em)?\b',title,re.I) and not re.search(r'(?<!\w)kraš(?:a|u|em)?(?!\w)|napolit|konditor|čokol|dorina',title+' '+lead[:500],re.I):return False,'karst'
 if name in {'Coca-Cola','Heineken','Carlsberg'} and not DOMESTIC.search(title+' '+lead):return False,'foreign_or_generic_brand'
 return True,''

def clusters(df,threshold):
 """Greedy representative clusters, same company, <=7 days, body 3-word cosine.

 Avoid transitive chaining: every added article must match the earliest cluster
 representative directly. This is a repetition proxy, not a count of news events.
 """
 texts=[' '.join(re.findall(r'\w+',normalize(x))[:400]) for x in df.body]
 enough=np.array([len(x.split())>=80 for x in texts])
 vector=TfidfVectorizer(ngram_range=(3,3),min_df=1,max_features=200000,sublinear_tf=True)
 mat=vector.fit_transform(texts)
 dates=pd.to_datetime(df.published).to_numpy()
 firms=[set(x.split('|')) for x in df.companies]
 reps=[]; ids=[]
 for i in range(len(df)):
  eligible=[j for j in reps if enough[i] and enough[j] and (dates[i]-dates[j])/np.timedelta64(1,'D')<=7 and firms[i]&firms[j]]
  selected=None
  if eligible:
   sims=(mat[i]@mat[eligible].T).toarray()[0]
   best=int(sims.argmax())
   if sims[best]>=threshold:selected=eligible[best]
  if selected is None:reps.append(i);selected=i
  ids.append(selected)
 return ids

def main():
 raw=pd.read_parquet(DATA/'candidates.parquet').fillna('')
 raw['title']=raw.title.map(clean);raw['body']=raw.body.map(clean)
 raw['canonical_url']=raw.url.map(canonical)
 raw['publisher_key']=[publisher_key(u,d) for u,d in zip(raw.url,raw.domain)]
 raw['body_len']=raw.body.str.len()
 raw=raw.sort_values(['published','body_len'],ascending=[True,False]).drop_duplicates('publisher_key')
 coverage=pd.read_csv(OUT/'outlet_coverage.csv')
 panel=coverage.groupby('domain').agg(months=('month','nunique'),min_days=('observed_days','min'))
 panel['eligible']=(panel.months==12)&(panel.min_days>=8)
 panel.to_csv(OUT/'panel.csv')
 stable=set(panel.index[panel.eligible])
 decisions=pd.read_csv(ROOT/'data/reference/food_drink_manual_exclusions.csv')
 manual=dict(zip(decisions.doc_id,decisions.reason))
 accepted=[]; excluded=[]
 for r in raw.itertuples():
  doc_id=hashlib.sha256(r.canonical_url.encode()).hexdigest()[:20]
  if doc_id in manual:
   excluded.append(dict(url=r.url,published=r.published,title=r.title,company='',reason=manual[doc_id]));continue
  if (r.domain=='hina.hr' and '/vijest/' not in r.url.lower()) or re.search(r'[-–] Komentari\s*$',r.title):
   excluded.append(dict(url=r.url,published=r.published,title=r.title,company='',reason='disclosure_gallery_video_or_comments'))
   continue
  hit=[];lead_hit=[]
  for name,rx in RX.items():
   title=bool(rx.search(r.title));lead=bool(rx.search(r.body[:900]))
   if not(title or lead):continue
   ok,why=allowed(name,r.title,r.body[:1500])
   if not ok:excluded.append(dict(url=r.url,published=r.published,title=r.title,company=name,reason=why));continue
   if title:hit.append(name)
   if lead:lead_hit.append(name)
  if not hit and not lead_hit:continue
  record=r._asdict();record.pop('Index',None)
  record.update(companies='|'.join(hit),lead_companies='|'.join(lead_hit),stable=r.domain in stable,
                month=r.published[:7],doc_id=hashlib.sha256(r.canonical_url.encode()).hexdigest()[:20])
  for topic,rx in TRX.items():
   topic_text=re.sub(r'\bRadnika (?=Mirko|Habijanec)','',r.title) if topic=='rad i plaće' else r.title
   if topic=='ulaganja i vlasništvo':topic_text=re.sub(r'\bBosqar\s+Invest\b','Bosqar',topic_text,flags=re.I)
   record[topic]=bool(rx.search(topic_text))
  accepted.append(record)
 a=pd.DataFrame(accepted).sort_values(['published','url']).reset_index(drop=True)
 a.to_parquet(DATA/'selected.parquet',index=False)
 pd.DataFrame(excluded).to_csv(DATA/'exclusions.csv',index=False)
 d=a[a.stable & a.companies.ne('')].copy().reset_index(drop=True)
 for threshold in (.75,.85,.95): d[f'cluster_{threshold}']=clusters(d,threshold)
 d.to_parquet(DATA/'headlines.parquet',index=False)
 # Main result tables, only aggregate or hashed evidence leaves private data/.
 monthly=d.groupby('month').agg(articles=('doc_id','size'),outlets=('domain','nunique'))
 den=coverage[coverage.domain.isin(stable)].groupby('month').records.sum()
 monthly['all_outlet_records']=den
 monthly['per_1000_records']=1000*monthly.articles/den
 monthly.to_csv(OUT/'monthly.csv')
 topics=d.groupby('month')[list(TOPICS)].sum().reset_index().melt(id_vars='month',var_name='topic',value_name='articles')
 topics['total_articles']=topics.month.map(monthly.articles)
 topics['share_pct']=100*topics.articles/topics.total_articles
 topics.to_csv(OUT/'topics_monthly.csv',index=False)
 pairs=d.assign(company=d.companies.str.split('|')).explode('company')
 pairs['sector']=pairs.company.map(lambda n:COMPANIES[n][0])
 counts=pairs.groupby(['company','sector']).agg(mentions=('doc_id','size'),outlets=('domain','nunique'),months=('month','nunique')).reset_index().sort_values('mentions',ascending=False)
 for company,(sector,_) in COMPANIES.items():
  if company not in set(counts.company):counts.loc[len(counts)]=[company,sector,0,0,0]
 counts['share_of_pairs_pct']=100*counts.mentions/counts.mentions.sum()
 counts.to_csv(OUT/'companies.csv',index=False)
 pairs.groupby(['company','outlet_type']).size().rename('mentions').reset_index().to_csv(OUT/'company_outlet_types.csv',index=False)
 pairs.groupby(['month','sector']).size().rename('mentions').reset_index().to_csv(OUT/'sector_monthly.csv',index=False)
 pairs.groupby(['month','company']).size().rename('mentions').reset_index().to_csv(OUT/'company_monthly.csv',index=False)
 d.groupby('outlet_type').size().rename('articles').to_csv(OUT/'outlet_types.csv')
 rep=[]
 for threshold in (.75,.85,.95):
  col=f'cluster_{threshold}'; sizes=d.groupby(col).size()
  rep.append(dict(cosine_threshold=threshold,articles=len(d),representatives=len(sizes),
                  articles_in_repeated_groups=int(sizes[sizes>1].sum()),redundant_copies=int((sizes-1).sum()),
                  repeated_share_pct=100*sizes[sizes>1].sum()/len(d)))
 pd.DataFrame(rep).to_csv(OUT/'repetition.csv',index=False)
 # Sensitivity to imposing the stable outlet panel.
 sens=[]
 for label,z in [('headline_all_outlets',a[a.companies.ne('')]),('headline_stable',d)]:
  sens.append(dict(variant=label,articles=len(z),outlets=z.domain.nunique()))
 pd.DataFrame(sens).to_csv(OUT/'selection_sensitivity.csv',index=False)
 # Stratified diagnostic reading sample, with separate top-cluster exemplars.
 sample=d.groupby('month',group_keys=False).sample(n=8,random_state=20261005)
 sample[['doc_id','published','domain','title','companies',*TOPICS,'url']].to_csv(DATA/'inspection_96.csv',index=False)
 top=d.groupby('cluster_0.85').size().nlargest(20)
 d[d['cluster_0.85'].isin(top.index)][['published','domain','title','companies','cluster_0.85','url']].to_csv(DATA/'largest_groups.csv',index=False)
 # The user-supplied two cases may have producers only in the body.
 cases=a[((a.title+' '+a.body.str[:1500]).str.contains('agrolagun',case=False)&a.month.eq('2026-06'))|
         ((a.title+' '+a.body.str[:1500]).str.contains('kraš',case=False)&a.month.eq('2026-02'))]
 cases[['doc_id','published','domain','title','companies','url','body']].to_parquet(DATA/'cases.parquet',index=False)
 audit=dict(candidate_rows=len(pd.read_parquet(DATA/'candidates.parquet')),unique_candidate_urls=len(raw),
  accepted_headline_or_lead=len(a),headline_articles=len(d),company_article_pairs=len(pairs),
  panel_outlets=len(stable),outlets_with_headlines=d.domain.nunique(),
  represented_companies=pairs.company.nunique(),
  exclusion_reasons=dict(Counter(x['reason'] for x in excluded)),
  main_definition='Company name in headline; domestic producer context; stable purposive outlet panel; canonical URL dedup.',
  topics=TOPICS,validation_status='exploratory; deterministic sample inspected separately; recall unknown')
 (OUT/'selection_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(audit,ensure_ascii=False,indent=2))
 print(counts.to_string(index=False));print(monthly.to_string());print(pd.DataFrame(rep).to_string(index=False))

if __name__=='__main__':main()
