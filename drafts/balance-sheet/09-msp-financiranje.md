# Likvidni, a žedni kapitala -> Hrvatski MSP nisu prezaduženi i sjede na gotovini, a financiranje teško stiže do onih s pravim ograničenjem

*Ovo je bilješka za budući post, nije gotov nalaz. Sve konkretne brojke su za provjeru i čekaju reprodukciju iz vlastitih podataka. Tema čeka čišćenje financijskih stupaca GFI baze.*

Mali i srednji poduzetnici nose najveći dio zaposlenosti, a tuže se na pristup kapitalu. Paradoks. Niska poluga, dobra likvidnost, a investicija manja nego što bi se očekivalo. Odgovorimo na jedno pitanje. Stiže li javno financiranje (EIB, HBOR) firmama sa stvarnim kreditnim ograničenjem, ili onima koje su već financijski jake. [Stub. Otvaranje vežemo na podnaslov gore i na prvi omjer dolje.]

## MSP sjede na gotovini, a poluga je niska

[Caption grafa. Kapital / imovina i gotovina / ukupna imovina po veličini firme.]

[Stub proze. Brojka bi vodila. Solventnost i likvidni jastuk pišu se omjerom, ne riječju. [Očekujemo da je medijan kapital / imovina kod MSP-a relativno visok, a udio gotovine i likvidne imovine iznad onoga što bi profil žrtve kreditnog ograničenja sugerirao.] Zaduženost niska, gotovina visoka. Profil koji ne viče za kreditom.]

[KUT] Je li niska poluga znak zdravlja ili znak da firme ni ne traže kredit jer ga ne očekuju dobiti.

## Novca ima, a investicija staje

[Caption grafa. Capex i ročnost duga (kratkoročni vs dugoročni) kroz vrijeme.]

[Stub proze. [Očekujemo da investicijska potrošnja zaostaje za likvidnošću, uz dug nagnut prema kratkoj ročnosti.] Kratak dug financira pogon, ne investiciju. Dugoročni dug, koji nosi capex, tanak je. Ako firme imaju jastuk, a ne investiraju, ograničenje nije u bilanci nego negdje drugdje.]

[KUT] Kratka ročnost duga -> investicija staje. Je li to oprez poduzetnika ili ponuda banaka koja ne nudi dugi novac.

## Pristup teče prema već jakima, ne prema ograničenima

Dobitnici. [Stub. Segment MSP-a koji javno financiranje stvarno doseže. Po veličini, sektoru, regiji. Hipoteza, ne nalaz.]

Gubitnici. [Stub. Segment s niskom vanjskom financijskom ovisnošću i visokim jastukom, koji program preskače jer izgleda jak na papiru, ili segment s ograničenjem koji do programa ne dođe.]

[KUT - glavna interpretacija] Ako financiranje teče prema već jakima, mjera ne popunjava jaz nego ga širi. Pravo pitanje nije koliko je novca ušlo, nego je li stiglo do firme koja bez njega ne investira.

[Payoff. Stub za so-what. Likvidni i nezaduženi, a investicija staje. Ako je tako, problem nije cijena ni dostupnost kapitala u prosjeku, nego raspodjela. Novac do onih kojima treba, ili do onih koji ga već imaju.]

## Napomene

- Izvor. FINA, Godišnji financijski izvještaji (`db_afs`). Dopunski. HNB kreditna statistika, HBOR programi.
- Tablica. `db_afs`
- Stupci / omjeri. Ročnost duga (kratkoročne vs dugoročne obveze), kapital / imovina (solventnost), capex (investicijska potrošnja), gotovina i likvidna imovina / ukupna imovina, vanjska financijska ovisnost. Segmentacija po veličini, NKD sektoru, regiji.
- Oprez. Svi navedeni omjeri traže financijske stupce GFI baze. Mapiranje `bNNN` na FINA AOP još je nepouzdano -> tema čeka čišćenje. Gdje se dira broj firmi, širi obuhvat baze nije stvarni rast.

---

## Bilješke za izradu

- Nalaz (očekivani). MSP bi po profilu (niska poluga, visok jastuk gotovine) izgledali financijski jako, a capex bi zaostajao -> ograničenje je u raspodjeli pristupa, ne u prosječnoj bilanci. U kondicionalu dok stupci nisu čisti.
- Podaci. `db_afs`, omjeri iznad (solventnost, likvidnost, ročnost, capex, vanjska ovisnost), uz HNB i HBOR za unakrsnu provjeru. Status povjerenja. SVI omjeri traže financijske stupce -> danas NEPOUZDANO.
- Kut. Stiže li javno financiranje (EIB, HBOR) firmama sa stvarnim ograničenjem ili već jakima.
- Vanjske brojke za provjeru.
  - EIB Grupa. 536 mil. EUR novog financiranja u Hrvatskoj 2025., više od pola za MSP i mid-cap (zeleni i digitalni projekti). Izvor. Lider / EIB. ZA PROVJERU.
  - HR firme u prosjeku relativno nisko zadužene, dobra likvidnost. Izvor. Lider / HGK. ZA PROVJERU.
  - Hrvatska 6. u EU po intenzitetu izdataka za rizični kapital. Izvor. Lider. ZA PROVJERU.
  - Napomena. Nijedna od ovih brojki ne smije ući u tijelo kao naš nalaz dok je ne reproduciramo iz vlastitih podataka.
- Mediji / izvori. Lider, HGK. Institucije. FINA, HNB, HBOR.
- Težina. Velika.
- Verdikt. Park - čeka čišćenje financijskih stupaca GFI baze.
