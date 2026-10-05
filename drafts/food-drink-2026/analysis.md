# Hrana i piće iza naslova — preliminarna analiza

Datum pripreme 5. listopada 2026. Promatrano razdoblje 1. rujna 2025. do 31. kolovoza 2026.

Ovo je istraživačka podloga za [nacrt](article.qmd). Glavni je cilj eksplorativan i deskriptivan pregled sektora u medijskom prostoru. Opisujemo proizvođače, vrste portala, kontinuitet prisutnosti, mjesečne obrasce i konkretne povode. Gospodarski podaci daju kratko objašnjenje poslovne važnosti opaženih vijesti. Taj smjer slijedi autorovu korekciju prvog nacrta.

## Nalazi koji nose pregled

1. **Koncentracija i kontinuitet.** Podravka ima 526 spominjanja, Kraš 174, Mlinar 115. Njihov zajednički udio među parovima proizvođač–članak iznosi 63,6%. Podravka i Kraš pojavljuju se svakog mjeseca, dok Mlinar ima 11 aktivnih mjeseci. Nizak broj za druga imena nije dokaz nevidljivosti njihovih brendova ili proizvoda.
2. **Različita mjesta prisutnosti.** Opći portali donose 445 članaka, poslovni i stručni 397, lokalni i regionalni 394. Podravka ima 258 lokalnih/regionalnih spominjanja, odnosno 49,0% svojih spominjanja. Kraš je najčešće na poslovnim/stručnim portalima, Mlinar na općima. To su obrasci unutar odabranog panela, bez mjerenja čitanosti.
3. **Nekoliko aktivnih razdoblja.** Listopad ima 187 članaka, travanj 148, srpanj 143, lipanj 141. Mlinar se u prosincu pojavljuje u 34 naslova. Mjesečne promjene opisujemo uz provjerene događaje, bez tvrdnje da smo kvantitativno pripisali svaki vrhunac jednom uzroku.
4. **Različiti povodi.** Poslovni rezultati, ulaganja, vlasništvo, radna mjesta i proizvodi daju različite ulaze u sektor. U travnju 57 naslova, odnosno 38,5%, sadrži riječi povezane s ulaganjima i vlasništvom. Taj rječnik uključuje dionice i dividende. Mjerimo riječi, ne neovisno validirane tematske udjele.
5. **Kraš kao mali pregled unutar velikoga.** Rezultati, pakiranje napolitanki, automatizacija linije, kupnja kompleksa i dionice smjenjuju se kroz godinu. Veljački naslovi o padu dobiti i stabilizaciji ilustriraju različite naglaske iste objave. Kratki financijski kontekst objašnjava njihovu pozadinu; ne postaje zasebna pouka o čitanju bilanci.
6. **Proizvođači pića i pojedinačni događaji.** Agrolaguna ima 24 spominjanja u 4 mjeseca. Lipanjski slučaj bezalkoholnog vina obuhvaća 10 članaka, s imenom proizvođača u 9 naslova. Jedna dodatno pronađena objava bez imena ne ulazi u glavni uzorak naslovne vidljivosti. Jamnica i Badel donose primjer vlasničkih pregovora, a pivovare ulaganja i sponzorstva.

## Opisni profili proizvođača

| company | mentions | months | outlets | peak_month | peak_mentions | leading_outlet_type | leading_outlet_mentions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Podravka | 526 | 12 | 34 | 2025-10 | 112 | lokalni i regionalni | 258 |
| Kraš | 174 | 12 | 27 | 2026-04 | 37 | poslovni i stručni | 86 |
| Mlinar | 115 | 11 | 31 | 2025-12 | 34 | opći | 55 |
| PIK Vrbovec | 100 | 8 | 29 | 2026-04 | 31 | opći | 52 |
| Pivac | 81 | 12 | 28 | 2025-10 | 22 | opći | 33 |
| Jamnica | 56 | 8 | 22 | 2026-02 | 11 | opći | 28 |
| Ledo | 43 | 9 | 18 | 2026-06 | 16 | poslovni i stručni | 17 |
| Badel 1862 | 41 | 11 | 21 | 2026-06 | 17 | poslovni i stručni | 19 |
| Coca-Cola | 40 | 11 | 16 | 2026-01 | 8 | opći | 19 |
| Agrolaguna | 24 | 4 | 16 | 2026-04 | 9 | poslovni i stručni | 10 |
| Heineken | 17 | 4 | 11 | 2026-07 | 12 | poslovni i stručni | 8 |
| Maraska | 16 | 9 | 7 | 2025-09 | 4 | opći | 6 |
| Dukat | 15 | 5 | 11 | 2026-03 | 5 | opći | 11 |
| Carlsberg | 13 | 6 | 7 | 2026-06 | 5 | lokalni i regionalni | 9 |
| Vindija | 9 | 7 | 5 | 2025-09 | 2 | lokalni i regionalni | 4 |
| Zagrebačka pivovara | 6 | 4 | 5 | 2025-12 | 3 | poslovni i stručni | 4 |
| Arivera fruit | 4 | 3 | 3 | 2025-10 | 2 | poslovni i stručni | 3 |
| Pivovara Daruvar | 2 | 2 | 1 | 2026-02 | 1 | poslovni i stručni | 2 |
| PPK | 0 | 0 | 0 |  | 0 |  | 0 |
| Slavonija slad | 0 | 0 | 0 |  | 0 |  | 0 |

Profil spaja `companies.csv`, `company_monthly.csv` i `company_outlet_types.csv`. Kod izjednačenog mjesečnog maksimuma tablica prikazuje raniji mjesec. Udio vodeće trojke i udio hrane koriste sve parove proizvođač–članak; mjesečni i ukupni broj članaka svaki članak broje jednom. Izlaz `outlet_monthly.csv` daje podatke za novi mjesečni grafikon.

## Izvor i konstrukcija uzorka

Izvor je lokalni arhiv članaka s odabranih web portala, tablica `media_data_all`, otvorena isključivo s `read_only=True`. Koriste se `DATE` za datum objave, `SOURCE_TYPE` za ograničenje na `web`, `TITLE` za naziv proizvođača i leksičke oznake, `URL` za domenu i identitet članka, `ITEM_ID` za razrješenje preklapanja u obuhvatu portala te `FULL_TEXT` za kontekst i sličnost teksta. `LANGUAGES` i `LOCATIONS` zadržani su u lokalnom izvodu, ali se ne koriste za klasifikaciju, geografski filtar ili nalaze. Autor, doseg, sentiment i interakcije nisu korišteni.

Okvir proizvođača dolazi iz EIZ-ovih tablica 6 i 8, vodeća društva prema prihodima za 2024. Obuhvaća 20 imena. Nije iscrpan popis industrije i ne pretražuje sve njihove robne marke. Strane vijesti o globalnim grupama bez relevantnog domaćeg konteksta uklanjaju se. Domaće objave o brendu, grupi, vlasnicima, prodajnim mjestima i sponzorstvima mogu ostati; ne predstavljaju nužno proizvodnju pravne osobe iz EIZ-ove tablice.

Popis portala namjerno uključuje opće, poslovne/stručne i lokalne/regionalne izvore. Točan popis i ručna podjela nalaze se u `OUTLETS` u skripti za izvoz. Poddomene pripadaju najduljoj definiranoj domeni. Neki portali zato uključuju specijalizirane i lokalne poddomene unutar opće kategorije. Kategorije nisu mjere dosega ili publike.

U opaženom prozoru podatke imaju 54 domene. Panel zadržava 46 domena koje imaju zapise u svih 12 mjeseci i barem osam opaženih dana u svakom mjesecu. U konačnom izboru članke ima 42 domena. Taj prag sprječava najgrublje ulaske i izlaske izvora, ali ne dokazuje potpunost prikupljanja. Stabilnost nije isto što i jednaka dnevna pokrivenost.

Široka pretraga daje 7,156 kandidatskih zapisa. Nakon objedinjavanja istog članka ostaje 7,075 kandidata. Pročišćavanje završava s **1.236 članaka i 1.282 parova proizvođač–članak** u glavnom panelu. Kandidatski brojevi uključuju široka podudaranja koja se ne prihvaćaju kao tvrtke. Dnevnik isključenja može sadržavati više odluka po članku i nije jednostavan uzastopni tok redaka.

Duplikati istog članka uklanjaju se prema kanoniziranom URL-u bez upita/fragmenta, a za odabrane velike portale prema identifikatoru članka u URL-u. Zadržava se najraniji datum, a pri istom datumu najdulji tekst. Objave na različitim portalima ostaju zasebne objave. Kontekstualna pravila uklanjaju sportske rezultate, osobe istog prezimena, dukate kao novčiće, špilju Vindija, generička zanimanja i druga pogrešna podudaranja. Ručne iznimke imaju hash i razlog u `data/reference/food_drink_manual_exclusions.csv`.

Pregledan je dijagnostički uzorak od osam naslova po mjesecu, veliki skupovi sličnih tekstova i ciljano problematična imena. Pravila su popravljana nakon tog čitanja. To je razvojna provjera, **nije neovisna procjena preciznosti**; odziv i preostala pogreška nisu izmjereni. Puni licencirani tekstovi ostaju u ignoriranom `data/processed/food_drink_2026/`.

## Mjesečni rezultati

`articles` broji odabrane jedinstvene članke. `all_outlet_records` broji sve zabilježene web zapise iz istog panela u mjesecu, uz razrješenje preklapajućih domena. Nazivnik nije zasebno očišćen popis svih jedinstvenih novinskih članaka. `per_1000_records` je normalizacija na tisuću zapisa baze, a ne udio publike ili svih objavljenih vijesti.

| month | articles | outlets | all_outlet_records | per_1000_records |
| --- | --- | --- | --- | --- |
| 2025-09 | 82 | 26 | 106091 | 0.773 |
| 2025-10 | 187 | 35 | 115418 | 1.620 |
| 2025-11 | 69 | 27 | 106912 | 0.645 |
| 2025-12 | 134 | 33 | 106743 | 1.255 |
| 2026-01 | 39 | 19 | 107839 | 0.362 |
| 2026-02 | 112 | 25 | 101565 | 1.103 |
| 2026-03 | 65 | 24 | 117035 | 0.555 |
| 2026-04 | 148 | 33 | 109889 | 1.347 |
| 2026-05 | 86 | 28 | 112710 | 0.763 |
| 2026-06 | 141 | 32 | 112208 | 1.257 |
| 2026-07 | 143 | 30 | 108142 | 1.322 |
| 2026-08 | 30 | 13 | 98017 | 0.306 |

Izvor tablice `outputs/tables/food_drink_2026/monthly.csv`.

## Tvrtke

Svaki članak broji se jednom za svako imenovano poduzeće. Nule ostaju vidljive u okviru i ne znače potpunu medijsku nevidljivost društva ili njegovih proizvoda.

| company | sector | mentions | outlets | months | share_of_pairs_pct |
| --- | --- | --- | --- | --- | --- |
| Podravka | hrana | 526 | 34 | 12 | 41.03 |
| Kraš | hrana | 174 | 27 | 12 | 13.57 |
| Mlinar | hrana | 115 | 31 | 11 | 8.97 |
| PIK Vrbovec | hrana | 100 | 29 | 8 | 7.8 |
| Pivac | hrana | 81 | 28 | 12 | 6.32 |
| Jamnica | piće | 56 | 22 | 8 | 4.37 |
| Ledo | hrana | 43 | 18 | 9 | 3.35 |
| Badel 1862 | piće | 41 | 21 | 11 | 3.2 |
| Coca-Cola | piće | 40 | 16 | 11 | 3.12 |
| Agrolaguna | piće | 24 | 16 | 4 | 1.87 |
| Heineken | piće | 17 | 11 | 4 | 1.33 |
| Maraska | piće | 16 | 7 | 9 | 1.25 |
| Dukat | hrana | 15 | 11 | 5 | 1.17 |
| Carlsberg | piće | 13 | 7 | 6 | 1.01 |
| Vindija | hrana | 9 | 5 | 7 | 0.7 |
| Zagrebačka pivovara | piće | 6 | 5 | 4 | 0.47 |
| Arivera fruit | hrana | 4 | 3 | 3 | 0.31 |
| Pivovara Daruvar | piće | 2 | 1 | 2 | 0.16 |
| PPK | hrana | 0 | 0 | 0 | 0.0 |
| Slavonija slad | piće | 0 | 0 | 0 | 0.0 |

Izvor `companies.csv`. Podsektorski mjesečni parovi nalaze se u `sector_monthly.csv`; zajednički članak može pridonijeti obama podsektorima.

## Tematske oznake i njihove granice

Pet skupina temelji se na regularnim izrazima nad naslovom. Jedan naslov može dobiti više oznaka ili nijednu. Rječnici i pravila spremljeni su u `selection_audit.json` i skripti `food_drink_2026_build.py`. Izraz *Bosqar Invest* uklonjen je prije traženja investicijskih riječi kako sam naziv ne bi stvorio oznaku.

Oznake nisu potpuna semantička analiza. Primjerice, naslov može opisati prodaju tvrtke bez riječi koje zahvaća rječnik, a riječ *brend* može se pojaviti u priči o bojkotu. Iz toga slijedi da mjerimo **udio naslova s tim riječima**, bez tvrdnje da smo izmjerili udio svih članaka o određenoj temi. Prije snažnijih tematskih zaključaka treba neovisno ručno kodirati reprezentativni uzorak naslova i tekstova.

| topic | month | articles | total_articles | share_pct |
| --- | --- | --- | --- | --- |
| cijene i troškovi | 2025-10 | 12 | 187 | 6.42 |
| proizvodi i promocija | 2026-01 | 10 | 39 | 25.64 |
| rad i plaće | 2025-11 | 15 | 69 | 21.74 |
| rezultati | 2026-02 | 23 | 112 | 20.54 |
| ulaganja i vlasništvo | 2026-04 | 57 | 148 | 38.51 |

Tablica prikazuje mjesečni maksimum svake leksičke skupine iz `topics_monthly.csv`.

## Osjetljivost na obuhvat i ponavljanje

| variant | articles | outlets |
| --- | --- | --- |
| headline_all_outlets | 1276 | 46 |
| headline_stable | 1236 | 42 |

Za sličnost koristimo prvih 400 riječi očišćenog teksta, TF–IDF trigrame, najmanje 80 riječi i najviše sedam dana razmaka uz zajedničko ime proizvođača. Svaki član grupe mora prijeći prag prema prvom predstavniku; nema tranzitivnog povezivanja. Ovo nije ručno identificiranje događaja, detektor priopćenja ni dokaz plaćene objave.

| cosine_threshold | articles | representatives | articles_in_repeated_groups | redundant_copies | repeated_share_pct |
| --- | --- | --- | --- | --- | --- |
| 0.75 | 1236 | 980 | 391 | 256 | 31.63 |
| 0.85 | 1236 | 1093 | 229 | 143 | 18.53 |
| 0.95 | 1236 | 1203 | 56 | 33 | 4.53 |

`articles_in_repeated_groups` uključuje i prvi član grupe. `redundant_copies` broji samo preostale članove. Velik raspon rezultata kroz pragove razlog je da u post ne unesemo jednu prividno čvrstu stopu ponavljanja.

| variant | articles | leading_company | podravka_share_pct | peak_article_month |
| --- | --- | --- | --- | --- |
| collapse_representative_cosine_0.75 | 980 | Podravka | 43.78 | 2025-10 |
| collapse_representative_cosine_0.85 | 1093 | Podravka | 42.87 | 2025-10 |
| collapse_representative_cosine_0.95 | 1203 | Podravka | 41.75 | 2025-10 |

Podravka vodi, a listopad ostaje mjesec s najviše predstavnika pri sva tri praga. To podupire ta dva nalaza unutar zadanog okvira. Ne uklanja pristranost izbora poduzeća ili portala.

## Gospodarski izvori i provjere

- [EIZ, Hrana i piće, travanj 2026.](https://www.eizg.hr/userdocsimages/publikacije/serijske-publikacije/sektorske-analize/SA_Hrana-i-pice_2026_HR_f.pdf), Petra Palić, Sektorske analize 130. Vizualno provjereni godišnja proizvodnja, tablica plaća, trgovinska tablica i okviri tvrtki.
- [DZS, prosinac 2025.](https://podaci.dzs.hr/2025/hr/97267), tablica II.1. Izvorni godišnji indeksi reproduciraju EIZ-ovih 1,6% za hranu i 8,5% za pića. Ne miješati ih s kalendarski prilagođenim godišnjim stopama.
- [DZS, veljača 2026.](https://podaci.dzs.hr/2026/hr/121409), tablica I.2, objava 31. ožujka, za mjesece rujan 2025. do veljače 2026.; [DZS, kolovoz 2026.](https://podaci.dzs.hr/2026/hr/120999), tablica I.2, objava 30. rujna, za ožujak do kolovoza 2026. Mjesečne međugodišnje stope su kalendarski prilagođene; dostupne su u `production_monthly.csv`, uz datum izdanja za svaku točku. Spajamo dva izdanja, a ne potpunu arhivu prvih objava za svaki mjesec.
- Plaće su prosječne mjesečne bruto plaće u 2025. Uvoz i izvoz obuhvaćaju **hranu, piće i duhan**. Izvoz pokriva 48,4% uvoza. Tu širu skupinu ne predstavljamo kao tržište bezalkoholnog vina.
- Kraš i Mlinar imaju zasebne, izvoru pripisane prijepise u `data/reference/food_drink_company_facts.csv`. Krašev godišnji i polugodišnji rezultat su tadašnje nerevidirane konsolidirane objave. Mlinarovih do 80 milijuna eura jest najavljeni financijski krug; 35 milijuna prva je faza EBRD-a. Ni jedno ne predstavlja dokaz već dovršenih kapitalnih ulaganja.

Problemi izvornog izvještaja izdvojeni su, a sporne brojke nisu prenesene u post:

- EIZ p.2 says top-ten food employment fell 2.8%; Table 5 and p.10 say it rose 2.8%.
- EIZ p.5 gives April 2026 producer prices inside a report dated April; release/vintage not established.
- EIZ p.5 productivity text does not reconcile with Table 3; not used.

## Što nije preuzeto iz početne ideje

Početni brief navodi 32,9% tekstova u sličnim skupinama i 17 Facebook objava s 36,4% interakcija. Izvorni izvod, pravila izbora i izvještaj za te brojke nisu dostavljeni. Novi web uzorak ima izričito drukčiju definiciju. Te brojke nisu reproducirane, nisu zamijenjene približnim podudaranjem i nisu unesene u nacrt. Facebook ostaje izvan ove analize.

Nisu procjenjivani sentiment, izvori izjava ili čitateljska uvjerenja. Bojkot iz siječnja 2025. izvan je glavnog prozora. Potrošačke cijene, turizam i stvarni učinci preuzimanja traže zasebnu analizu ako post dobije taj kut.

## Uredničke odluke i grafike

Autor je odabrao eksplorativan, deskriptivan pregled i zatim odobrio završno poliranje i objavu. Prethodne oznake za odluku o glavnom kutu povučene su nakon te korekcije. Posljednji `[KUT]` uz završni naglasak o lokalnoj ulozi uklonjen je nakon odobrenja postojeće deskriptivne verzije; završetku nije dodana nova interpretacija. Autor nije dodijeljen, pa ostaje `author: []`. Završna verzija ima `draft: false` i `freeze: auto` za objavu bez privatnih podataka.

Tri grafikona čitaju spremljene tablice i paletu `R/house_style.R`. Tvrtke koriste vodoravne stupce od nule, složene po vrsti portala. Mjesečni pregled koristi stupce ukupnog broja članaka, podijeljene istim bojama po vrsti portala. Zajednička početna crta daje preciznu usporedbu ukupnih brojeva; razine unutar stupca opisuju sastav. Linija bi dobro prikazala kretanje ukupnog broja, ali slabije sastav. Teme zadržavaju pet malih grafikona s jednakom postotnom skalom. Usporedba medijskih i proizvodnih kalendara više nije prikazana u postu; pripadni gospodarski podaci ostaju u istraživačkim izlazima.

Detalji izvođenja nalaze se u [README-u](README.md). Datoteke `claim_ledger.csv`, `macro_facts.csv`, `company_facts.csv`, `agrolaguna_case.csv` i `kras_case.csv` povezuju nalaze s tablicama i javnim izvorima. Provjera izračuna je u `quality_reports/2026-10-05_food-drink-verification.json`.
