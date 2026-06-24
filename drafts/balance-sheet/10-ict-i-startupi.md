# Bilanca bez tvornice -> ICT firme rastu na nematerijalnoj imovini i pretplatama, ne na strojevima

*Biljeska za buduci post, nije nas nalaz. Sve konkretne brojke su za provjeru i stoje samo u bloku Vanjske brojke za provjeru. Tema ceka ciscenje financijskih stupaca GFI baze.*

[Otvaranje. Tradicionalna firma drzi vrijednost u strojevima, zalihama i zgradama. ICT firma drzi je u kodu, ugovorima i ljudima. Odgovorimo kako se ta razlika vidi u bilanci, kad usporedimo NKD 62 i 63 s ostatkom gospodarstva.]

## Digitalna firma nosi imovinu koja se ne moze dotaknuti

[Caption grafa. Udio nematerijalne imovine u ukupnoj aktivi, ICT (NKD 62, 63) naspram tradicionalnih sektora.]

[Stub proze. Brojka bi vodila. (Ocekujemo da je udio nematerijalne imovine, kapitalizirani softver i R&D, kod ICT firmi vidno visi nego u proizvodnji ili trgovini, dok je udio dugotrajne materijalne imovine nizi.)]

[KUT] Je li niska materijalna imovina prednost (lagana, skalabilna firma) ili rizik (malo toga za zalog, tesko financiranje preko banke)?

## Rast prihoda i potrosnja gotovine ne idu uvijek zajedno

[Caption grafa. Rast prihoda naspram operativnog novcanog toka, ICT firme po velicini.]

[Stub proze. (Ocekujemo da dio brzorastucih ICT firmi pokazuje rast prihoda uz negativan ili tanak operativni novcani tok, klasican cash burn, dok zrele firme generiraju gotovinu.) Ovdje treba paziti na obuhvat. Vise ICT firmi u bazi ne znaci nuzno rast sektora, dio je sireg obuhvata GFI baze (vise u Napomenama).]

[KUT] Gdje je granica izmedu zdrave investicije u rast i firme koja samo trosi tudji kapital?

## Pretplate i inozemni klijenti mijenjaju strukturu obveza i potrazivanja

[Caption grafa. Udio odgodjenih prihoda i inozemnih potrazivanja u bilanci ICT firmi.]

[Stub proze. (Ocekujemo vidljiv trag pretplatnickog modela kroz odgodjene prihode, te visok udio potrazivanja od inozemnih klijenata, izvozni karakter sektora.) Struktura temeljnog kapitala i krugovi dokapitalizacije mogli bi se citati iz promjena kapitala kroz godine.]

[KUT] Sto odgodjeni prihod govori o predvidljivosti poslovanja, i tko ga uopce ima u Hrvatskoj?

[KUT - glavna interpretacija] Digitalna ekonomija nije manja verzija stare, nego druga vrsta firme. Kapitalno laka, nematerijalno teska, izvozno okrenuta. Pitanje za post je mjeri li ju nasa bilanca uopce dobro, ili joj klasicni omjeri promase narav.

[Payoff. Stub za so-what. (Ako se potvrdi da ICT firme nose vrijednost u nematerijalnoj imovini i ugovorima, onda standardni pokazatelji zaduzenosti i likvidnosti, gradjeni za firme sa strojevima, daju krivu sliku. Post bi trebao pokazati gdje stari omjeri zakazu i koji ih bolje opisuju.)]

## Napomene

- Izvor. FINA, Godisnji financijski izvjestaji (db_afs). Dopunski, vanjski medijski i institucionalni izvori samo za kontekst, ne za nas nalaz.
- Tablica. `db_afs`
- Stupci / omjeri. Trazi financijske stupce. Nematerijalna imovina, dugotrajna materijalna imovina, ukupna aktiva, prihodi, operativni novcani tok, odgodjeni prihodi, potrazivanja (domaca i inozemna), temeljni kapital. Sektor iz `nacerev21` (NKD 62, 63). Omjeri. Intenzitet nematerijalne imovine, rast prihoda naspram novcanog toka, udio odgodjenih prihoda, udio inozemnih potrazivanja.
- Oprez. Financijski stupci GFI baze jos nisu procisceni, mapiranje bNNN na FINA AOP je nepouzdano, pa nijedan financijski omjer danas ne stoji. Uz to, broj firmi u bazi raste dijelom zbog sireg obuhvata, ne stvarnog rasta sektora, to razdvojiti prije nego se broj firmi koristi kao mjera rasta.

---

## Biljeske za izradu

- Nalaz (ocekivani). ICT firme (NKD 62, 63) trebale bi nositi vise nematerijalne i manje materijalne imovine od tradicionalnih sektora, uz vidljiv trag pretplata (odgodjeni prihodi) i izvoza (inozemna potrazivanja). Magnitude tek u kondicionalu dok stupci nisu cisti.
- Podaci. Tablica `db_afs`. Stupci. Nematerijalna i materijalna imovina, ukupna aktiva, prihodi, novcani tok, odgodjeni prihodi, potrazivanja, temeljni kapital, plus `nacerev21` za sektor. Omjeri kao gore. Status povjerenja. SVI omjeri trazze financijske stupce -> danas NEPOUZDANO. Pouzdani su samo metapodatkovni stupci (`nacerev21`, `employeecounteop`).
- Kut. Digitalna firma je druga vrsta firme. Mjere li ju klasicni bilancni omjeri dobro, ili joj promase narav?
- Vanjske brojke za provjeru. (Sve za provjeru, nisu nas nalaz.) ICT izvoz 2,14% BDP-a (2022.). Projekcija digitalne ekonomije 15% BDP-a do 2030. Hrvatska 6. u EU po rizicnom kapitalu. Infobip i Rimac Automobili zajedno oko 4,1% BDP-a. Izvor za provjeru. Lider, Poslovni.hr, te institucionalno FINA i ZSE.
- Mediji / izvori. Mediji. Lider, Poslovni.hr. Institucije i izvori. FINA, ZSE.
- Tezina. Velika. Trazi cijeli set financijskih stupaca i njihovo ciscenje, plus razdvajanje obuhvata od rasta.
- Verdikt. Park - ceka ciscenje financijskih stupaca GFI baze.
