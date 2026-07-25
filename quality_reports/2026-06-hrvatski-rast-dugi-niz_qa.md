# QA. Svi naši usponi i padovi (dugi niz BDP-a)

**Ocjena 94. Spremno za objavu (prag 90).**

Prolaz od 25. srpnja 2026., navečer, nakon ugradnje dvaju radova (Bićanić,
2012. i Bićanić, Deskar-Škrbić i Zrnc, HUB, 2016.). Zamjenjuje jutarnji prolaz
(ocjena 93), koji je vrijedio za tekst prije ugradnje i propustio dva starija
nalaza. Četiri kritičara, detalji u `_style.md`, `_editor.md`, `_numbers.md` i
`_charts.md`. Prvi obračun dao je **62, blokirano**, sa 11 nalaza. Svi su
ISPRAVLJENI u istoj sesiji, stanje niže. Rezidualno na dnu.

## Što je bilo čisto i prije popravka

- **Brojke.** Svih 53 provjereno. 48 se slaže s `outputs/`, 5 uredno pripisano
  literaturi, ništa bez izvora, ništa ustajalo. Drawdown tablica ponovno
  izračunata iz tekućeg `gdp_long.csv` i poklapa se red po red.
- **Interpunkcija.** Nula dvotočja, crta i navodnika u prozi, bez AI tragova.
- **Grafovi, kućni sloj.** Paleta provjerena do piksela na svih sedam PNG-ova.
  Baze stupaca na nuli, bez dvostrukih osi, bez spajanja razina.
- **[KUT] i payoff.** Markera nema i nijedan nije potreban, novi materijal je
  izvorno poduprta činjenica. Payoff sjeda i otvara liniju naprijed.

## Nalazi i popravci

Rubrika iz `_workflow/quality-gates.md`. Dva nalaza koje je style-critic
označio kritičnima primijenjena su niže, jer kritični razred rubrike traži
krivu ili neizvornu brojku, a number-checker je potvrdio da su sve brojke
točne. Riječ je bila o unutarnjim neusklađenostima.

### Veliki nalazi (Major), svi ispravljeni

1. **(bilo minus 10) gdp_7, Tica panel interpolira obje ratne rupe.**
   ISPRAVLJENO. `raw_panels()` sada gradi mrežu svih godina po izvoru pa NaN
   lomi liniju na 1914. do 1919. i 1940. do 1946. Graf ponovno renderiran i
   pregledan, prekidi vidljivi. Nalaz dopisan u MEMORY uz postojeći
   [LEARN:chart] (ista klasa buga, druga funkcija).
2. **(bilo minus 5) Prag brojanja padova, tijelo i Napomene se sudarali.**
   ISPRAVLJENO. Tijelo sada kaže *dobro ispod praga od oko 7% iz Napomena*.
3. **(bilo minus 5) Nova teza bez razrješenja u zaključku.** ISPRAVLJENO.
   Payoff dobio vezu na usponsku stranu. *Ista vrsta sigurnosti vrijedi i za
   uspone. Ne koliko smo točno rasli, nego da je svaki nalet bio sporiji od
   prethodnog.*

### Mali nalazi (Minor), svi ispravljeni

4. **(bilo minus 3) Naslov Letargije mjeri eru, susjedi vrh do dna.**
   ISPRAVLJENO opcijom razdvajanja. Naslov ostaje na eri (2008. do 2014.,
   isto kao stupac na gdp_2), a tekst sada izrijekom razdvaja pad od ere.
   *Dno je 2012., stajanje traje do 2014., a vrh iz 2008. linija prijeđe tek
   2017.*
5. **(bilo minus 3) Sidro odlomak ponavljao Napomene.** ISPRAVLJENO. Tijelo
   skraćeno na *Razloga su dva, drukčije sidro i drukčije stope kroz ratne
   godine (više u Napomenama).* Definicija sidra ostaje u karti pouzdanosti i
   u Napomenama.
6. **(bilo minus 3) Potpis gdp_4 i traka na grafu s dva imena.** ISPRAVLJENO.
   Potpis sada *zastoj od 1980.*, isto kao traka.
7. **(bilo minus 3) Rečenica mehanizma 1980. maraton.** ISPRAVLJENO. Razbijena
   u tri rečenice.
8. **(bilo minus 3) *Oko minus 33%* za sva tri izvora.** ISPRAVLJENO. Sada
   *sličan pad, između minus 33 i minus 35% od 1990.* (Maddison minus 32,5,
   Svjetska banka minus 33,5, PWT minus 34,8).
9. **(bilo minus 1) Točka-zarez u Napomenama.** ISPRAVLJENO, zamijenjen s *te*.
10. **(bilo minus 1) Aslund bez dijakritike.** ISPRAVLJENO, Åslund na oba
    mjesta.
11. **(bilo minus 1) Spojler konvergencije pred payoffom.** ISPRAVLJENO,
    ostao goli pokazivač na rad, nalaz izbačen iz zaključka.

### Bez odbitka

- Urednikov prijedlog da se *objašnjenje nije u tome* ublaži u *vjerojatno*
  odbijen. Kuća ne trpi hedging, tvrdnja je izvorno poduprta (HUB rad izrijekom
  razdvaja smrt predsjednika od mehanizma).

## Rezidualno (nije blokirajuće)

- (minus 3) Ime *Letargija* i dalje nosi dva raspona, eru na stupcu i naslovu
  (2008. do 2014.) i pad u strelici (dno 2012.). Tekst to sada izrijekom
  razdvaja, ali dvojnost ostaje ugrađena u dizajn era prema padovima.
- (minus 3) Naslijeđene sitnice iz jutarnjeg prolaza. Miljković (1992.) bez
  mrežnog izdanja, gušće dvostruke zagrade iza strelica na tri mjesta, tijesan
  naslov na gdp_7.

Ocjena poslije popravka. Start 100, minus 6 rezidualno. **94.**

## Provjera nakon popravka

`scripts/update_gdp.R` i `python/gdp_charts.py` ponovno izvršeni, gdp_7
pregledan (prekidi na ratnim rupama vidljivi), `quarto render` prolazi bez
greške, brojke u prozi i dalje se slažu s `outputs/tables/`.
