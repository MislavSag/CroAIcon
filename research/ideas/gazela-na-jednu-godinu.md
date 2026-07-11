# Gazela na jednu godinu. Brzi rast se u Hrvatskoj gotovo nikad ne ponavlja
*A gazelle for one year. High growth in Croatia almost never repeats.*

**Status.** Brainstorm 2026-07-11, kritičar: **build now** (rang 1/5). Leća: trajanje i dinamika. Effort: **mali**.

## Kuka

Javna rasprava o brzorastućim firmama je statična. Tko je ovogodišnja gazela, tko je dobio nagradu, koga subvencionirati. Nitko nije izmjerio traje li taj rast. Reframe u zombi-stilu: brzi rast nije svojstvo firme nego *spell* — koliko traje i koja je vjerojatnost da se ponovi. Daunfeldt i Halvarsson (2015) na švedskim podacima nalaze da su gazele "one-hit wonders". Hrvatska replika ne postoji.

## Očekivani nalaz

Medijan trajanja spella brzog rasta je jedna godina. Firma iz gornjeg decila rasta zaposlenosti ima ~15 % vjerojatnosti da to ponovi iduće godine, prema ~10 % čistog slučaja. **Headline broj: od 100 ovogodišnjih gazela, njih ~15 su gazele i dogodine — a 10 bi bilo i bacanjem novčića.** Nalaz je objavljiv u oba smjera: perzistencija je priča, i slučajnost je priča.

## Podaci & varijable

- `db_afs`: `employeecounteop` (POUZDAN) za stope rasta na firmama s ≥ 10 zaposlenih, `nacerev21` (POUZDAN) za sektorski rez, `subjecttaxnoid` + `reportyear` kao kralježnica panela.
- `b110` poslovni prihod (AUDITIRAN, objavljen u postu o zaduženosti) kao robusnosna mjera rasta.
- Bez vanjskih izvora. Jedina otvorena ovisnost: b110/b125 vintage-provjera, već u checklisti zombi-plana.

## Kako izgraditi

1. Dedupe (`subjecttaxnoid`, `reportyear`) — poznati quirk dupliciranih redaka.
2. Baza: firme s `employeecounteop >= 10` u baznoj godini (OECD-ov prag). Godišnja stopa rasta zaposlenosti; gornji decil unutar godine = gazela.
3. Jezgra: tranzicijska tablica P(gazela u t+1 | gazela u t) po godinama, protiv baznih 10 %. Plus distribucija duljine spella (udio gazela kojima spell traje točno jednu godinu).
4. Robusnost kao sadržaj, ne fusnota: OECD 3-godišnja definicija (prosjek 20 %/god kroz 3 godine) i rast `b110` prihoda kao cross-check.
5. Sektorski rez: gdje žive rijetki ponavljači (I vs J vs C).

## Grafovi

- "100 gazela" waffle/bar: ponavljači vs one-hit wonderi.
- Linija repeat-ratea po godinama 2003-2024.
- Sektorski bar ponavljača.

## Zamke

- Mean reversion + mjerna greška headcounta mehanički proizvode ne-perzistenciju → pošten okvir: nalaz je presuda o *ciljanju* politika (nagrade, subvencije po prošlogodišnjem rastu), nikad "rast ne postoji".
- Mali nazivnici čine stope rasta skakutavima → zato prag 10+, i to se kaže.
- Prosinački end-of-period headcount šumi u sezonskim sektorima → turizam s dodatnim oprezom.
- Headline je rank-based (decili) → winsorizacija nepotrebna.

## Logged form (idea playbook)

- **Hook.** Gazela na jednu godinu. Brzi rast se gotovo nikad ne ponavlja.
- **Finding.** Repeat-rate gazela ~15 % prema ~10 % slučaja; medijan spella 1 godina.
- **Data.** `employeecounteop`, `nacerev21` (pouzdani) + `b110` (auditiran). Sve dostupno.
- **Angle.** [KUT] Biranje pobjednika po lanjskom rastu je lutrija — premisa Gazela i scale-up subvencija pada na novčić.
- **Effort.** Mali. Jedna skripta, tri grafa.
- **Verdict.** Build now. Najmanji build u seriji, čisti povjereni stupci, kontrarni test protiv imenovane nagrade (Lider/FINA Gazele) i politike (HAMAG/EU scale-up), izravna hrvatska replika Daunfeldt & Halvarsson (2015).
