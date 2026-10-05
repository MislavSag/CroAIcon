# Hrana i piće — završna verzija

- `article.qmd` je kanonski tekst. Uređivati ovdje.
- `article-preview.md` je čitljiva kopija s izračunanim brojkama i slikama, generirana nakon provjere HTML-a.
- `analysis.md` je generirana preliminarna analiza s nalazima, metodom, osjetljivošću i ograničenjima.
- `posts/2026-10-hrana-pice-iza-naslova/index.qmd` je kopija za Quarto, s `draft: false` i praznim autorom.
- `_site/posts/2026-10-hrana-pice-iza-naslova/index.html` je lokalni prikaz. Odredište odobrene objave je [AI.econ](https://mislavsag.github.io/CroAIcon/posts/2026-10-hrana-pice-iza-naslova/).
- Glavni je smjer eksplorativan i deskriptivan pregled sektora u medijima. Gospodarski nalazi služe kao kontekst opaženih vijesti. Autor je odobrio ovu verziju i objavu 5. listopada 2026. Posljednja interna urednička oznaka uklonjena je uz očuvan odobreni završetak.
- Ako post preuzme Mislav, završni analitički nacrt treba proći njegov autor-specific `mislav-humanizer` postupak.

## Reprodukcija

Pokrenuti iz korijena repozitorija. Analiza koristi instalirani Python s paketima `duckdb`, `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `lxml`, `pymupdf` i Parquet podrškom. Quarto koristi postojeći repozitorijski `.venv` s Jupyterom. Put do baze može se zadati varijablom `DETERMDB_MERGED`; zadani je korisnikov put `C:/Users/lsikic/Luka C/DetermDB/determDB_merged.duckdb`. Baza se otvara samo za čitanje.

```powershell
python python/food_drink_2026_sources.py
python python/food_drink_2026_extract.py
python python/food_drink_2026_build.py
python python/food_drink_2026_macro.py
python python/food_drink_2026_facts.py
python python/food_drink_2026_charts.py
python python/food_drink_2026_report.py
python python/food_drink_2026_prepare_draft.py
$env:QUARTO_PYTHON = (Resolve-Path '.venv/Scripts/python.exe').Path
quarto render posts/2026-10-hrana-pice-iza-naslova/index.qmd
python python/food_drink_2026_verify_render.py --published
```

Prvo preuzimanje javnih izvora treba mrežu; postojeće lokalne snimke se ponovno koriste. Krašev poslužitelj odbija izravno preuzimanje s HTTP 403. Njegove javne objave provjerene su pregledom web izvora, a pripisani prijepisi s URL-om i datumom nalaze se u `data/reference/food_drink_company_facts.csv`. Skripta za makroanalizu ne ovisi o neuspjelim preuzimanjima Kraša.

Izvoz provjerava veličinu i vrijeme izmjene baze prije i poslije čitanja; nema potpunog hasha velike baze. Mjesečni obuhvat portala ponovno koristi samo ako se podudaraju ti metapodaci, razdoblje i popis domena. Za osvježavanje obuhvata ukloniti isključivo njegov cache `outputs/tables/food_drink_2026/outlet_coverage.csv` pa ponovno pokrenuti izvoz.

## Datoteke i privatnost

Sirovi javni izvori su u `data/raw/food_drink_2026/`. Izvedeni licencirani tekstovi, kandidati i dijagnostički uzorak ostaju lokalno u `data/processed/food_drink_2026/`. Te su mape ignorirane Gitom. Za ponavljanje analize na drugom računalu potrebni su pristup istoj bazi i izvorne snimke ili nova preuzimanja.

Agregati su u `outputs/tables/food_drink_2026/`, brojevi za inline Quarto u `outputs/facts/food_drink_2026.json`, a slike u `outputs/figures/food_drink_2026/`. Repozitorij općenito ignorira `outputs/`; za novo izvršavanje analize potrebni su ti izlazi ili ponovni izračun. Kopije grafikona nalaze se uz post. Quarto koristi javni zapis izvršavanja u `_freeze/posts/2026-10-hrana-pice-iza-naslova/` za render cijelog sitea bez privatne baze. Ne prenositi pune medijske tekstove u javnu mapu.

## Provjere

Računski audit provjerava jedinstvenost članaka, zbrojeve, mjesece, reprodukciju odabranih EIZ vrijednosti iz DZS-a i nepromijenjene metapodatke baze. Dodatna provjera HTML-a traži razriješene inline brojeve, tri postojeće slike, oznake za uredničke odluke i podudarnost kopije nacrta.

Grafikoni i relevantne stranice izvornog PDF-a vizualno su pregledani. Quarto je renderiran. Puni prikaz stranice u pregledniku nije bilo moguće vizualno pregledati jer u ovoj sesiji nema dostupnog preglednika. To ostaje ograničenje provjere izgleda, uz prolaz programskih provjera HTML-a i slika.
