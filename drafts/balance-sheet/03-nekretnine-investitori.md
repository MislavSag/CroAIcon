# Cijene rastu na ekranu, bilance se pune u tišini -> Dok mediji broje indeks cijena, GFI bilance investitora u nekretnine bilježe gdje stvarno sjedi rizik, u zalihama, hipotekama i predugovorima

*Bilješka za budući post. Sve brojke su za provjeru, nisu naš nalaz. Tema čeka čišćenje financijskih stupaca GFI baze.*

Cijena kvadrata je već pet godina najglasnija brojka u zemlji. [No cijena je ono što kupac vidi. Bilanca investitora je ono što kupac ne vidi.] Pogledajmo nekretninsku priču s druge strane stakla. Ne kroz indeks cijena, nego kroz ono što firme iz NKD 41 (gradnja) i NKD 68 (poslovanje nekretninama) knjiže u svojim financijskim izvještajima. [Obećanje. Gdje rastuće cijene zapravo sjede u bilanci, i koliko od toga je dug.]

## Zaliha nekretnina raste brže od prodaje

[Caption grafa. Zalihe nekretnina i potraživanja od kupaca kod NKD 41 i 68, indeks, niz godina.]

[Stub proze. Brojka bi vodila. Zaliha kvadrata na bilanci investitora vs. dinamika prodaje.] [Očekujemo da zalihe nekretnina rastu, dok se prodaja hladi, pa se nenaplaćeni kvadrati gomilaju na bilanci. Magnitudu i smjer ne tvrdimo dok financijski stupci nisu provjereni.]

[KUT] Je li rastuća zaliha znak povjerenja investitora u daljnji rast cijena, ili znak da kupci nestaju, a kvadrati zapinju.

## Dug financira kvadrate, a ne prodaja

[Caption grafa. Omjer hipoteka / imovina i struktura novčanog toka kod investitora u nekretnine.]

[Stub proze. Tko gradi novcem iz poslovanja, a tko novcem iz financiranja.] [Očekujemo da se novčani tok iz poslovanja stišće, a tok iz financiranja širi, pa rast bilance nose hipoteke, ne prodaja. Omjer hipoteka/imovina i smjer toka tvrdimo tek nakon čišćenja stupaca.]

[KUT] Ako kvadrate sve više drži dug, a sve manje prodaja, rastuća cijena štiti bilancu samo dok cijena raste.

## Tko je dobio, a tko izgubio

Dobitnici. [Investitori s niskim omjerom hipoteka i kvadratima kupljenim ranije. Agencije na transakciji, dok transakcija ima.]

Gubitnici. [Investitori koji su zalihu napunili na vrhu i na dug. Firme oslonjene na kratkoročni najam nakon pravila 80% suglasnosti.]

[KUT - glavna interpretacija] Nove regulacije (porez na nekretnine, pravilo 80% suglasnosti za kratkoročni najam) ne mijenjaju samo cijenu. Preslaguju bilance. Pitanje je tko nakon preslagivanja ostaje s kvadratima koje ne može ni prodati ni iznajmiti.

[Payoff. Stub za so-what. Indeks cijena mjeri raspoloženje tržišta. Bilanca mjeri tko će ostati stajati kad raspoloženje stane. Ovaj post gleda u bilancu.]

## Napomene

- Izvor. FINA, Godišnji financijski izvještaji (`db_afs`), uz križanje s podacima Porezne uprave za NKD 41 i 68.
- Tablica. `db_afs`, filtrirano na `nacerev21` u skupinama 41 (gradnja zgrada) i 68 (poslovanje nekretninama).
- Stupci / omjeri. Zalihe nekretnina, potraživanja od kupaca, hipoteke / imovina, izvanbilančne obveze (predugovori), novčani tok iz poslovanja vs. financiranja. [Svi traže financijske stupce GFI baze.]
- Oprez. Financijski stupci GFI baze još nisu provjereni (mapiranje `bNNN` -> FINA AOP je nepouzdano), pa nijedan omjer ovdje još nije naš nalaz. Gdje tema dira broj firmi u NKD 41 i 68, širi obuhvat baze nije isto što i rast tržišta.

---

## Bilješke za izradu

- Nalaz (očekivani). [Rast cijena u medijima vjerojatno bi se u bilancama investitora pokazao kao rastuća zaliha nekretnina i rastući oslonac na dug, a ne kao rastuća prodaja. U kondicionalu dok financijski stupci nisu provjereni.]
- Podaci. `db_afs`, filtar `nacerev21` 41 i 68. Omjeri. Zalihe, potraživanja od kupaca, hipoteke/imovina, izvanbilančne obveze (predugovori), novčani tok poslovanje vs. financiranje. Status. SVI traže financijske stupce -> danas NEPOUZDANO. Križanje s Poreznom upravom za NKD 41 i 68 kao dopunski izvor.
- Kut. Nekretninu treba čitati iz bilance investitora, ne iz indeksa cijena. Regulacija preslaguje rizik, ne samo cijenu.
- Vanjske brojke za provjeru. (Index.hr, Nacional) Cijene stanova ~udvostručene od 2015. (za provjeru). Q2 2025. indeks cijena plus 13,2% g/g (za provjeru). Prodaja nekretnina minus 13% u prvih 9 mjeseci 2025. (za provjeru). Nijedna od ovih brojki ne ulazi u tijelo kao naš nalaz.
- Mediji / izvori. Mediji. Index.hr, Nacional. Institucije. FINA, Porezna uprava.
- Težina. Velika. (Filtar po NKD je lak, ali cijela teza počiva na financijskim stupcima i vanjskom križanju.)
- Verdikt. Park - čeka čišćenje financijskih stupaca GFI baze.
