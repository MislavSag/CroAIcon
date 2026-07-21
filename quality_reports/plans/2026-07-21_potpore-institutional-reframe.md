# Plan. Institucionalni reframe posta o koncentraciji državnih potpora

Datum. 2026-07-21
Post. `posts/2026-07-drzavne-potpore-koncentracija/index.qmd` (autor Mislav Sagovac, objavljen 2026-07-17)
Zadatak. Preokvirivanje posta iz samostalnog mjerenja u dopunu institucionalne rasprave koja je već u tijeku. Nijedna brojka se ne mijenja.

## Tvrda pravila

1. **Strojevi se ne diraju.** Brojke, isključenje redaka sa statusom `Upozorenje`, OIB filtar, blok reproducibilnosti i sve napomene o ograničenjima ostaju identični. Nijedan `{python}` izraz se ne mijenja.
2. **Rječnik.** Nigdje `klijentelizam`, `pogodovanje`, `netransparentnost`, ni pripisivanje motiva. Nigdje `prazan`, `rupa`, `skriveno` u blizini odjeljka o obuhvatu. Nigdje spomena da nitko nije reagirao na analizu.
3. **Svaka udarna brojka dobiva sljedeću rečenicu s benignim mehanizmom.**
4. **Ne imenovati najveće primatelje.** To je zaseban, kasniji post na provjerenim zapisima registra (HEP i HBOR).
5. Svaka institucionalna tvrdnja mora imati provjeren primarni izvor i živi link. Nepotvrđena tvrdnja se ne piše.

## Izmjene po točkama

| # | Mjesto | Zahvat |
|---|--------|--------|
| 1 | Front matter | Naslov ostaje. Novi podnaslov signalizira komplementarnost, ne prikrivanje. Nove `categories`. `description` na komplementarno uokvirivanje. |
| 2 | Uvod | Otvara se institucionalnim kalendarom, tri datirane činjenice, pa pivot na dimenziju koju izvješća ne prikazuju. Postojeće pitanje pada u drugi odlomak. |
| 3 | Obuhvat | Prvo kredit instituciji (nova javna usluga, najava centraliziranog evidentiranja), pa mjerenje obuhvata kao polazna točka za praćenje napretka. Zatvara se jeftinim rješenjem (objava povijesnih godina u javnoj snimci). |
| 4 | Vrste potpora | Dvije rečenice o energetskoj krizi i privremenim okvirima, plus hrvatski dokumentirani slučaj modela naknade. Briše se `čak`. |
| 5 | Unutar vrste | Jedna rečenica koja rez veže uz Country Report Komisije. |
| 6 | Veličina | Dizajn programa (pragovi za velika ulaganja vs pozivi s mnogo malih dodjela) kao dio objašnjenja omjera. Zatvara se prilikom, ne zahtjevom. |
| 7 | Ponavljanje | Redovita SGEI naknada je godišnja po prirodi, pa je ponavljanje na vrhu očekivano. Otvoreno pitanje je sredina distribucije. |
| 8 | Novi odjeljak prije zaključka | *Gdje se nalaz uklapa u širu raspravu.* Tri odlomka. Draghi i popuštanje pravila, kanaliziranje kroz razvojne institucije, NPOO izvještavanje i reformski smjer. |
| 9 | Zaključak | Nalazi postaju ponude. Decilna tablica u godišnjem izvješću, godišnja usporedba obuhvata registra. Suradnički zatvarač. |
| 10 | Dopuna + metapodaci | Datirani P.S. koji pokazuje da je prozor živ. Linkovi na primarne dokumente. |

## Provjera prije predaje

- `python python/state_aid_concentration_build.py` prošao, izlazi u `outputs/`.
- `quarto render posts/2026-07-drzavne-potpore-koncentracija` prošao.
- Diff pokazuje nula promjena u `{python}` izrazima i u bloku `## Napomene` osim dodanih izvora.
- Svaki novi link dohvaćen i potvrđen.

## Status. Gotovo 2026-07-21

Provjere prošle. Build skripta ponovno pokrenuta, post renderiran, 54 inline `{python}` izraza i `{python}` blok bajt po bajt identični, sve stavke `## Napomene` na mjestu, nula dugih crtica, nula [KUT] markera.

## Odstupanja od brifa, s razlogom

Tri tvrdnje iz brifa nisu prošle provjeru pa su zamijenjene.

1. **Country Report Komisije iz lipnja 2026. ne sadrži traženi odlomak.** SWD(2026) 211 od 3. lipnja 2026. spominje *State aid* četiri puta, sve u uskim tehničkim kontekstima. Nema ničega o boljem ciljanju potpora ni o dominaciji državnih i nekolicine velikih privatnih poduzeća. Zamjena. OECD Ekonomski pregled Hrvatske 2026. od 30. siječnja 2026., citat o imovini poduzeća u državnom vlasništvu od oko 45% BDP-a i oko 4% zaposlenosti, *much higher shares than most OECD and peer economies*. Citat sam provjerio dohvatom stranice.
2. **Model naknade HEP-u nije dogovoren s Komisijom.** Nema odluke Komisije, nema broja predmeta. Riječ je o Odluci Vlade od 14. ožujka 2024. Komisija je na izravno pitanje odgovorila da nema komentara. HEP zato nije spomenut, i zbog pravila o neimenovanju najvećih primatelja. Zamjena. Pregled Komisije o kriznim potporama, gdje su dva njemačka energetska poduzeća u 2022. nosila 75% svih kriznih potpora dodijeljenih u EU-u, a Hrvatska i Rumunjska više od 80% svojih dale kroz jamstva za kredite.
3. **Tvrdnja da europska literatura nema podatke o koncentraciji na razini firmi nije provjerena.** Zamjena je uža i provjerena. Pregled državnih potpora Komisije prati iznose po državama članicama, ciljevima i instrumentima, ali ne po pojedinačnim primateljima.

Ispravljeni datumi iz brifa. Dokapitalizaciju HBOR-a Komisija je odobrila 20. travnja 2026., a provedena je u lipnju. Zakon o pravnim osobama u vlasništvu RH donesen je 15. srpnja 2025., ne 2026. Shema za gorivo u ribarstvu odobrena je 15. lipnja 2026.; 17. srpnja 2026. je datum popisa odobrenih mjera, ne odluke.

## Otvoreno

- Globalni `mislav-humanizer` skill nije instaliran u ovom okruženju (`~/.claude/skills/` sadrži samo `graphify` i `scholar-skill`). Post je Mislavljev, pa glasovni prolaz treba pokrenuti on ili ga treba instalirati.
