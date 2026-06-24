# Struja koja jede maržu -> Energetski sok pomiče EBITDA maržu najizloženijih industrija, a kapital bježi u učinkovitost

*Bilješka za budući post. Sve konkretne brojke su vanjske i za provjeru, nisu naš nalaz. Tema čeka čišćenje financijskih stupaca GFI baze.*

Cijena energije udari prvo onamo gdje je trošak energije najteži. Metal, kemija, cement, prehrana. [Pogledajmo nosi li sok 2021. do 2024. mjerljiv trag u maržama tih sektora, i tko ga je platio. (stub otvaranja, proza fali)]

## Trošak energije razdvaja industriju na dvije skupine

[Caption grafa. Udio troška energije u ukupnim operativnim troškovima, po sektorima, jedna godina.]

[Stub proze. Brojka bi vodila. (ovdje bi išao udio energetski intenzivnih sektora naspram ostatka, npr. metal i cement na vrhu, usluge na dnu.) Očekujemo da se firme dijele u dvije jasne skupine -> energetski intenzivne i ostale. Magnituda još nije izračunata iz baze.]

[KUT] Granica izloženosti nije sektor nego struktura troška. Dvije firme u istoj NACE skupini mogu biti na suprotnim stranama soka.

## Sok stišće maržu tamo gdje je trošak energije najveći

[Caption grafa. EBITDA marža po skupini izloženosti, 2021. do 2025., prije i poslije soka.]

[Stub proze. (ovdje difference-in-differences. Energetski intenzivne firme kao tretirana skupina, ostale kao kontrola, prijelom oko 2022.) Očekivali bismo da marža intenzivnih firmi padne brže i dublje nego kod kontrole. Razlika razlika je nalaz. Sve brojke čekaju pročišćene financijske stupce.]

[KUT] Pad marže nije isto što i propast. Pitanje je je li sok pojeo dobit ili samo pomak prema kupcu kroz cijenu.

## Prijenos troška, a ne izloženost, dijeli pobjednike od gubitnika

Dobitnici. [Firme s niskim udjelom energije i firme koje su trošak prenijele na cijenu. (za provjeru iz baze.)]

Gubitnici. [Energetski intenzivne firme koje cijenu nisu mogle dignuti -> marža apsorbira udar. (za provjeru iz baze.)]

[KUT - glavna interpretacija] Prava priča nije koliko je struja poskupjela, nego tko ju je uspio proslijediti dalje. Prijenos troška dijeli pobjednike od gubitnika, ne sama izloženost.

[Payoff. Stub za so-what. (ovdje zatvaranje: ako kapital bježi u energetsku učinkovitost, capex u dodacima dugotrajnoj imovini i promjene obrtnog kapitala pokazuju gdje industrija plaća prilagodbu. Tko ulaže, opstaje. Tko ne, gubi maržu trajno.) Proza fali.]

## Napomene

- Izvor. FINA, Godišnji financijski izvještaji (db_afs). Dopunski. HGK, HUP za sektorski kontekst.
- Tablica. `db_afs`
- Stupci / omjeri. Trošak energije / ukupni operativni troškovi. EBITDA marža (2021. do 2025.). Capex u energetsku učinkovitost (dodaci dugotrajnoj imovini). Promjene obrtnog kapitala. NACE (`nacerev21`) za sektorsku podjelu, broj zaposlenih (`employeecounteop`) za veličinu.
- Oprez. Svi traženi financijski stupci jos su nepročišćeni. Mapiranje bNNN na FINA AOP je nepouzdano. Gdje se temom dira broj firmi, širi obuhvat baze nije stvarni rast.

---

## Bilješke za izradu

- Nalaz (očekivani). EBITDA marža energetski intenzivnih sektora (metal, kemija, cement, prehrana) trebala bi pasti jače od kontrole nakon 2022., uz razliku razlika kao mjeru soka. Magnituda nepoznata do pročišćenih stupaca.
- Podaci. `db_afs`. Trošak energije / OPEX, EBITDA marža, capex (dodaci dugotrajnoj imovini), obrtni kapital, `nacerev21`, `employeecounteop`. Status povjerenja. Svi financijski omjeri traže financijske stupce -> danas NEPOUZDANO. Pouzdani su samo `nacerev21` i `employeecounteop`.
- Kut. Prijenos troška, ne izloženost, dijeli pobjednike od gubitnika.
- Vanjske brojke za provjeru. Cijene struje za firme oko 18% iznad EU prosjeka (za provjeru, izvor Lider / Index.hr / HGK). Industrijske cijene struje udvostručene 2021. do 2024. (za provjeru, izvor Lider / Index.hr). Ne ulaze u tijelo kao naš nalaz.
- Mediji / izvori. Mediji. Lider, Index.hr. Institucije. FINA, HGK, HUP.
- Težina. Velika. Difference-in-differences traži čiste financijske stupce i pažljivu definiciju tretirane skupine.
- Verdikt. Park - ceka ciscenje financijskih stupaca GFI baze.
