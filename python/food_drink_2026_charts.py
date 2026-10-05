"""Three house-style figures, sourced exclusively from saved analysis tables."""
from pathlib import Path
import re
import shutil
import random
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd

random.seed(20261005);np.random.seed(20261005)
ROOT=Path(__file__).resolve().parents[1]
TABLES=ROOT/'outputs/tables/food_drink_2026'
OUT=ROOT/'outputs/figures/food_drink_2026'
POST=ROOT/'posts/2026-10-hrana-pice-iza-naslova'
PAL=dict(re.findall(r'(\w+)\s*=\s*"(#[A-Fa-f0-9]{6})"',(ROOT/'R/house_style.R').read_text(encoding='utf-8')))
MONTHS=['ruj.','lis.','stu.','pro.','sij.','velj.','ožu.','tra.','svi.','lip.','srp.','kol.']

def hr(v,d=1):return f'{v:,.{d}f}'.replace(',','X').replace('.',',').replace('X','.')
def theme_house(ax,horizontal=False):
 for spine in ax.spines.values():spine.set_visible(False)
 ax.tick_params(length=0,labelsize=9,pad=7)
 ax.set_axisbelow(True);ax.grid(axis='x' if horizontal else 'y',color=PAL['hair'],linewidth=.6)

def save(fig,name):
 OUT.mkdir(parents=True,exist_ok=True);POST.mkdir(parents=True,exist_ok=True)
 fig.savefig(OUT/name,dpi=180,facecolor=PAL['paper']);plt.close(fig)
 shutil.copyfile(OUT/name,POST/name)

def calendar_chart():
 d=pd.read_csv(TABLES/'monthly.csv')
 p=pd.read_csv(TABLES/'outlet_monthly.csv').pivot(index='month',columns='outlet_type',values='articles').reindex(d.month).fillna(0)
 fig,ax=plt.subplots(figsize=(10,6.6))
 fig.subplots_adjust(left=.10,right=.95,top=.72,bottom=.23)
 x=np.arange(len(d));bottom=np.zeros(len(d))
 types=['opći','poslovni i stručni','lokalni i regionalni']
 for typ,color in zip(types,[PAL['accent'],PAL['ink'],PAL['muted']]):
  values=p[typ].to_numpy()
  ax.bar(x,values,bottom=bottom,width=.65,color=color,label=typ)
  bottom+=values
 for i,value in enumerate(bottom):ax.text(i,value+4,hr(value,0),ha='center',fontsize=9)
 assert np.array_equal(bottom,d.articles.to_numpy())
 ax.set_ylim(0,max(bottom)*1.17);ax.set_xticks(x,MONTHS)
 ax.yaxis.set_major_formatter(FuncFormatter(lambda x,_:hr(x,0)))
 theme_house(ax)
 fig.text(.055,.95,'Najviše odabranih objava donosi listopad',weight='bold',fontsize=14)
 fig.text(.055,.89,'Broj članaka s nazivom proizvođača u naslovu · prema vrsti portala',fontsize=10,color=PAL['muted'])
 handles,labels=ax.get_legend_handles_labels()
 fig.legend(handles,labels,loc='upper left',bbox_to_anchor=(.055,.84),ncol=3,frameon=False,fontsize=8)
 fig.text(.055,.14,'Rujan 2025. → kolovoz 2026. · isti panel odabranih portala.',fontsize=8,color=PAL['muted'])
 fig.text(.055,.09,'Članak se broji jednom, i kada u naslovu imenuje više proizvođača.',fontsize=8,color=PAL['muted'])
 fig.text(.055,.045,'Izvor · Determ; odabrani proizvođači i portali; vlastiti izračun.',fontsize=8,color=PAL['muted'])
 save(fig,'01_kalendari.png')

def topics_chart():
 d=pd.read_csv(TABLES/'topics_monthly.csv')
 topics=['rezultati','ulaganja i vlasništvo','cijene i troškovi','rad i plaće','proizvodi i promocija']
 fig,axes=plt.subplots(5,1,figsize=(10,10),sharex=True,sharey=True)
 fig.subplots_adjust(left=.10,right=.94,top=.86,bottom=.16,hspace=.62)
 limit=max(50,np.ceil(d.share_pct.max()/10)*10)
 for ax,topic in zip(axes,topics):
  s=d[d.topic.eq(topic)].sort_values('month');x=np.arange(len(s))
  ax.plot(x,s.share_pct,color=PAL['accent'],marker='o',ms=4,lw=1.8)
  ax.set_ylim(0,limit);ax.set_yticks([0,limit/2,limit],[f'{int(v)}%' for v in [0,limit/2,limit]])
  ax.set_title(topic.capitalize(),loc='left',fontsize=10,pad=7)
  peak=int(s.share_pct.to_numpy().argmax());val=s.share_pct.iloc[peak]
  ax.annotate(hr(val,0)+'%',(peak,val),xytext=(0,8 if val<limit*.8 else -15),textcoords='offset points',ha='center',fontsize=9)
  theme_house(ax)
 axes[-1].set_xticks(np.arange(12),MONTHS)
 fig.text(.055,.954,'Ulaganja i vlasništvo ističu se u proljetnim naslovima',fontsize=14,weight='bold')
 fig.text(.055,.919,'Udio naslova s riječima povezanima s temom · isti panel portala',fontsize=10,color=PAL['muted'])
 fig.text(.055,.103,'Jedan naslov može sadržavati više tema. Udio se računa među svim odabranim naslovima.',fontsize=8,color=PAL['muted'])
 fig.text(.055,.07,'Riječ je o preliminarnim leksičkim oznakama, bez ocjenjivanja tona teksta.',fontsize=8,color=PAL['muted'])
 fig.text(.055,.035,'Izvor · Determ; rujan 2025. → kolovoz 2026.; vlastiti izračun.',fontsize=8,color=PAL['muted'])
 save(fig,'02_teme.png')

def companies_chart():
 d=pd.read_csv(TABLES/'companies.csv');t=pd.read_csv(TABLES/'company_outlet_types.csv')
 top=d.company.head(10).tolist();types=['opći','poslovni i stručni','lokalni i regionalni']
 p=t.pivot_table(index='company',columns='outlet_type',values='mentions',aggfunc='sum',fill_value=0).reindex(top)
 fig,ax=plt.subplots(figsize=(10,7.4));fig.subplots_adjust(left=.28,right=.9,top=.75,bottom=.21)
 left=np.zeros(len(top));colors=[PAL['accent'],PAL['ink'],PAL['muted']]
 for typ,col in zip(types,colors):
  y=p[typ] if typ in p else np.zeros(len(top))
  ax.barh(np.arange(len(top)),y,left=left,height=.64,label=typ,color=col);left+=y
 for i,n in enumerate(left):ax.text(n+max(left)*.015,i,hr(n,0),va='center',fontsize=9)
 ax.set_yticks(np.arange(len(top)),top);ax.invert_yaxis();ax.set_xlim(0,max(left)*1.16)
 ax.xaxis.set_major_formatter(FuncFormatter(lambda v,_:hr(v,0)));theme_house(ax,horizontal=True)
 fig.text(.055,.95,f'{top[0]} je najčešće imenovan proizvođač',fontsize=14,weight='bold')
 fig.text(.055,.90,'Deset najvidljivijih među odabranih 20 proizvođača · spominjanja u naslovima',fontsize=10,color=PAL['muted'])
 handles,labels=ax.get_legend_handles_labels();fig.legend(handles,labels,loc='upper left',bbox_to_anchor=(.055,.855),ncol=3,frameon=False,fontsize=8)
 fig.text(.055,.135,'Jedno spominjanje po proizvođaču i članku. Članak može imenovati više proizvođača.',fontsize=8,color=PAL['muted'])
 fig.text(.055,.095,'Nazivi obuhvaćaju i grupu ili brend; ovo nisu tržišni udjeli ni rang ekonomskog značaja.',fontsize=8,color=PAL['muted'])
 fig.text(.055,.05,'Izvori · Determ; okvir proizvođača prema EIZ-u, Sektorske analize 130, tablice 6 i 8.',fontsize=8,color=PAL['muted'])
 save(fig,'03_proizvodaci.png')

def main():
 mpl.rcParams.update({'font.family':'DejaVu Sans Mono','font.size':10,'text.color':PAL['ink'],
  'axes.facecolor':PAL['paper'],'figure.facecolor':PAL['paper'],'axes.labelcolor':PAL['ink'],
  'xtick.color':PAL['muted'],'ytick.color':PAL['muted']})
 calendar_chart();topics_chart();companies_chart()
 print('Rendered three figures from saved outputs.')

if __name__=='__main__':main()
