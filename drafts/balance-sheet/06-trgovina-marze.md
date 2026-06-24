# Police pune, marže tanke -> Trgovina na malo raste godinama, a hrvatski lanci po dodanoj vrijednosti i marži zaostaju za internacionalnima

*Bilješka za budući post. Sve konkretne brojke su za provjeru, nisu naš nalaz. Tema čeka čišćenje financijskih stupaca GFI baze.*

[Otvaranje. Opener. Potrošnja u trgovini na malo raste već godinama. Bridge. Pogledajmo tko taj rast pretvara u maržu, a tko ga samo proveze kroz police. Promijenimo pitanje s *koliko se prodaje* na *koliko ostaje trgovcu*. Spoji gore na podnaslov (rast vs marža), dolje na prvu brojku, omjer obrtaja zaliha.]

## Rast prometa ne znači rast marže

[Caption grafa. Realni promet trgovine na malo vs dodana vrijednost po zaposlenom, domaći lanci, [razdoblje].]

[Stub proze. Brojka bi vodila. [Očekujemo da promet raste brže nego dodana vrijednost po zaposlenom, jer rast ide kroz volumen, ne kroz maržu.] Hipoteza, ne nalaz. Brojka stiže tek nakon čišćenja stupaca.]

[KUT] Je li rast potrošnje stvarna snaga sektora ili samo prolazi kroz njega prema dobavljaču.

## Domaći lanci drže zalihe duže nego internacionalni

[Caption grafa. Koeficijent obrtaja zaliha, domaći (Konzum, Tommy, Plodine) vs internacionalni (Lidl, Spar, Kaufland), [razdoblje].]

[Stub proze. [Očekujemo da internacionalni lanci okreću zalihe brže, a domaći vežu više kapitala u policama.] Veži uz ciklus obrtnog kapitala. Brza zaliha plus odgoda plaćanja dobavljaču finansira rast bez vlastitog novca. Hipoteza, ne tvrdnja.]

[KUT] Razlika u obrtaju zaliha kao razlika u poslovnom modelu, ne samo u efikasnosti.

## Internacionalni lanci dobivaju, domaći zaostaju

[Samo ako financijski stupci to potvrde nakon čišćenja. Za sada hipoteza u kondicionalu.]

Dobitnici. [Očekivano internacionalni lanci. Brži obrtaj zaliha, viša dodana vrijednost po zaposlenom, dobavljač financira ciklus (obveze prema dobavljačima > potraživanja od kupaca).]

Gubitnici. [Očekivano domaći lanci. Sporiji obrtaj, tanja neto marža, duži ciklus obrtnog kapitala.]

[KUT - glavna interpretacija] Održivost potrošnje ne ovisi o tome koliko Hrvati troše, nego o tome posluju li trgovci dovoljno čvrsto da prežive kad rast stane. Tanka marža u dobrim godinama je rizik za loše.

[Payoff. Stub za so-what. [Police su pune dok promet raste. Pitanje je što ostaje trgovcu kad se rast ohladi, a marža je već tanka.] Ne sažetak. Jedna do dvije rečenice, tek kad brojke sjednu.]

## Napomene

- Izvor. FINA, Godišnji financijski izvještaji (`db_afs`). Dopunski. DZS (promet trgovine na malo), EIZ (kontekst).
- Tablica. `db_afs`
- Stupci / omjeri. Koeficijent obrtaja zaliha, bruto marža, neto marža, dodana vrijednost po zaposlenom, ciklus obrtnog kapitala, obveze prema dobavljačima vs potraživanja od kupaca. Svi traže financijske stupce.
- Oprez. Financijski stupci GFI baze još nisu pročišćeni (mapiranje `bNNN` != FINA AOP je nepouzdano), pa nijedan omjer još nije pouzdan. Gdje tema dira broj firmi po segmentu, širi obuhvat baze nije stvarni rast.

---

## Bilješke za izradu

- Nalaz (očekivani). Hrvatski lanci bi po dodanoj vrijednosti po zaposlenom i neto marži zaostajali za internacionalnima, uz sporiji obrtaj zaliha i duži ciklus obrtnog kapitala. Gruba magnituda tek nakon čišćenja stupaca.
- Podaci. `db_afs`, financijski stupci (zalihe, prihod, trošak prodanog, obveze, potraživanja) plus `employeecounteop` za nazivnik i `nacerev21` za izdvajanje trgovine na malo. Status povjerenja. Metadata stupci pouzdani, financijski NEPOUZDANI danas. Svi ključni omjeri traže financijske stupce.
- Kut. Održivost potrošnje se mjeri snagom trgovca, ne visinom prometa. Tanka marža u rastu je skriveni rizik.
- Vanjske brojke za provjeru. 33 uzastopna mjeseca realnog godišnjeg rasta (do prosinca 2025.), izvor Index.hr / Jutarnji list. Cijela 2025. plus 3,6% realno. Prosinac 2025. hrana, piće i duhan plus 4,0%, neprehrana plus 5,6% realno. EIZ upozorava na neizvjesnije razdoblje. Sve označeno kao za provjeru, ne naš nalaz.
- Mediji / izvori. Mediji. Index.hr, Jutarnji list. Institucije. FINA, DZS, EIZ.
- Težina. Velika. Tema u potpunosti ovisi o financijskim stupcima, plus usporedba pojedinačnih lanaca traži čisto izdvajanje firmi po OIB-u / nazivu.
- Verdikt. Park - čeka čišćenje financijskih stupaca GFI baze.
