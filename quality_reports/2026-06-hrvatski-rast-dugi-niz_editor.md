# Editor review. Svi naši usponi i padovi (dugi niz BDP-a)

Pregled posta kakav stoji sada, nakon ugradnje dva rada (Bićanić 2012.;
Bićanić, Deskar-Škrbić i Zrnc, HUB 2016.). Usporedio sam trenutni tekst s
`git diff` protiv zadnjeg commita da precizno odvojim novi materijal od
starog. Fokus je na značenju i luku, ne na gramatici ili brojkama po sebi
(to su druge kritike).

**Sažetak po pitanjima iz zadatka.**

- **Cijepa li novi nalaz ("tempo se poslije 1980. više ne vrati") jedan
  argument na dva?** Djelomično. Vidi Major #1. Ostatak poglavlja "Rast u dva
  naleta" gradi prema centralnoj tezi (metodološka poštenost oko točke reza),
  ali sama tvrdnja o tempu ostaje neiskorištena do kraja.
- **Luta li koji novi odjeljak?** Nijedan odjeljak u cjelini ne luta. Novi
  pasusi (dužnička kriza 1980., dvije rekonstrukcije/sidro, HUB pokazivač za
  konvergenciju) svi ostaju tematski unutar svog odjeljka. Problem nije
  lutanje nego dvoje. jedna tvrdnja ostaje neiskorištena (Major #1), jedan
  pasus tiho ponavlja Napomene (Major #2).
- **Jesu li granice pošteno iskazane?** Uglavnom da, ovo je i dalje najjača
  strana posta (gust niz izričitih ograda, "smjer siguran, brojke nisu"
  refren, jugoslavenska/hrvatska razlika provjerena umjesto tvrđena). Jedna
  pukotina, prag za brojanje pada iskazan dvjema različitim brojkama u tijelu
  i Napomenama (Major #3).
- **Slijeće li payoff?** Da. Zaključak eksplicitno progovara "nešto drugo",
  vraća se na raznolikost padova i trajanje povratka, i otvara jednu liniju
  naprijed ("sljedeći pad neće biti kao prošli"). Jedino omekšanje, spojler
  o konvergenciji odmah prije payoffa pomalo guši prostor (Minor #1).

## Critical

Nema nalaza u ovoj kategoriji.

## Major

**#1. Poglavlje "Rast u dva naleta, prvi jači" (redci 34-42), rečenica "Svaki
je nalet sporiji od prethodnog, a tempo prvog se poslije 1980. više ne vrati."**
Problem. Ovo je nov, samostalan nalaz (u staroj verziji socijalizam i oporavak
su bili izjednačeni na 5,0%, rez na 1980. i formulacija "tempo se ne vrati" su
danas dodani), nosi vlastiti header i vlastitu težinu, ali zaključak ga
nigdje ne pokupi. Payoff (redci 203-207) govori isključivo o raznolikosti
padova i trajanju povratka, ne i o tome da se tempo rasta nikad nije vratio.
Post tako ostavlja dva zasebna "sigurna nalaza" umjesto jednog. Ostatak istog
poglavlja (metodološka poštenost o rezu na 1980. umjesto 1986., protuprimjer
"oba bi naleta izgledala jednako po 5,0%") ispravno gradi prema centralnoj
tezi o osjetljivosti na izbor granice, pa nije potrebno rezati cijeli pasus.
Fix. Ili vezati tvrdnju natrag u payoff jednom rečenicom (npr. da ni tempo
rasta, kao ni dubina padova, više ne obećava povratak na staru brzinu), ili
stišati je u headeru/tekstu na razinu scene-settinga za poglavlje o padovima,
umjesto da stoji kao vlastita najava.

**#2. Devedesete, pasus "Vrh nije jedini izbor..." (redci 165-170) naspram
Napomene, bullet "Devedesete" (redci 238-241).** Problem. Tijelo u cijelosti
razrađuje "dva razloga" zašto se Milanovićeva rekonstrukcija i ona Bićanića,
Deskar-Škrbića i Zrnca razilaze, drukčije *sidro* (razina za 1990.) i drukčije
stope kroz ratne godine, bez ikakvog pokazivača prema Napomenama. Napomene
zatim iznose istu tvrdnju, gotovo istim riječima ("sidro, razina uzeta za
1990., i izvor stopa kroz ratne godine"). To je puno ponavljanje pune tvrdnje
na dva mjesta, upravo ono što AGENTS.md zabranjuje. Utoliko je uočljivije jer
tri retka niže, u istom odlomku, post to radi kako treba, "Zabilježeni pad k
tome vjerojatno precjenjuje stvarni (zašto, u *Napomenama*)" jasno pokazuje
umjesto da unaprijed ponavlja tri razloga. Fix. U tijelu ostaviti samo
"Razloga su dva, drukčije sidro i drukčije stope kroz ratne godine (više u
*Napomenama*)." i prebaciti detalj (koja razina, koji izvor) isključivo u
Napomene, po uzoru na rečenicu tri retka niže u istom pasusu.

**#3. Prag za brojanje pada, tijelo (redci 118-119) naspram Napomene, bullet
"Padovi i prag" (redci 224-226).** Problem. Tijelo kaže "Nijedan ne prijeđe
minus 5%, ispod praga iz *Napomena*", što čitatelja upućuje da je 5% prag iz
Napomena. Napomene pak kažu "Padom brojimo epizodu dublju od oko 7%." Dvije
različite brojke predstavljene kao ista stvar, prag za brojanje pada. Provjerio
sam `outputs/tables/gdp_drawdowns.csv`, stvarni prag (gdje `major` prelazi iz
FALSE u TRUE) leži negdje između 4,9% (1956., najveći isključeni trzaj) i 7,4%
(2020., najmanji ubrojeni pad), pa obje brojke tehnički prežive provjeru, ali
ne mogu obje biti "prag". Ovo je točno vrsta brojke koju je post već jednom
morao učiniti eksplicitnom i dosljednom (vidi MEMORY.md, ista pouka o brojanju
padova). Fix. Ili tijelo kaže "Nijedan ne prijeđe minus 5%, duboko ispod praga
iz *Napomena*" (naglašava da su isključeni trzaji daleko ispod crte, ne da 5%
jest crta), ili obje brojke uskladiti na 7%. Provjeri s number-checkerom koja
je stvarna vrijednost u skripti.

## Minor

**#1. Zaključak, redci 197-201, rečenica "Kratki sažetak, Sloveniju i Austriju
hrvatska staza ne sustiže ni u jednom razdoblju."** Problem. Post upravo kaže
da o konvergenciji ne govori iz ovog niza jer nema usporedni niz, a onda ipak
u istom dahu iznosi tuđi nalaz o konvergenciji, jednu rečenicu prije nego što
se payoff stvarno sliježe ("Ono što ovaj niz pouzdano govori je nešto drugo").
Nije pogrešno, jasno je pripisano (Bićanić, Deskar-Škrbić i Zrnc, 2016.), ali
u zadnjih desetak redaka posta to je treća stvar koja se otvara i odmah
napušta (poslije "povratak nije velika vijest" i "povratak je dijelom
ugrađen"), pa payoff mora probijati kroz gušće grmlje nego što bi trebao.
Fix. Kratiti na pokazivač bez spojlera, "Tko traži razinu prema EU ili
konvergenciju, naći će je kod Bićanića, Deskar-Škrbića i Zrnca (2016.)." i
prepustiti sam nalaz Napomenama ili čitatelju koji klikne.

**#2. Redak 96-98, "Iste godine umre Tito, ali objašnjenje nije u tome...
(Bićanić, Deskar-Škrbić i Zrnc, 2016.)."** Problem, sitnica. Ovo je jedino
mjesto u postu gdje se jedan uzrok tvrdi s punom sigurnošću i suprotstavlja
konkurentskom objašnjenju, u tekstu inače gustom od ograda ("smjer siguran,
brojke nisu" na svakom koraku). Nije netočno niti bez izvora, samo odskače
tonom od ostatka posta. Fix. Nije nužan, ali ako se dotjeruje, blaga ograda
poput "objašnjenje je vjerojatno drugdje" bi držala ton dosljednim s ostatkom
posta.

## [KUT] provjera

Nema nijednog `[KUT]` markera u postu (provjereno pretragom cijele datoteke).
Ovo je dosljedno s postojećim stilom ovog konkretnog posta, koji nikad nije
imao [KUT] blokove čak ni u ranijim verzijama (usporedi s
`posts/2026-06-zagreb-profit/index.qmd` i
`posts/2026-06-zombi-firme-recesija/index.qmd`, koji ih imaju jer su još u
uredničkoj obradi). Ništa nije tiho popunjeno, nema ostataka markera ni u
tijelu ni u Napomenama. Novi materijal (tempo rasta se ne vraća, dužnička
kriza umjesto Tite, konvergencija prema HUB radu) su sve izvedene,
citirane tvrdnje, ne otvorena čitanja podataka koja bi tražila uredničku
odluku, pa nijedno novo mjesto po mom sudu ne traži marker. Jedina bliska
kandidatkinja je sama rečenica iz Major #1 (tempo se ne vraća), ali problem
tamo nije da nedostaje ljudska interpretacija nego da nalaz ostaje visjeti bez
veze na zaključak, što je uređeno gore kao pitanje luka, ne KUT-a.

## Napomene vs. tijelo, opće stanje

Osim Major #2, podjela rada je zapravo dobra i vrijedi je zadržati kao uzor.
Društveni proizvod/BDP pojmovni jaz (redci 135-138 naspram 247-251), razlozi
precjenjivanja pada devedesetih (redak 172 naspram 241-246) i most "što se da
popraviti" (redci 252-256) svi ispravno ostavljaju puni detalj u Napomenama i
u tijelu samo pokazuju prstom. Depresija (redci 69-79 naspram 230-236) dijeli
istu činjenicu (cjenovni mehanizam) na dvije razine specifičnosti, narativnu u
tijelu i tehničku u Napomenama, što je u redu jer nije doslovno ponavljanje.

## Napomena o statusu

Postojeći `quality_reports/2026-06-hrvatski-rast-dugi-niz_qa.md` (ocjena 93,
"spremno za objavu") datira iz prolaska prije ugradnje HUB rada i Bićanić
(2012.), i tvrdi da je prag za pad "eksplicitan u tekstu i Napomenama"
(oko 7%) bez spomena "5%". Taj rezultat je zastario u odnosu na tekst kakav
stoji sad. Post treba novi `/qa-post` prolazak prije objave, ne oslanjanje na
rezultat 93.
