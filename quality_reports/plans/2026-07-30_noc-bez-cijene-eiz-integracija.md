# Plan. Integrirati nalaze EIZ-ove Sektorske analize (turizam, br. 126) u post *Noć bez cijene*

Datum: 2026-07-30. Post: `posts/2026-07-noc-bez-cijene/index.qmd`. Autor: Luka Šikić.

## Zašto

Pročitan je EIZ, *Sektorske analize: Turizam*, br. 126 (Buturac i Rašić, studeni 2025.). Izvještaj
je deskriptivni sektorski monitor i nigdje ne dijeli novac s brojem noćenja, pa glavni kut posta
preživljava. Ali otvara sedam pitanja koja post ne pokriva i jednu tvrdnju koju treba izoštriti.
Ovaj plan ih sve uvodi, uz nove podatke iz izvora koje već imamo lokalno.

## Provjere koje su već napravljene

- **Podudarnost s DZS-om.** Noćenja 2024. (93,68 vs 93,7 mil.), dolasci (20,25 vs 20,2 mil.),
  srpanj + kolovoz (55,9%), udio hotela (27,3%), postelje (1,18 mil.) — sve se poklapa.
- **Rekoncilijacija prihoda 55.1 (bila je jedina neslaganja).** EIZ u tekstu piše 3,0 mlrd. eura
  za 1.626 subjekata. Naš izračun daje 3,25 mlrd. za 1.603 firme. **Naš broj je točan.** Dokaz.
  EIZ sam navodi da deset vodećih firmi (1.363,42 mil. ukupnih prihoda) čini 41,2% djelatnosti,
  što implicira nazivnik od 3,31 mlrd., ne 3,0. Neovisno smo izračunali koncentraciju iz `db_afs`
  i dobili **41,1%** te zbroj top 10 od 1.335 mil. poslovnih prihoda. Sve se slaže s njihovom
  tablicom, a ne s njihovom rečenicom. `b147` ima nisku popunjenost i ne koristi se.
- **HNB.** Prihodi od stranih turista 2024. = **14,97 mlrd. eura** (+2,7%, +388,6 mil.), potvrđeno
  na vlada.gov.hr prema HNB-u. EIZ zaokružuje na 15,0.

## Što se mijenja u postu

### Izoštriti (tekst)

1. **Uvod.** *nema nijedne cijene* → točnije. DZS i HNB mjere vrijednost turizma u agregatu
   (devizni prihodi, satelitski račun, 11,3% BDP-a). Ono čega nema je **cijena jedne noći**.
   Ovako napisano tvrdnja je neoboriva i usput uvodi sljedeći odjeljak.
2. **Domaći gosti.** Udio jest ravan, ali razina raste, 5,09 → 8,72 mil. noćenja (2013. → 2024.).
   Dodati jednu rečenicu da se ne čita kao da domaći turizam stoji.
3. **Payoff.** Uklopiti EIZ-ovu zabrinutost (rast cijena smještaja slabi cjenovnu konkurentnost)
   i porez na nekretnine kao ograničenje ponude. To nije proturječje nego druga polovica iste
   slike, pa mora biti izrečeno.

### Novi odjeljci (tri)

4. **Gost ostavi 176 eura po noći, smještaj proknjiži najviše 44.** HNB devizni prihodi po
   stranom noćenju protiv prihoda smještajnih firmi. 3,78 od 14,97 mlrd. = 25%. Novi grafikon.
5. **Gostiju je više nego ikad, a svaki ostaje kraće.** Noćenja po dolasku 5,28 (2013.) → 4,63
   (2024.), strani 5,52 → 4,89. Uz prihod po dolasku. Novi grafikon.
6. **Hoteli polako uzimaju natrag svoj udio.** Udio hotela u noćenjima 22,4% (2021.) → 27,3%
   (2024.) → 27,7% (2025.). Izravno odgovara na glavni [KUT]. Novi grafikon.

### Dopune u postojećim odjeljcima

7. **Koncentracija.** Deset firmi uzima 41,1% prihoda hotelske djelatnosti i 35,4% cijelog
   odjeljka 55. Ide u odjeljak o modelima smještaja, jer je ista priča: korporativni sloj
   hrvatskog turizma je malen i koncentriran.
8. **Platforme.** Od 46,6 mil. noćenja u sobama i apartmanima, **37,7 mil. je rezervirano preko
   internetskih platformi** (DZS, eksperimentalna statistika). Nevidljiva polovica nije nevidljiva
   svima, nego samo financijskoj statistici. Najjača moguća potpora [KUT]-u.
9. **Plaće.** Smještaj 1.189 eura neto (2024.), 9,8% ispod prosjeka gospodarstva; ugostiteljstvo
   929 eura, 29,5% ispod. Izvor EIZ prema DZS-u. Jedna do dvije rečenice.

## Kako

1. `python/tourism_value_build.py`. Dodati.
   - `SQL_CONCENTRATION` (top 10 udio, 551 i 55) i `SQL_CLASS_SPLIT` (nacerev24, rekoncilijacija).
   - Čitanje `BS_TU11` za noćenja po dolasku, po rezidentnosti, 2013. – 2024.
   - Čitanje `BS_TU14` po rezidentnosti i godinama za udjele vrsta smještaja 2019. – 2025.
   - Čitanje eksperimentalne statistike platformi (`T02`) za noćenja u 55.2.
   - `data/external/tourism_external.csv`, novi mali ručni ulaz s provenijencijom. HNB devizni
     prihodi i DZS plaće. Svaki redak nosi izvor i URL.
   - Nove provjere. Rekoncilijacija s EIZ-om (koncentracija u rasponu 40 – 42%), HNB jaz
     (smještaj između 20 i 35% deviznih prihoda), zbroj platformi manji od ukupnih 55.2 noćenja.
2. `python/tourism_value_charts.py`. Tri nova grafikona, ista paleta i isti `titles()` sustav.
   - `tourism_7_hnb_jaz.png`. Vodoravni raspored 176 eura.
   - `tourism_8_nocenja_po_dolasku.png`. Linija, ukupno i strani.
   - `tourism_9_udio_hotela.png`. Linija, tri vrste smještaja 2019. – 2025.
3. `posts/2026-07-noc-bez-cijene/index.qmd`. Tekst prema gornjem redoslijedu. Sve nove brojke
   idu kroz `facts` iz `outputs/facts/tourism_value.json`, nijedna se ne tipka.
4. Napomene. Dodati rekoncilijaciju s EIZ-om kao zasebnu natuknicu, izvore za HNB i plaće,
   i referencu na EIZ s poveznicom. Bez kodova stupaca i bez imena tablica iz baze.
5. Rerun. `python python/tourism_value_build.py`, pa `python python/tourism_value_charts.py`,
   pa `quarto render`. Na kraju `/qa-post`.

## Rizici

- **Post postaje predug.** Devet odjeljaka umjesto šest. Mitigacija. Nova proza je kratka, a
  koncentracija i platforme ulaze kao odlomci u postojeće odjeljke, ne kao novi naslovi.
- **Jaz od 176 eura miješa dvije populacije.** HNB broji samo strane goste, prihod firmi i domaće.
  Mitigacija. Prihod smještaja po *stranom* noćenju iskazati kao gornju granicu (*najviše 44*),
  jer pretpostavlja da sve dolazi od stranaca. To je obrana koja ne može pasti.
- **Plaće i HNB nisu iz lokalnog dumpa.** Mitigacija. Zasebna datoteka s izvorom po retku,
  jasno označena kao vanjski ulaz, i navedena u Napomenama.

## Gotovo kad

Build prolazi go/no-go, devet grafikona nacrtano, post se renderira, sve brojke u tekstu dolaze
iz `outputs/`, i `/qa-post` vrati ocjenu 90 ili više.
