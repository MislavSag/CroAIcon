# Plan. Ispraviti tvrdnju o polovici noćenja izvan poduzeća

Post: `posts/2026-07-noc-bez-cijene/index.qmd` (nacrt)
Datum: 2026-07-30
Status: **izvršeno** 30. srpnja 2026. Build i grafikoni ponovno pokrenuti, post renderiran, sve kritične provjere prolaze. Otvoreno ostaju samo dva [KUT] markera, koji čekaju autora.

## Kontekst. Što je pogrešno

Odjeljak *Polovica noćenja gotovo ne prođe kroz poduzeće* miješa dvije različite populacije i iz njih izvodi tvrdnju koju podaci ne nose.

1. **4,4 EUR po noćenju za sobe i apartmane nije mjera ničega.** Brojnik je prihod 1.691 trgovačkog društva u NKD skupini 55.2. Nazivnik je svih 46,6 milijuna noćenja koje DZS vodi u *vrsti smještaja* 55.2. To su različiti skupovi objekata, pa količnik nije ni cijena, ni stopa naplate, ni udio, nego artefakt.
2. **49,8% nije udio kućanstava.** To je udio DZS-ove vrste smještaja u ukupnim noćenjima. Unutar te vrste ima i firmi. Rečenica *Polovica hrvatskog turizma odvija se izvan poduzeća, u kućanstvima* pripisuje kućanstvima cijeli segment.
3. **Podjela noćenja na firme i kućanstva se iz ovih podataka ne može izmjeriti.** Provjereno: `BS_TU14` dijeli noćenja po vrsti objekta, ne po tome kome objekt pripada. Ni eksperimentalna statistika platformi, ni primorske, ni otočne tablice ne nose tu podjelu. Post zato tu brojku ne smije ni tvrditi ni procjenjivati.

Ishod. Odjeljak zadržava nalaz, ali ga iznosi samo iz onoga što je mjereno. Cijena po noćenju ostaje samo za hotele i kampove, gdje prihod i noćenja opisuju iste subjekte. Segment soba i apartmana opisuje se bez ijednog podatka o novcu po noćenju.

## Nova činjenica iz podataka koju skripta trenutno ispušta

`BS_TU14` ima drugu razinu unutar 55.2 koju parser preskače. Za 2024.:

| vrsta unutar 55.2 | noćenja | postelje |
|---|---|---|
| Sobe, apartmani, studio-apartmani, kuće za odmor | 45.167.304 | 697.267 |
| Hosteli | 918.385 | 16.973 |
| ostalo (lječilišta, prenoćišta, domovi, robinzonski smještaj) | 550.895 | 18.034 |
| **55.2 ukupno** | **46.636.584** | **732.274** |

Podvrste se zbrajaju u ukupno bez ostatka. To omogućuje da se nazivnik nazove točno (*sobe, apartmani i kuće za odmor*, 48,2% svih noćenja u zemlji) umjesto da se cijela skupina 55.2 zove *apartmani*.

## Promjene po datotekama

### 1. `python/tourism_value_build.py`

- U `read_accommodation_types()` dodati parsiranje druge razine hijerarhije (uvlaka u stupcu *Vrste smještaja* označava podvrstu). Nova tablica `outputs/tables/tourism_accommodation_subtypes.csv` s noćenjima i posteljama po podvrsti za `LAST_YEAR`.
- Nova provjera `subtypes_sum_to_552`: zbroj podvrsta unutar 55.2 mora dati objavljeni ukupni iznos 55.2 (tolerancija 0,1%). Ide u kritični set.
- U `model_value` dodati `revenue_share_pct` u petlju koja gradi `model_*` činjenice, jer novi grafikon 2 crta udjele prihoda.
- Nove činjenice: `subtype_rooms_nights`, `subtype_rooms_beds`, `subtype_rooms_share_of_national_pct`, `subtype_rooms_share_of_552_pct`, `subtype_hostels_nights`.
- **Ukloniti iz `facts` ključeve koje post više ne smije dohvatiti**: `model_552_eur_per_night`, `model_552_eur_per_bed`, `model_hotel_to_apartman_ratio` (`model_hotel_to_apartment_ratio`). Stupci ostaju u `tourism_value_by_model.csv` jer ih čita provjera `apartment_rate_is_not_a_price`, koja se zadržava kao zaštita, s komentarom da je to interna dijagnostika, ne izlaz za tekst. Petlja koja gradi `model_*` činjenice dobiva izričito izuzimanje za skupinu 552 i mjere u eurima po noćenju.
- Zadržati bez promjene: `eur_per_night_matched_segments` (74,7 EUR, hoteli + kampovi), `hotel_eur_per_night_*`, `nights_per_bed_*`, `model_apartment_nights_share`, `model_apartment_revenue_share`, `platform_share_of_apartments_pct`.

### 2. `python/tourism_value_charts.py`

- `fig_models()` preraditi iz cijena u udjele. Parne vodoravne trake po vrsti smještaja, udio u noćenjima protiv udjela u prihodu trgovačkih društava. Naslov *Hoteli nose 27% noćenja i 86% prihoda, apartmani 50% i 5%*, podnaslov navodi da su to dvije različite raspodjele, a ne cijena. Datoteka i naziv figure ostaju `tourism_2_po_vrsti_smjestaja.png` da se ne mijenja putanja u postu. Boje po istoj `RISE`/`FALL`/`MUTED` logici kao ostali rangirani stupčani grafikoni.
- `fig_bed_use()`: naslov *privatni 64* → *krevet u apartmanu 64*, jer *privatni* prejudicira vlasništvo koje ova tablica ne mjeri.
- Provjeriti da nijedan drugi grafikon ne crta `eur_per_night` za skupinu 552. Grafikon udjela vrsta smještaja (`share_sobe`) crta noćenja i ostaje nepromijenjen.

### 3. `posts/2026-07-noc-bez-cijene/index.qmd`

| mjesto | promjena |
|---|---|
| r. 76, uvodni most | *polovicu gostiju ne prima poduzeće nego kućanstvo* → u nazivniku su sva noćenja, a gotovo polovica ostvari se u sobama, apartmanima i kućama za odmor, gdje poduzeća gotovo ne postoje |
| r. 100, naslov odjeljka | → **Pola noćenja je u smještaju koji firme gotovo ne vode** |
| r. 104–106 | zadržati hotel 127,2 i kamp 12,2 kao izmjerene cijene. Izbaciti *Soba ili apartman 4,4* |
| r. 108 | prepisati. Umjesto objašnjavanja artefakta, reći što se zna: skupina su sobe, apartmani i kuće za odmor, 45,2 od 46,6 milijuna noćenja u njoj, 697.267 postelja, a društava u istoj NKD skupini ima 1.691 s 2.266 zaposlenih i 5,5% prihoda djelatnosti smještaja. Izričito reći da DZS noćenja ne dijeli po tome vodi li objekt firma ili kućanstvo, pa se prihod po noćenju u tom segmentu ne računa |
| r. 110 | ostaje. 74,7 EUR za hotele i kampove je čista mjera i sada nosi cijeli teret cijene |
| r. 112 | *Polovica hrvatskog turizma odvija se izvan poduzeća, u kućanstvima* → dvije raspodjele: 49,8% noćenja u toj vrsti smještaja protiv 5,5% prihoda društava u istoj skupini, uz zaključak da je to mjera koliko se turizma vodi izvan poslovnih knjiga, bez brojke koja to kvantificira |
| r. 116 | *privatni krevet* → *krevet u sobi ili apartmanu*, *Privatnih je postelja* → *Postelja je u toj vrsti smještaja* |
| r. 130 | *Gdje prevladavaju privatni apartmani* ostaje, ali zadnja rečenica gubi implikaciju izmjerenog udjela |
| r. 197–198, 201, Napomene | bullet *Glavna mjera* dodaje da nazivnik nije podijeljen po vlasništvu objekta. Bullet *Gdje je mjera ipak cijena* prestaje objašnjavati kako se iznos za sobe i apartmane ne čita kao cijena i umjesto toga kaže da se ne računa. Bullet *Vrste smještaja* dodaje da DZS objavljuje i podvrste unutar 55.2 i da ta podjela nije po vlasništvu |

**[KUT] markeri se ne mijenjaju.** Dva ih se tiču ove tvrdnje i oba nose isti preveliki zahvat, pa idu autoru na odluku, ne u tiho prepisivanje:

- r. 122 *Je li nevidljiva polovica turizma problem naplate, problem poreza ili problem stanovanja.*
- r. 188 *[KUT, glavna interpretacija] To da polovica turizma ne prolazi kroz poduzeća nije nesreća nego model.*

Predložena zamjena za oba, na odobrenje: *polovica turizma* → *smještaj koji se ne vodi u poslovnim knjigama*. Rečenica r. 192 (*za polovicu noćenja ni ne znamo koliko su donijele*) je pod novim okvirom točna i ostaje.

### 4. `MEMORY.md`

Novi red u *Data quirks*: DZS `BS_TU14` dijeli noćenja po vrsti smještajnog objekta, a ne po tome je li objekt u kućanstvu ili u društvu. Udio skupine 55.2 u noćenjima nije udio kućanstava, i podjela firma/kućanstvo se iz statistike turizma ne može izmjeriti. Ista tablica ima drugu razinu hijerarhije s podvrstama koje se zbrajaju u ukupno.

## Provjera

1. `QUARTO_PYTHON=.venv/Scripts/python.exe` u okruženju za sve što dira Quarto.
2. `.venv/Scripts/python.exe python/tourism_value_build.py` → sve kritične provjere prolaze, uključujući novu `subtypes_sum_to_552`. Potvrditi da `outputs/facts/tourism_value.json` više ne sadrži `model_552_eur_per_night`.
3. `.venv/Scripts/python.exe python/tourism_value_charts.py` → pregledati `tourism_2_po_vrsti_smjestaja.png` i `tourism_10_iskoristenost_postelja.png` očima, ne samo potvrditi da su se zapisale.
4. `quarto render posts/2026-07-noc-bez-cijene` → render prolazi, u HTML-u nema ni jednog *4,4* ni *4 eura* u tom odjeljku, i nijedan `{python}` izraz ne pada na ključu kojeg više nema.
5. Pretražiti cijeli post na *polovica*, *privatn*, *kućanst* i potvrditi da nijedno preostalo mjesto ne tvrdi izmjereni udio.
6. Dopisati nalaz u `quality_reports/2026-07-noc-bez-cijene_qa.md` da se isti ne pronađe treći put.
7. Post ostaje `draft: true`.
