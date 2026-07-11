# Slavonija je izgubila ljude, a ne poslove. Zaposlenost u slavonskim firmama desetljeće nakon egzodusa
*Slavonia lost people, not jobs. Firm employment in the five counties a decade after the exodus.*

**Status.** Brainstorm 2026-07-11, kritičar: **build now** (rang 4/5). Leća: diskurs, kontrarno. Effort: **mali**.

## Kuka

O Slavoniji se raspravlja isključivo kroz demografiju: egzodus, iseljavanje, "Slavonija umire". Paralelno vlada prodaje "Projekt Slavonija" kao uspjeh. Obje strane barataju stanovništvom — nitko ne gleda seriju radnih mjesta u firmama. Depopulacija i uništavanje poslova su različite serije, a panel ima drugu od njih.

## Očekivani nalaz

Zaposlenost u firmama pet slavonskih županija rasla je dvoznamenkasto od 2013. (vjerojatno +10-20 %), dok je stanovništvo palo otprilike desetinu — poslovi po preostalom stanovniku oštro su porasli. Ali jaz prema nacionalnom rastu zaposlenosti (~+25-30 %) se ŠIRIO. **Headline: zaposlenost u firmama pet slavonskih županija 2013 → 2024 (+X %), uz otprilike desetinu manje stanovnika.** Dvostruka presuda: pada i "Slavonija umire" i "Projekt Slavonija radi".

## Podaci & varijable

- `db_afs`: `employeecounteop` po `countyid` × `reportyear` (oba POUZDANA, countyid 100 % popunjen — verificirati `ref_county` join i pet slavonskih šifri u DB sesiji, flag iz zombi-plana), `nacerev21` (POUZDAN) za sektorski miks slavonskog rasta, `godina_osnivanja` za stope rađanja firmi 2012+.
- Vanjsko: DZS county employment xlsx kao robusnosni nazivnik (širi obuhvat, break serije 2025) i DZS popis/procjene stanovništva po županijama za per-capita liniju.

## Kako izgraditi

1. Zbrojiti `employeecounteop` po `countyid` × `reportyear` 2013-2024. **Prvo potvrditi pet slavonskih county šifri protiv `ref_county`** (join je u zombi-planu neverificiran).
2. Tri serije: indeks zaposlenosti pet županija (2013=100), nacionalni indeks, poslovi po stanovniku (DZS procjene interpolirane između popisa).
3. Po MEMORY pravilu: voditi sa zaposlenošću, nikad brojem firmi (širenje obuhvata glumi rast). Balanced-panel varijanta (firme prisutne i 2013 i 2024) kao robusnosna linija koja razdvaja stvarni rast od širenja baze.
4. Sektorska dekompozicija slavonskog rasta: koje NKD sekcije ga nose (para-javni sektori vs prerađivačka vs trgovina) — prirodni [KUT] follow-up "kakvi poslovi".

## Grafovi

- Twin-line divergencija: poslovi vs stanovništvo za pet županija.
- Rangirani bar 21 županije po desetljetnom rastu zaposlenosti, slavonskih pet istaknuto.

## Zamke

- GFI baza isključuje obrt i OPG-ove — velik komad slavonskog rada. Tvrdnja je o zaposlenosti u firmama; u podnaslov i Napomene.
- HQ efekt: zagrebački lanac knjiži slavonske trgovine u Zagrebu → pristranost PROTIV nalaza; nalaz je donja granica. Reći smjer i ići dalje.
- Popis je desetljetni; per-capita linija koristi DZS godišnje procjene između popisa.
- DZS robusnost je obavezna jer je Slavonija poljoprivredno teška.

## Logged form (idea playbook)

- **Hook.** Slavonija je izgubila ljude, a ne poslove.
- **Finding.** Zaposlenost u firmama +10-20 % od 2013. uz −10 % stanovnika; jaz prema nacionalnom rastu ipak se širi.
- **Data.** Dva pouzdana stupca + dvije javne DZS datoteke.
- **Angle.** [KUT] Depopulacija i uništavanje poslova su različite serije — Hrvatska se svađala samo oko prve, a druga pokazuje suprotno.
- **Effort.** Mali. County group-by, jedna sesija.
- **Verdict.** Build now. Maksimalan identity hook (svaki čitatelj iz pet županija), kontrarno prema dvije imenovane naracije istovremeno, magnitude na obje polovice paradoksa.
