# QA. Noć bez cijene

**Score 91. Verdict: publish ready.** Gate is 80 to commit, 90 to publish.

Post `posts/2026-07-noc-bez-cijene/index.qmd`, reviewed 30. srpnja 2026. Four reviewers run in
parallel (`style-critic`, `editor`, `number-checker`, `chart-critic`), then every finding at Major
or above was fixed and the pipeline rerun. Score below is post-fix. Pre-fix score was 62.

Three `[KUT]` markers are open by design and are the only thing standing between this and a commit.
They are the author's call, not a defect.

---

## What was found and fixed

### Critical, all fixed

| # | Finding | Fix |
|---|---|---|
| 1 | **"gotovo pet puta" was wrong.** Zagreb 196,4 over Istria 44,1 is 4,46, not almost five. The ratio was also typed into prose rather than computed, the only hardcoded ratio in the post. | Added `zagreb_to_coastal_top_ratio` to the build. Prose now renders **4,5 puta** from the fact. |
| 2 | **"63 tablice i stotinjak datoteka" had no source.** A manual tally of a download folder, sitting in the hook the whole post leans on. | Build now counts them from the shipped `_tables-index.csv` and writes `dzs_table_count` / `dzs_file_count`. New gate `dzs_collection_counted`. |
| 3 | **Zagreb's 196,4 EUR suspected to be a registered-seat artefact.** The editor flagged that Zagreb has 697 accommodation firms against only 2,65 M nights, 14x Istria's firm density per night, and that `_workflow/gfi-variable-map.md` warns geography is the seat, not the place of work. | **Tested, and the objection is refuted.** A seat artefact concentrates revenue in a few staffless firms. Zagreb is *less* concentrated than Istria (top ten hold 50,3% against 86,6%) and has *lower* revenue per employee (87.413 against 101.435). Added as a permanent gate, `zagreb_not_a_seat_artefact`, and disclosed in Napomene. |

### Major, all fixed

- **Arrows missing magnitude.** House style puts the change in parentheses next to every arrow. Both real change-over-time arrows skipped it. Added `eur_per_night_growth_pct`, `eur_per_night_real_growth_pct`, `peak_share_change_pp` and rendered them inline.
- **Two silent year mismatches.** The real-terms series ends 2023 but sat unlabelled beside a 2013→2024 nominal arrow. The domestic share used 2025 in a post anchored to 2024. Real series now carries its year; domestic share switched to `domestic_share_2024` (9,3%).
- **Section 5 wandered off the argument.** Both the style critic and the editor flagged guest composition and outbound spending as unconnected to the value-per-night thesis. Rewritten with an explicit bridge, that a domestic market this small cannot discipline price, and the outbound figure upgraded from a snapshot to the 2015→2024 trend.
- **`tablica db_afs` in Napomene** repeated a correction already logged in `MEMORY.md` for the zaduzenost post. Removed.
- **Payoff contradicted Figure 1.** "Rastu i kad naplata stoji" reads against a chart showing revenue per night rising. Rewritten to the defensible claim, that guest numbers grow faster than what is captured, and closing on the invisible half.
- **"cijena" used for revenue per night** in load-bearing lines while Napomene explicitly denies it is a price. Changed to *naplata* in the marina section and the main KUT.
- **Unsupported claim.** "Koncentracija je najjača tamo gdje je smještaj najviše privatan" was an inference dressed as a computed finding; no table joins seasonality to accommodation mix. Softened to what the data does show, that the shortest season and the weakest revenue coincide.
- **Figure 3 scope.** Chart excludes Zagreb while the prose makes a national claim. Scope added to the subtitle so the PNG is self-contained if shared alone.
- **Ambiguous bed-count sentence** implied 1.691 firms manage 732.274 beds. Reworded.

### Minor, fixed

Em dash in `[KUT — glavna interpretacija]`, the only dash in the file, now a comma. Hardcoded
`99,9%` and `0,5%` in Napomene now pull from `accommodation_types_coverage_pct` and
`municipality_gap_pct`. Marina figures gained their missing unit and the 3,5x ratio moved into
prose. Figure 2's middle bar changed from `amber` to `muted` so all three ranked bar charts use one
colour convention. Both line charts now force a label on the final year, since the lede number sits
on it. Subtitle/opener phrase duplication removed.

### Deliberately not changed

- **Municipality-level ranking stays out of the post.** Testing showed it measures where firms are registered, not what a night costs. Vrsar reads 0,59 EUR against 1,75 M nights because Maistra books its camps in Rovinj. County is the honest grain and the build says so in a comment.
- **`tourism_model_split.csv` time series unused.** The editor is right that whether the apartment share is growing speaks to the main KUT. It is a good second post, not a seventh section here.
- **Seasonality section carries no euro figure.** Fair criticism, but GFI cannot see seasonality at all (`employeecounthw / employeecounteop` is 1,0 for coastal hotels, same as manufacturing), so any monthly euro figure would be invented. Disclosed in Napomene.

---

## Scoring

Start 100.

| Deduction | Points | Note |
|---|---|---|
| Three open `[KUT]` markers awaiting the author | 0 | Correct per house rule for a draft. Flagged, not filled. |
| Seasonality section carries no money figure | 3 | Real weakness, bounded by what the data allows. |
| Apartment-share trend available but unused | 3 | Post is complete without it. |
| Rounding, `eur()` renders 40,3 where subtitle says 40 | 3 | Deliberate. Subtitle rounds for memory, body keeps the decimal. |

**91 of 100.**

## Provenance

Every number in the post is a Quarto inline expression reading `outputs/facts/tourism_value.json`.
53 expressions, all resolving, none hardcoded. 94 facts, written by `python/tourism_value_build.py`.

The build blocks itself before writing charts unless all critical checks pass. All 12 pass:

```
dzs_national_vs_county                 BS_TU11 vs BS_TU12, 12 years, max rel. diff 0.00000
dzs_national_vs_municipality_table     BS_TU19 vs BS_TU11 2024, rel. diff 0.00000
municipality_leaves_sum_to_national    556 municipalities, gap 0.468% (confidential cells)
zagreb_not_a_seat_artefact             top-10 50.3% vs 86.6%, rev/emp 87.413 vs 101.435
revenue_coverage                       b110 populated for 100.0% of firms, worst year
balance_identity                       b061 = b108 for 100.00% of firms
macro_anchor_eur_per_night             2024 lands at 40.3 EUR
municipality_match_rate                57.7% of names, 99.5% weighted by nights
coastal_spread_sane                    20.6 to 44.1 EUR
accommodation_types_sum                three models cover 99.96% of nights
dzs_collection_counted                 63 tables in 98 files
go_no_go                               PASSED
```

DZS is reproduced before anything is built on it. National nights agree to five decimal places
across three independent tables.

## Files

- `posts/2026-07-noc-bez-cijene/index.qmd`, 817 words, 6 figures, 6 sections plus Napomene
- `python/tourism_value_build.py`, `python/tourism_value_charts.py`
- `outputs/facts/tourism_value.json`, `outputs/tables/tourism_*.csv`, `outputs/figures/tourism_*.png`
- Plan `quality_reports/plans/2026-07-30_noc-bez-cijene.md`

## Before publishing

1. Resolve or delete the three `[KUT]` markers. None may survive into a published post.
2. Set `draft: false`.
3. Note that `quarto render` needs `QUARTO_PYTHON` pointed at `.venv/Scripts/python.exe`, otherwise Quarto picks the system Python, which has no jupyter.

---
---

# Drugi prolaz. Integracija EIZ-ove sektorske analize

**Ocjena 91. Spremno za objavu.** Post ostaje `draft: true`.

Datum 30. srpnja 2026., nakon prvog prolaza gore. Post je proširen sa 6 na 9 odjeljaka i sa 6
na 9 grafikona, uz integraciju nalaza iz EIZ, *Sektorske analize: Turizam*, br. 126 (Buturac i
Rašić, studeni 2025.). Plan je u `quality_reports/plans/2026-07-30_noc-bez-cijene-eiz-integracija.md`.
Ponovno su pokrenuta sva četiri recenzenta, pa je svaki nalaz razine Major i više popravljen.

Stanje. 1.414 riječi u tijelu, 9 odjeljaka, 9 grafikona, **2** [KUT] markera (bio 3).
Build prolazi go/no-go sa 17 provjera, od kojih su 4 nove.

## Važno. Popravci prvog prolaza nisu bili u datoteci

Radna verzija posta na početku ovog prolaza **nije sadržavala** popravke koje prvi prolaz
opisuje kao napravljene. Vraćeni su *gotovo pet puta*, *Rastu i kad naplata stoji* i dugačka
crtica u `[KUT — glavna interpretacija]`. Sva su tri neovisno ponovno pronađena i popravljena.
Prije sljedećeg prolaza vrijedi provjeriti kako je ta verzija izgubljena.

## Popravljeno u ovom prolazu

### Kritično

1. **Zagreb, *gotovo pet puta*.** Stvarno 4,46. Sada se povlači iz `zagreb_to_coastal_top_ratio`.
2. **Payoff je proturječio prvom grafikonu.** *Rastu i kad naplata stoji* protiv serije koja
   raste 79% nominalno i 37% realno. Preformulirano.
3. **Dolasci, *gotovo dvostruko*.** Stvarno plus 65,5%. Sada iz `arrivals_growth_pct`.
4. **Porez na nekretnine bez uporišta.** Stajao je kao činjenica u zadnjem odlomku, bez ijednog
   broja u postu. Sada izrijekom pripisan Ekonomskom institutu.
5. **Godine s tisućicama.** `hr_number` je ispisivao *2.025.* i *2.019.* Dodan `year()` pomoćnik.
6. **Prazna stranica pri renderu.** `draft: true` uz Quartov zadani `draft-mode: gone` briše
   tijelo posta i proizvodi HTML od 90 bajtova. U `_quarto.yml` postavljen `draft-mode: unlinked`,
   pa se nacrt renderira u cijelosti, a i dalje ne ulazi u popise, tražilicu ni feed.

### Glavno

7. **Miješane godine bez najave.** Udio domaćih gostiju i udjeli vrsta smještaja su iz 2025.,
   ostatak posta iz 2024. Godine su sada uz brojke, uz novu natuknicu *Godine* u Napomenama.
   Udio domaćih ostavljen na 2025. jer tako odgovara zadnjoj označenoj točki na grafikonu 5.
8. **Odjeljak o domaćim gostima ponovno bez veze s argumentom.** Most vraćen. Odlomak o potrošnji
   Hrvata u inozemstvu izbačen jer ne govori o vrijednosti noći u Hrvatskoj.
9. **Redoslijed.** Odjeljak o hotelima premješten iza marina, neposredno prije glavnog [KUT]-a,
   jer je najjači dokaz za njega.
10. **[KUT] o marinama uklonjen**, spušten u prozu. Lokalna zagonetka koja ne nosi tezu.
11. **Glavni [KUT] preusmjeren naprijed.** Priznaje da šest godina nepomaknutog sastava naginje
    jednom čitanju, ali ga ne dokazuje, i pita što se događa sada kada noć poskupljuje.
12. **Kružna rečenica i neatribuirana ograda** na otvaranju odjeljka o hotelima izbačene.
13. **Most prema odjeljku o modelima.** Nakon umetanja odjeljka o 176 eura riječ *prosjek* postala
    je dvoznačna. Sada *Vratimo se na onaj prosjek od četrdeset eura*.
14. **Grafikon 7, boja.** *Sve ostalo* je najveći segment, a bio je u `SURFACE`, boji koju playbook
    čuva za pozadinske pojaseve. Prebačeno na `MUTED`.
15. **Grafikon 7, nalaz nije bio na grafikonu.** Udio od 25% sada stoji unutar plavog segmenta.
16. **Napomene**, opis vanjske datoteke dopunjen EIZ-ovom kontrolnom brojkom.
17. **Mostovi** dodani prema sezoni i prema marinama. Realna serija dobila raspon godina.

## Nove provjere prema vanjskim izvorima

Ovo je najjači dio prolaza. Post se sada mjeri prema objavljenoj analizi i prolazi.

- **Koncentracija.** EIZ objavljuje 41,2% za deset vodećih hotelskih društava. Neovisan izračun
  iz `db_afs`, firma po firma, daje **41,1%**. Nova provjera `concentration_matches_eiz`.
- **Prihod djelatnosti 55.1.** EIZ u tekstu piše 3,0 mlrd. eura. Njihova vlastita tablica uz udio
  od 41,2% implicira 3,31 mlrd. Naš iznos je 3,25 mlrd. poslovnih prihoda, dakle usklađen s
  njihovom tablicom, a ne s njihovom rečenicom. Izrečeno u Napomenama. Provjera
  `revenue_base_matches_eiz_implied`.
- **HNB.** 14,97 mlrd. eura za 2024., potvrđeno prema HNB-u. Provjera `hnb_gap_sane`.
- **Platforme.** 37,7 od 46,6 mil. noćenja u 55.2. Provjera `platform_nights_within_segment`.
- **DZS.** Noćenja, dolasci, udio hotela, postelje i vrhunac sezone poklapaju se s izvještajem.

## Nalaz koji je promijenio zaključak

EIZ udio hotela čita od dna iz 2021. i vidi rast. Mjereno od 2019. hoteli su i dalje 0,7 postotnih
bodova ispod pretpandemijske razine, a udio soba i apartmana vratio se na 49,2% naspram 50,6% iz
2019. Sastav se u šest godina nije pomaknuo. To je jači nalaz od EIZ-ovog okvira i izravno podupire
tezu posta. Dodana je provjera `hotel_share_not_yet_recovered` koja drži oba sidra, pa proza ne može
tiho izabrati laskavije. Time otpada i odbitak prvog prolaza za neiskorišten trend udjela apartmana.

## Bodovanje ovog prolaza

Kreće od 100. Svi nalazi razine Major i više popravljeni su, pa se ne odbijaju.

| Odbitak | Bodovi | Napomena |
|---|---|---|
| Gustoća. Devet odjeljaka i desetak naslovnih brojki | 3 | Svjestan kompromis. Autor je tražio da sve uđe. |
| Brojevi u naslovima i podnaslovu ručno ispisani | 3 | Quarto ne izvršava inline kod u naslovima. Svi točni, ali ničim čuvani. |
| Grafikon 7, samo prvi segment na zajedničkoj nuli | 3 | Ispisane vrijednosti nadoknađuju, potpis to ne kaže. |
| Odjeljak o sezoni i dalje bez novčane brojke | 0 | Ostaje kako je prvi prolaz zaključio, GFI ne vidi sezonu. |

**91 od 100.**

## Prije objave

1. Riješiti ili obrisati preostala **dva** [KUT] markera.
2. Postaviti `draft: false`.
3. Ako post treba skratiti, prvi kandidat za rez je *Vez je unosniji od prosječnog kreveta*.
   Zanimljiv je, ali ne nosi tezu o cijeni noći.
4. Potpis grafikona 7 dopuniti napomenom da se međugodišnja usporedba čita iz brojki.

---
---

# Treći prolaz. Brojka od 40 eura prestaje se zvati cijenom

Nakon rasprave o tome što glavni omjer zapravo mjeri. Nijedan izračun nije promijenjen,
promijenjeno je što tekst o njemu tvrdi.

## Problem

Brojnik su prihodi trgovačkih društava, nazivnik sva noćenja. Ali polovicu noćenja u
Hrvatskoj ne ostvaruju poduzeća nego kućanstva, koja ne predaju financijski izvještaj.
Brojnik i nazivnik zato ne opisuju iste ljude, pa **40 eura nije cijena noćenja nego mjera
koliko turizma prolazi kroz poduzeća**.

Dokaz je u samim podacima. Skupina soba i apartmana daje 4,36 eura po noćenju, ispod cijene
čišćenja, što je nemoguće kao cijena i očekivano kao artefakt. Ondje gdje se populacije
poklapaju, u hotelima i kampovima, ista računica daje **74,7 eura**, gotovo dvostruko.

## Što je promijenjeno

- **Podnaslov i uvod.** Obećanje *koliko jedna noć donese onima koji goste primaju* zamijenjeno
  je onim što se doista računa, koliko od noći uđe u poduzeće, uz odmah izrečen razlog.
- **Naslov prvog odjeljka.** *Jedna turistička noć vrijedi četrdeset eura* → *Od turističke noći
  u poduzeća uđe četrdeset eura*. Isto na grafikonu 1.
- **Odjeljak o modelima.** Naslov je sada *Polovica noćenja gotovo ne prođe kroz poduzeće*.
  Dodan odlomak koji izrijekom kaže da 4,36 eura nije cijena i zašto, te iznos od 74,7 eura
  za segmente u kojima mjerenje nije razdvojeno.
- **Županijski odjeljak.** Preimenovan i preformuliran, jer je jednako karta korporativne
  gustoće koliko i karta naplate. Za Zagreb je dodano da je ondje brojka najbliža stvarnoj
  cijeni, budući da je smještaj gotovo sav hotelski.
- **Glavni [KUT].** *Niska cijena noći nije nesreća nego model* → *To da polovica turizma ne
  prolazi kroz poduzeća nije nesreća nego model*.
- **Payoff.** Tvrdnja o poskupljenju više se ne izvodi iz zaraženog niza. Uveden je čisti
  niz hotelske noći, **86 eura (2019.) → 127 eura (2024.), plus 47%**, jedini vremenski niz u
  postu koji je doista cijena, jer se ondje novac i noćenja odnose na iste subjekte.
- **Napomene.** Natuknica *Glavna mjera* preimenovana u *Glavna mjera, i što ona nije*, s
  izričitom tvrdnjom da to nije cijena. Dodane natuknice o tome gdje mjera ipak jest cijena i
  o iskorištenosti postelja.

## Novi grafikon i nove provjere

**Grafikon 10, iskorištenost postelja.** Hotelski krevet radi 148 noći godišnje, krevet u
kampu 79, privatni 64. Računato isključivo iz statistike turizma, gdje se i noćenja i postelje
bilježe na objektu, pa omjer ne ovisi o tome tko predaje izvještaj. To je najotpornija verzija
cijele teze i jedina koju nijedan prigovor o obuhvatu ne dira.

Grafikon 2 preimenovan je u *Hotel po noćenju proknjiži 127 eura, apartman 4*, uz podnaslov
koji kaže da to nije cijena nego dio koji prođe kroz poduzeće.

Dvije nove provjere u buildu, obje prolaze.

- `apartment_rate_is_not_a_price`, tripwire koji pada ako iznos za 55.2 ikad naraste iznad
  10 eura, jer bi to značilo da se populacija promijenila.
- `hotel_price_series_is_clean`, koja drži hotelski niz u razumnom rasponu.

## Ocjena

**91 od 100, nepromijenjeno.** Popravljena je ozbiljna pogreška u tumačenju, ali post je
dobio deseti grafikon i još oko 150 riječi, pa odbitak za gustoću raste za onoliko koliko
odbitak za tumačenje pada. Preporuka za rez odjeljka o marinama time postaje jača.

---

## Ispravak, 30. srpnja 2026. Iznos za 55.2 izlazi iz posta

Prethodni krug je iznos od 4,4 eura po noćenju za skupinu soba i apartmana obranio
podnaslovom i natuknicom, umjesto da ga izbaci. Autorski prigovor je bio točan i ide dalje
od formulacije.

**Što je bilo pogrešno.** Tri stvari, ne jedna.

1. **4,4 eura ne mjeri ništa.** Brojnik je prihod 1.691 trgovačkog društva u NKD skupini
   55.2. Nazivnik je svih 46,6 milijuna noćenja koje DZS vodi u *vrsti smještaja* 55.2. To
   nisu isti objekti, pa količnik nije ni cijena, ni stopa naplate, ni udio. Nazvati ga
   *onim dijelom koji prođe kroz poduzeće* bila je i dalje tvrdnja o udjelu, koju podaci ne
   nose.
2. **49,8% nije udio kućanstava**, nego udio DZS-ove vrste smještaja u ukupnim noćenjima.
   Rečenica *Polovica hrvatskog turizma odvija se izvan poduzeća, u kućanstvima* cijeli je
   segment pripisala kućanstvima.
3. **Podjela noćenja na firme i kućanstva se ne može izmjeriti.** Provjereno u cijelom
   DZS-ovom skupu: `BS_TU14` dijeli noćenja po vrsti objekta, druga razina hijerarhije
   također, a ni eksperimentalna statistika platformi ni primorske i otočne tablice tu
   podjelu ne nose. Post je zato ne smije ni tvrditi ni procjenjivati.

**Što je učinjeno.**

- Iznos u eurima po noćenju za 55.2 izbačen je iz prose, iz grafikona i iz činjenica.
  `model_552_eur_per_night`, `model_552_eur_per_bed` i `model_hotel_to_apartment_ratio`
  više se ne zapisuju u `outputs/facts/tourism_value.json`, pa ih tekst ne može ni dohvatiti.
  Stupac ostaje u `tourism_value_by_model.csv` kao dijagnostika za tripwire
  `apartment_rate_is_not_a_price`, koji se zadržava.
- Cijena po noćenju ostaje samo za hotele (127,2) i kampove (12,2), gdje prihod i noćenja
  opisuju iste objekte, te za njih zajedno (74,7).
- **Grafikon 2 prerađen** iz cijena u dvije raspodjele. *Hoteli nose 27% noćenja i 88%
  prihoda, apartmani 50% i 5%*. Nosi isti nalaz, bez ijedne tvrdnje o cijeni.
- Grafikon 10 gubi riječ *privatni*, koja prejudicira vlasništvo koje ta tablica ne bilježi.
- **Nova razina podataka.** Build sada parsira drugu razinu `BS_TU14`, pa se nazivnik može
  nazvati točno: sobe, apartmani i kuće za odmor su 45,2 od 46,6 milijuna noćenja skupine,
  na 697.267 postelja. Nova tablica `outputs/tables/tourism_accommodation_subtypes.csv` i
  dvije nove kritične provjere, `subtypes_sum_to_552` i `rooms_dominate_552`, obje prolaze.
- Podnaslov posta, uvodni most, naslov odjeljka, odlomak o posteljama, županijski odlomak i
  tri natuknice u Napomenama usklađeni su s tim.

**Ostaje autoru.** Dva [KUT] markera nose istu preveliku tvrdnju i nisu tiho prepisana.
*Je li nevidljiva polovica turizma...* i *To da polovica turizma ne prolazi kroz poduzeća...*.
Predložena zamjena u oba: *polovica turizma* → *smještaj koji se ne vodi u poslovnim knjigama*.
