"""Write the preliminary research record from the saved result tables."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/tables/food_drink_2026'

def table(df):
    def cell(x):
        return str(x).replace('|', '/')
    rows = [list(df.columns), ['---'] * len(df.columns), *df.astype(str).values.tolist()]
    return '\n'.join('| ' + ' | '.join(map(cell, row)) + ' |' for row in rows)

def main():
    facts = json.loads((ROOT / 'outputs/facts/food_drink_2026.json').read_text(encoding='utf-8'))
    audit = json.loads((OUT / 'selection_audit.json').read_text(encoding='utf-8'))
    macro = json.loads((OUT / 'macro_audit.json').read_text(encoding='utf-8'))
    def n(key, digits=0):
        return f'{facts[key]:,.{digits}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    monthly = pd.read_csv(OUT / 'monthly.csv')
    monthly['per_1000_records'] = monthly.per_1000_records.map(lambda x: f'{x:.3f}')
    companies = pd.read_csv(OUT / 'companies.csv')
    companies['share_of_pairs_pct'] = companies.share_of_pairs_pct.round(2)
    sensitivity = pd.read_csv(OUT / 'cluster_sensitivity.csv')
    sensitivity['podravka_share_pct'] = sensitivity.podravka_share_pct.round(2)
    repetition = pd.read_csv(OUT / 'repetition.csv')
    repetition['repeated_share_pct'] = repetition.repeated_share_pct.round(2)
    topics = pd.read_csv(OUT / 'topics_monthly.csv')
    peaks = topics.loc[topics.groupby('topic').share_pct.idxmax(), ['topic', 'month', 'articles', 'total_articles', 'share_pct']]
    peaks['share_pct'] = peaks.share_pct.round(2)
    text = f'''# Hrana i piće iza naslova — preliminarna analiza

Datum pripreme 5. listopada 2026. Promatrano razdoblje 1. rujna 2025. do 31. kolovoza 2026.

Ovo je istraživačka podloga za [nacrt](article.qmd). Glavni je cilj eksplorativan i deskriptivan pregled sektora u medijskom prostoru. Opisujemo proizvođače, vrste portala, kontinuitet prisutnosti, mjesečne obrasce i konkretne povode. Gospodarski podaci daju kratko objašnjenje poslovne važnosti opaženih vijesti. Taj smjer slijedi autorovu korekciju prvog nacrta.

## Nalazi koji nose pregled

1. **Koncentracija i kontinuitet.** Podravka ima {n('podravka_mentions')} spominjanja, Kraš {n('kras_mentions')}, Mlinar {n('mlinar_mentions')}. Njihov zajednički udio među parovima proizvođač–članak iznosi {n('top_three_pair_share_pct', 1)}%. Podravka i Kraš pojavljuju se svakog mjeseca, dok Mlinar ima {n('mlinar_active_months')} aktivnih mjeseci. Nizak broj za druga imena nije dokaz nevidljivosti njihovih brendova ili proizvoda.
2. **Različita mjesta prisutnosti.** Opći portali donose {n('general_articles')} članaka, poslovni i stručni {n('business_articles')}, lokalni i regionalni {n('local_articles')}. Podravka ima {n('podravka_local_mentions')} lokalnih/regionalnih spominjanja, odnosno {n('podravka_local_share_pct', 1)}% svojih spominjanja. Kraš je najčešće na poslovnim/stručnim portalima, Mlinar na općima. To su obrasci unutar odabranog panela, bez mjerenja čitanosti.
3. **Nekoliko aktivnih razdoblja.** Listopad ima {n('october_articles')} članaka, travanj {n('april_articles')}, srpanj {n('july_articles')}, lipanj {n('june_articles')}. Mlinar se u prosincu pojavljuje u {n('mlinar_december_mentions')} naslova. Mjesečne promjene opisujemo uz provjerene događaje, bez tvrdnje da smo kvantitativno pripisali svaki vrhunac jednom uzroku.
4. **Različiti povodi.** Poslovni rezultati, ulaganja, vlasništvo, radna mjesta i proizvodi daju različite ulaze u sektor. U travnju {n('april_investment_articles')} naslova, odnosno {n('april_investment_share_pct', 1)}%, sadrži riječi povezane s ulaganjima i vlasništvom. Taj rječnik uključuje dionice i dividende. Mjerimo riječi, ne neovisno validirane tematske udjele.
5. **Kraš kao mali pregled unutar velikoga.** Rezultati, pakiranje napolitanki, automatizacija linije, kupnja kompleksa i dionice smjenjuju se kroz godinu. Veljački naslovi o padu dobiti i stabilizaciji ilustriraju različite naglaske iste objave. Kratki financijski kontekst objašnjava njihovu pozadinu; ne postaje zasebna pouka o čitanju bilanci.
6. **Proizvođači pića i pojedinačni događaji.** Agrolaguna ima {n('agrolaguna_mentions')} spominjanja u {n('agrolaguna_active_months')} mjeseca. Lipanjski slučaj bezalkoholnog vina obuhvaća {n('agrolaguna_case_articles')} članaka, s imenom proizvođača u {n('agrolaguna_named_titles')} naslova. Jedna dodatno pronađena objava bez imena ne ulazi u glavni uzorak naslovne vidljivosti. Jamnica i Badel donose primjer vlasničkih pregovora, a pivovare ulaganja i sponzorstva.

## Opisni profili proizvođača

{table(pd.read_csv(OUT / 'company_profiles.csv').fillna(''))}

Profil spaja `companies.csv`, `company_monthly.csv` i `company_outlet_types.csv`. Kod izjednačenog mjesečnog maksimuma tablica prikazuje raniji mjesec. Udio vodeće trojke i udio hrane koriste sve parove proizvođač–članak; mjesečni i ukupni broj članaka svaki članak broje jednom. Izlaz `outlet_monthly.csv` daje podatke za novi mjesečni grafikon.

## Izvor i konstrukcija uzorka

Izvor je lokalni `determDB_merged.duckdb`, tablica `media_data_all`, otvorena isključivo s `read_only=True`. Koriste se `DATE` za datum objave, `SOURCE_TYPE` za ograničenje na `web`, `TITLE` za naziv proizvođača i leksičke oznake, `URL` za domenu i identitet članka, `ITEM_ID` za razrješenje preklapanja u obuhvatu portala te `FULL_TEXT` za kontekst i sličnost teksta. `LANGUAGES` i `LOCATIONS` zadržani su u lokalnom izvodu, ali se ne koriste za klasifikaciju, geografski filtar ili nalaze. Autor, doseg, sentiment i interakcije nisu korišteni.

Okvir proizvođača dolazi iz EIZ-ovih tablica 6 i 8, vodeća društva prema prihodima za 2024. Obuhvaća {n('frame_companies')} imena. Nije iscrpan popis industrije i ne pretražuje sve njihove robne marke. Strane vijesti o globalnim grupama bez relevantnog domaćeg konteksta uklanjaju se. Domaće objave o brendu, grupi, vlasnicima, prodajnim mjestima i sponzorstvima mogu ostati; ne predstavljaju nužno proizvodnju pravne osobe iz EIZ-ove tablice.

Popis portala namjerno uključuje opće, poslovne/stručne i lokalne/regionalne izvore. Točan popis i ručna podjela nalaze se u `OUTLETS` u skripti za izvoz. Poddomene pripadaju najduljoj definiranoj domeni. Neki portali zato uključuju specijalizirane i lokalne poddomene unutar opće kategorije. Kategorije nisu mjere dosega ili publike.

U opaženom prozoru podatke imaju 54 domene. Panel zadržava {n('panel_outlets')} domena koje imaju zapise u svih 12 mjeseci i barem osam opaženih dana u svakom mjesecu. U konačnom izboru članke ima {n('active_outlets')} domena. Taj prag sprječava najgrublje ulaske i izlaske izvora, ali ne dokazuje potpunost prikupljanja. Stabilnost nije isto što i jednaka dnevna pokrivenost.

Široka pretraga daje {audit['candidate_rows']:,} kandidatskih zapisa. Nakon objedinjavanja istog članka ostaje {audit['unique_candidate_urls']:,} kandidata. Pročišćavanje završava s **{n('n_articles')} članaka i {n('n_pairs')} parova proizvođač–članak** u glavnom panelu. Kandidatski brojevi uključuju široka podudaranja koja se ne prihvaćaju kao tvrtke. Dnevnik isključenja može sadržavati više odluka po članku i nije jednostavan uzastopni tok redaka.

Duplikati istog članka uklanjaju se prema kanoniziranom URL-u bez upita/fragmenta, a za odabrane velike portale prema identifikatoru članka u URL-u. Zadržava se najraniji datum, a pri istom datumu najdulji tekst. Objave na različitim portalima ostaju zasebne objave. Kontekstualna pravila uklanjaju sportske rezultate, osobe istog prezimena, dukate kao novčiće, špilju Vindija, generička zanimanja i druga pogrešna podudaranja. Ručne iznimke imaju hash i razlog u `data/reference/food_drink_manual_exclusions.csv`.

Pregledan je dijagnostički uzorak od osam naslova po mjesecu, veliki skupovi sličnih tekstova i ciljano problematična imena. Pravila su popravljana nakon tog čitanja. To je razvojna provjera, **nije neovisna procjena preciznosti**; odziv i preostala pogreška nisu izmjereni. Puni licencirani tekstovi ostaju u ignoriranom `data/processed/food_drink_2026/`.

## Mjesečni rezultati

`articles` broji odabrane jedinstvene članke. `all_outlet_records` broji sve zabilježene web zapise iz istog panela u mjesecu, uz razrješenje preklapajućih domena. Nazivnik nije zasebno očišćen popis svih jedinstvenih novinskih članaka. `per_1000_records` je normalizacija na tisuću zapisa baze, a ne udio publike ili svih objavljenih vijesti.

{table(monthly)}

Izvor tablice `outputs/tables/food_drink_2026/monthly.csv`.

## Tvrtke

Svaki članak broji se jednom za svako imenovano poduzeće. Nule ostaju vidljive u okviru i ne znače potpunu medijsku nevidljivost društva ili njegovih proizvoda.

{table(companies)}

Izvor `companies.csv`. Podsektorski mjesečni parovi nalaze se u `sector_monthly.csv`; zajednički članak može pridonijeti obama podsektorima.

## Tematske oznake i njihove granice

Pet skupina temelji se na regularnim izrazima nad naslovom. Jedan naslov može dobiti više oznaka ili nijednu. Rječnici i pravila spremljeni su u `selection_audit.json` i skripti `food_drink_2026_build.py`. Izraz *Bosqar Invest* uklonjen je prije traženja investicijskih riječi kako sam naziv ne bi stvorio oznaku.

Oznake nisu potpuna semantička analiza. Primjerice, naslov može opisati prodaju tvrtke bez riječi koje zahvaća rječnik, a riječ *brend* može se pojaviti u priči o bojkotu. Iz toga slijedi da mjerimo **udio naslova s tim riječima**, bez tvrdnje da smo izmjerili udio svih članaka o određenoj temi. Prije snažnijih tematskih zaključaka treba neovisno ručno kodirati reprezentativni uzorak naslova i tekstova.

{table(peaks)}

Tablica prikazuje mjesečni maksimum svake leksičke skupine iz `topics_monthly.csv`.

## Osjetljivost na obuhvat i ponavljanje

{table(pd.read_csv(OUT / 'selection_sensitivity.csv'))}

Za sličnost koristimo prvih 400 riječi očišćenog teksta, TF–IDF trigrame, najmanje 80 riječi i najviše sedam dana razmaka uz zajedničko ime proizvođača. Svaki član grupe mora prijeći prag prema prvom predstavniku; nema tranzitivnog povezivanja. Ovo nije ručno identificiranje događaja, detektor priopćenja ni dokaz plaćene objave.

{table(repetition)}

`articles_in_repeated_groups` uključuje i prvi član grupe. `redundant_copies` broji samo preostale članove. Velik raspon rezultata kroz pragove razlog je da u post ne unesemo jednu prividno čvrstu stopu ponavljanja.

{table(sensitivity)}

Podravka vodi, a listopad ostaje mjesec s najviše predstavnika pri sva tri praga. To podupire ta dva nalaza unutar zadanog okvira. Ne uklanja pristranost izbora poduzeća ili portala.

## Gospodarski izvori i provjere

- [EIZ, Hrana i piće, travanj 2026.](https://www.eizg.hr/userdocsimages/publikacije/serijske-publikacije/sektorske-analize/SA_Hrana-i-pice_2026_HR_f.pdf), Petra Palić, Sektorske analize 130. Vizualno provjereni godišnja proizvodnja, tablica plaća, trgovinska tablica i okviri tvrtki.
- [DZS, prosinac 2025.](https://podaci.dzs.hr/2025/hr/97267), tablica II.1. Izvorni godišnji indeksi reproduciraju EIZ-ovih {n('hrana_production_2025', 1)}% za hranu i {n('piće_production_2025', 1)}% za pića. Ne miješati ih s kalendarski prilagođenim godišnjim stopama.
- [DZS, veljača 2026.](https://podaci.dzs.hr/2026/hr/121409), tablica I.2, objava 31. ožujka, za mjesece rujan 2025. do veljače 2026.; [DZS, kolovoz 2026.](https://podaci.dzs.hr/2026/hr/120999), tablica I.2, objava 30. rujna, za ožujak do kolovoza 2026. Mjesečne međugodišnje stope su kalendarski prilagođene; dostupne su u `production_monthly.csv`, uz datum izdanja za svaku točku. Spajamo dva izdanja, a ne potpunu arhivu prvih objava za svaki mjesec.
- Plaće su prosječne mjesečne bruto plaće u 2025. Uvoz i izvoz obuhvaćaju **hranu, piće i duhan**. Izvoz pokriva {n('trade_coverage_pct', 1)}% uvoza. Tu širu skupinu ne predstavljamo kao tržište bezalkoholnog vina.
- Kraš i Mlinar imaju zasebne, izvoru pripisane prijepise u `data/reference/food_drink_company_facts.csv`. Krašev godišnji i polugodišnji rezultat su tadašnje nerevidirane konsolidirane objave. Mlinarovih do {n('mlinar_investment_ceiling')} milijuna eura jest najavljeni financijski krug; {n('mlinar_ebrd_first_phase')} milijuna prva je faza EBRD-a. Ni jedno ne predstavlja dokaz već dovršenih kapitalnih ulaganja.

Problemi izvornog izvještaja izdvojeni su, a sporne brojke nisu prenesene u post:

{chr(10).join('- ' + issue for issue in macro['source_issues_excluded'])}

## Što nije preuzeto iz početne ideje

Početni brief navodi 32,9% tekstova u sličnim skupinama i 17 Facebook objava s 36,4% interakcija. Izvorni izvod, pravila izbora i izvještaj za te brojke nisu dostavljeni. Novi web uzorak ima izričito drukčiju definiciju. Te brojke nisu reproducirane, nisu zamijenjene približnim podudaranjem i nisu unesene u nacrt. Facebook ostaje izvan ove analize.

Nisu procjenjivani sentiment, izvori izjava ili čitateljska uvjerenja. Bojkot iz siječnja 2025. izvan je glavnog prozora. Potrošačke cijene, turizam i stvarni učinci preuzimanja traže zasebnu analizu ako post dobije taj kut.

## Uredničke odluke i grafike

Autor je odabrao eksplorativan, deskriptivan pregled i zatim odobrio završno poliranje i objavu. Prethodne oznake za odluku o glavnom kutu povučene su nakon te korekcije. Posljednji `[KUT]` uz završni naglasak o lokalnoj ulozi uklonjen je nakon odobrenja postojeće deskriptivne verzije; završetku nije dodana nova interpretacija. Autor nije dodijeljen, pa ostaje `author: []`. Završna verzija ima `draft: false` i `freeze: auto` za objavu bez privatnih podataka.

Tri grafikona čitaju spremljene tablice i paletu `R/house_style.R`. Tvrtke koriste vodoravne stupce od nule, složene po vrsti portala. Mjesečni pregled koristi stupce ukupnog broja članaka, podijeljene istim bojama po vrsti portala. Zajednička početna crta daje preciznu usporedbu ukupnih brojeva; razine unutar stupca opisuju sastav. Linija bi dobro prikazala kretanje ukupnog broja, ali slabije sastav. Teme zadržavaju pet malih grafikona s jednakom postotnom skalom. Usporedba medijskih i proizvodnih kalendara više nije prikazana u postu; pripadni gospodarski podaci ostaju u istraživačkim izlazima.

Detalji izvođenja nalaze se u [README-u](README.md). Datoteke `claim_ledger.csv`, `macro_facts.csv`, `company_facts.csv`, `agrolaguna_case.csv` i `kras_case.csv` povezuju nalaze s tablicama i javnim izvorima. Provjera izračuna je u `quality_reports/2026-10-05_food-drink-verification.json`.
'''
    (ROOT / 'drafts/food-drink-2026/analysis.md').write_text(text, encoding='utf-8')
    print('Wrote preliminary analysis from saved outputs.')

if __name__ == '__main__':
    main()
