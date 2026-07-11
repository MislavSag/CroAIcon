# Tvrtka od jednog čovjeka. Pola novih firmi nikad ne zaposli nijednog radnika
*A company of one. Half of new Croatian firms never hire a single worker.*

**Status.** Brainstorm 2026-07-11, kritičar: **build now** (rang 3/5). Leća: trajanje i dinamika. Effort: **srednji**.

## Kuka

Svako malo izađe priopćenje o rekordnom broju novoosnovanih firmi kao znaku poduzetničkog preporoda. Statično pitanje: koliko se firmi rodilo. Nitko ne pita: kada nova firma prvi put nekoga zaposli — i zaposli li ikad. Reframe: registracija nije zaposlenje. Vrijeme-do-prvog-zaposlenja je spell, a jeftini ulaz (j.d.o.o. reforma 2012, "firma za 10 kuna") do sada nema nijednu duration-based evaluaciju.

## Očekivani nalaz

Otprilike polovica firmi osnovanih od 2012. ne prijavi nijednog zaposlenog unutar pet godina. Medijan vremena do prvog zaposlenja među budućim poslodavcima: 1-2 godine. Stopa konverzije u poslodavca klizi prema dolje po kohortama. **Headline: udio novih firmi koje unutar 5 godina od osnutka nikad nikoga ne zaposle (~50 %), plus drift po kohortama.** Nalaz preživi i 10 postotnih bodova greške.

## Podaci & varijable

- `db_afs`: `employeecounteop` (POUZDAN — ali audit 0-vs-NULL je nosivi prvi korak), `nacerev21` (POUZDAN), `countyid` (POUZDAN, 100 % popunjen), `subjecttaxnoid` + `reportyear`.
- `godina_osnivanja` preko register joina (~92 % match; restrikcija na kohorte 2012+ zaobilazi survivorship-caveat prije 2010).
- sudreg API `datum_brisanja` (vanjski, besplatan, verificiran) za competing risk: smrt prije prvog zaposlenja.
- Registarski `pravni_oblik` za split j.d.o.o. vs d.o.o. → eksplicitna presuda o reformi.

## Kako izgraditi

1. **Korak nula, prije svega:** audit `employeecounteop` 0 vs NULL na novim ulaznicima — missing nije nula. Ako NULL-ovi dominiraju ranim predajama, headline je napuhan i dizajn treba activity-filter na predaji (`b110 > 0` kao auditirani fallback).
2. Kohorte osnivanja 2012+ preko `godina_osnivanja`. Spell = od godine osnutka do prve godine s `employeecounteop >= 1`.
3. Brisanje (`datum_brisanja`) kao competing risk → **Aalen-Johansen kumulativna incidencija**, ne naivni KM (mrtve firme ne mogu zaposliti).
4. Jezgra: kumulativna incidencija prvog zaposlenja po dobi 1-5 po kohortama; udio never-hires-unutar-5 po kohorti; medijan vremena do prvog zaposlenja među konverterima.
5. Split j.d.o.o. vs d.o.o. preko `pravni_oblik`.

## Grafovi

- Kohortne krivulje konverzije s vidljivom right-censoring zonom za recentne kohorte.
- Županijski choropleth stope konverzije u poslodavca (giscoR poligoni + crosswalk iz zombi-plana).
- Sektorski bar (J solo-kontraktori vs C vs F).

## Zamke

- Vlasnici-direktori na ugovoru o upravljanju ne ulaze u headcount → "nikad ne zaposli" treba jednu pažljivu definicijsku rečenicu na početku.
- Univerzum su inkorporirane firme; obrt je isključen — reći u podnaslovu i Napomenama.
- Firme koje nikad ne predaju GFI ovdje su nevidljive; tvrdnja je uvjetna na ulazak u bazu predaja. Jedna rečenica u Napomenama.
- Recentne kohorte imaju kratke prozore → pokazati cenzuru, nikad ekstrapolirati.

## Logged form (idea playbook)

- **Hook.** Tvrtka od jednog čovjeka. Pola novih firmi nikad nikoga ne zaposli.
- **Finding.** ~50 % kohorti 2012+ bez ijednog zaposlenog unutar 5 godina; konverzija pada po kohortama.
- **Data.** Pouzdani stupci + verificirani registar. Ništa nedostupno.
- **Angle.** [KUT] Registracija nije zaposlenje — rekordna rođenja firmi iz priopćenja pola su ljušture koje nikad ne isplate plaću.
- **Effort.** Srednji. Jedna build skripta nakon što 0-vs-NULL audit prođe.
- **Verdict.** Build now. Distinktan duration-objekt (time-to-first-hire), prva firm-level evaluacija j.d.o.o. reforme, ugrađen kontrarni test protiv HGK/vladinog žanra priopćenja o rekordnim rođenjima.
