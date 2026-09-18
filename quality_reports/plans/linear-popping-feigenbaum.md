# Plan. Deset preliminarnih nacrta za analizu bilanci

Datum. 2026-06-22
Slug. balance-sheet-placeholder-drafts
Status. GOTOVO. 11 datoteka u `drafts/balance-sheet/` (indeks + 10 bilješki), backlog dopunjen. Provjera prošla (bez dugih crtica, bez ćirilice, sve Park, obje zone u svakoj bilješci).

## Kontekst

Autor ima izvještaj s deset ekonomskih tema iz hrvatskih medija koje se mogu
analizirati kroz podatke na razini firme (bilance, RDG, novčani tok). Cilj nije
analiza, nego **preliminarni nacrti, placeholderi za buduće postove**. Brze
bilješke za kasnije, ne gotove analize. Ne dohvaćamo podatke i ne spajamo izvore.

Dvije tvrde okolnosti oblikuju nacrte.

1. **Sve teme počivaju na financijskim stupcima** (D/E, tekuća likvidnost, marže,
   EBITDA, dobit, zalihe, dug). Po `MEMORY.md` i memoriji
   (`gfi-db-afs-column-mapping-broken`), ti stupci **nisu provjereni** — mapiranje
   bNNN ≠ FINA AOP je nepouzdano. Zato je svaki od deset postova legitimno
   *budući* posao, **Park dok se financijski stupci ne pročiste**. To je i razlog
   zašto su placeholder bilješke pravi format.
2. **Brojke nisu naše.** Postoci iz izvještaja (82%, +13,2%, +10% itd.) su
   medijski/sekundarni izvori. Kućno pravilo. Svaka brojka u postu vodi do
   `outputs/`. U bilješkama te brojke idu pod *Vanjske brojke za provjeru*, nikad
   kao naš nalaz.

## Što isporučujemo

`drafts/balance-sheet/` s jedanaest datoteka. Indeks plus deset bilješki, jedna
po temi. Plus dopuna `_workflow/ideas-backlog.md`, sekcija **Parked**, deset
linija koje pokazuju na bilješke.

Sve na hrvatskom, uključujući blok za izradu. Dubina. *idea-note + skeleton* —
oblik iz idea-playbooka plus kratki hrvatski kostur posta s naslovima-tvrdnjama i
[KUT] mjestima, da budući autor može dizati izravno.

### Raspored datoteka

```
drafts/balance-sheet/
  00-index.md                      indeks, tablica deset tema + status
  01-zaduzenost-i-likvidnost.md
  02-turizam-marze-i-troskovi.md
  03-nekretnine-investitori.md
  04-energija-i-konkurentnost.md
  05-place-i-marze.md
  06-trgovina-marze.md
  07-drzavne-firme.md
  08-poljoprivreda-subvencije.md
  09-msp-financiranje.md
  10-ict-i-startupi.md
```

### Format jedne bilješke

Dvije zone u jednoj datoteci. Gore kostur posta koji se može dizati, dolje
blok za izradu. Sve u kućnom glasu (kratko, prezent, strelice, točke umjesto
dvotočja, kurziv umjesto navodnika, brojka vodi).

```
# [Naslov, udica] — [podnaslov, doslovna linija nalaza]

[Otvaranje. Opener orijentira na temu, bridge poziva (hortativ, npr. Odgovorimo)
 i imenuje obećanje. Stub, jedna do dvije rečenice.]

## [Naslov-tvrdnja 1]
[Caption grafa, jedna linija.]
[Stub proze. Brojka vodi, promjena strelicom.]
[KUT] [kut u jednoj rečenici]

## [Naslov-tvrdnja 2]
...

## Tko je dobio, a tko izgubio    (gdje podaci to nude)
Dobitnici. [...]  Gubitnici. [...]

[KUT — glavna interpretacija] [središnji kut]

[Payoff. So-what koji zatvara, prije Napomena. Stub.]

## Napomene
- Izvor. [FINA GFI db_afs + dopunski izvor iz izvještaja]
- Tablica. `db_afs`
- Stupci / omjeri. [koji financijski stupci/omjeri trebaju]
- Oprez. [obuhvat + financijski stupci još nepročišćeni]

---

## Bilješke za izradu
- Nalaz (očekivani). [hipoteza s grubom magnitudom]
- Podaci. [tablica, stupci/omjeri, status povjerenja — svi traže financijske
  stupce, danas NEPOUZDANO]
- Kut. [KUT u jednoj liniji]
- Vanjske brojke za provjeru. [medijske brojke iz izvještaja + izvor, jasno
  označene kao za provjeru, nisu naš nalaz]
- Mediji / izvori. [Lider, Jutarnji, Index... + FINA/HNB/DZS/ZSE]
- Težina. mala / srednja / velika
- Verdikt. Park — čeka čišćenje financijskih stupaca GFI baze.
```

`00-index.md` nosi kratak uvod (čemu mapa služi, da su sve teme Park), pa tablicu
deset tema. Kolone. # / Tema / Ključni omjeri / Izvor podataka / Mediji / Datoteka.
Ista logika kao sažeta matrica iz izvještaja, ali s linkom na svaku bilješku i sa
statusom Park.

## Kako gradimo

`Workflow`, jedan prolaz fan-outa, jer ima deset nezavisnih bilješki.

- **Faza 1. Nacrti (10 agenata paralelno).** Jedan agent po temi. Svaki dobije.
  izvod teme iz izvještaja, kućni glas u sažetku, spec formata gore, i tvrde
  okolnosti (brojke su vanjske/za provjeru, financijski stupci nepouzdani →
  Park). Vraća strukturirano `{slug, naslov, podnaslov, markdown}`.
- **Sklapanje (glavna petlja).** Ja pišem deset datoteka na fiksne putanje,
  složim `00-index.md` i dopunim `_workflow/ideas-backlog.md`. Pisanje datoteka
  ostaje determinističko i u mojoj kontroli, agenti samo proizvode sadržaj.
- **Lagana provjera dosljednosti (opcija).** Jedan prolaz da glas i format budu
  ujednačeni kroz svih deset (strelice, bez dugih crtica, naslovi su tvrdnje).
  Lagano, jer su ovo bilješke a ne gotovi postovi.

## Tvrde okolnosti, ugrađene u svaku bilješku

- Nijedna medijska brojka ne stoji kao naš nalaz. Sve idu pod *Vanjske brojke za
  provjeru* s izvorom.
- Svaka bilješka je Park, s istim razlogom. financijski stupci GFI baze još nisu
  pročišćeni.
- Obuhvat nije rast. gdje tema dira broj firmi, ista nota kao u objavljenom
  sektorskom postu.
- Bez `draft:true` post-folder strukture. ovo su `.md` bilješke u `drafts/`, ne
  ulaze u objavljeno stablo `posts/`.

## Dopuna backloga

`_workflow/ideas-backlog.md`, sekcija **Parked**, dodati deset linija u obliku
playbooka (Hook, Finding, Data, Angle, Effort, Verdict), svaka s pokazivačem na
`drafts/balance-sheet/NN-...md`. Postojeća linija "Anything resting on financial
columns..." ostaje kao krovni razlog; deset novih linija je konkretizira.

## Provjera

Ovo su bilješke, ne kod, pa nema skripti za pokrenuti niti brojki za usidriti.
Provjera je uredska.

1. Jedanaest datoteka postoji u `drafts/balance-sheet/`, indeks linka na svih deset.
2. Svaka bilješka ima obje zone (kostur + blok za izradu) i Verdikt Park.
3. Nijedna medijska brojka nije predstavljena kao naš nalaz (grep po
   *Vanjske brojke za provjeru*).
4. `_workflow/ideas-backlog.md` ima deset novih Parked linija s pokazivačima.
5. Glas. naslovi su tvrdnje, promjene su strelice, nema dugih crtica.

## Izvan opsega

Dohvat podataka, čišćenje financijskih stupaca, build skripte, grafovi, render.
Sve to čeka da financijski stupci postanu pouzdani. Ovaj zadatak staje na
bilješkama za budućnost.
