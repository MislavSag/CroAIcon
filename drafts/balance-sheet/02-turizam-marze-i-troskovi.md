# Pune sobe, tanke marže -> Trošak osoblja jede hotelsku maržu brže nego što dolasci rastu

*Bilješka za budući post, nije gotov nalaz. Sve konkretne brojke su za provjeru i stoje samo u bloku Vanjske brojke za provjeru. Tema čeka čišćenje financijskih stupaca GFI baze.*

[Otvaranje. Turizam nosi oko petine BDP-a, pa kad turizmu padne marža, padne i široj slici. Pogledajmo kamo ide svaka kuna prihoda hotela, jer dolasci rastu, a profit se stišće. Veže se na podnaslov gore i na prvi omjer dolje (trošak osoblja / prihod).]

## Trošak osoblja jede maržu brže nego što prihod raste

[Caption grafa. Omjer trošak osoblja / prihod, hoteli, [godišnji niz]. Jedna linija.]

[Stub proze. Ovdje vodi brojka. Udio plaća u prihodu hotela i njegov pomak kroz godine. [Hipoteza. Omjer trošak osoblja / prihod raste (smjer plus), dok bruto marža pada (smjer minus), jer plaće rastu brže od cijene noćenja.] Brojka ostaje prazna dok financijski stupci ne budu provjereni.]

[KUT] Je li pritisak na maržu sezonski (predsezona, plaće prije prihoda) ili strukturni (manjak radne snage trajno diže cijenu rada).

## Imovina radi pola godine, dug se vrti cijelu

[Caption grafa. Iskoristenost imovine (prihod / ukupna imovina) i likvidnost u predsezoni, [niz po kvartalima ili godinama].]

[Stub proze. Hotel je teška bilanca koja prihod skuplja u par mjeseci. [Hipoteza. Niska iskoristenost imovine i tanak novac u predsezoni, kad plaće, capex i kamate teku, a gosti još ne dolaze.] Dug vezan uz promjenjivu kamatu pojačava stisak. Brojke prazne do čišćenja.]

[KUT] Koliko je hotelska bilanca izložena promjenjivoj kamati i što to znači kad se ciklus okrene.

## Lagana bilanca izmiče stisku, teška ga upija

[Samo ako tema ponudi pobjednike i gubitnike nakon analize. Za sada hipoteza, ne nalaz.]

Dobitnici. [Privatni kratkoročni najam. Niska fiksna imovina, malo zaposlenih, marža manje izložena trošku rada.]
Gubitnici. [Hoteli. Teška bilanca, visok udio plaća, capex i dug koji se vrti cijelu godinu.]

[KUT - glavna interpretacija] Napetost hotel naspram Airbnba. Najam puni krevete uz nisku fiksnu imovinu, hotel nosi ljude, capex i dug. Pitanje za post. Tko zapravo nosi rizik petine BDP-a.

[Payoff. Stub za so-what. Turizam može rasti u dolascima, a istovremeno tanjiti maržu onoga tko drži najviše kapitala. Pune sobe nisu isto što i zdrava bilanca. Slijeće nakon brojki, nije sažetak.]

## Napomene

- Izvor. FINA, Godišnji financijski izvještaji (`db_afs`), dopunski CBRE (RevPAR, hotelski pokazatelji) i medijski navodi (Jutarnji list, N1) samo kao vanjski kontekst.
- Tablica. `db_afs`.
- Stupci / omjeri. Trošak osoblja / prihod, prihod / ukupna imovina (iskoristenost), capex / imovina, likvidnost (predsezona), udio duga uz promjenjivu kamatu. Filtar po `nacerev21` na smještaj i ugostiteljstvo. Svi traže financijske stupce.
- Oprez. Financijski stupci GFI baze još nisu pročišćeni (mapiranje bNNN nije pouzdano jednako FINA AOP), pa nijedan omjer iznad nije izračunat. Broj firmi u sektoru dijelom odražava širi obuhvat baze, ne stvarni rast. Lead na zaposlenost dok se financije ne potvrde.

---

## Biljeske za izradu

- Nalaz (očekivani). Rast troška osoblja stišće hotelsku bruto maržu brže nego što dolasci rastu, dok privatni najam s lakom bilancom izmiče tom pritisku. Magnituda nepoznata do čišćenja, ali smjer očekujemo jasan.
- Podaci. `db_afs`, filtar `nacerev21` (smještaj i ugostiteljstvo). Omjeri. Trošak osoblja / prihod, prihod / imovina, capex / imovina, likvidnost u predsezoni, udio duga uz promjenjivu kamatu. Status povjerenja. SVI omjeri traže financijske stupce -> danas NEPOUZDANO. Pouzdano je za sada samo `employeecounteop` i `nacerev21`.
- Kut. Hotel naspram Airbnba. Tko nosi kapital i rizik petine BDP-a, a tko skuplja maržu bez teške bilance.
- Vanjske brojke za provjeru (medijski navodi, NISU naš nalaz):
  - Zagreb H1 2025. 610.000 dolazaka (plus 2,1% g/g), 1,2 mil. noćenja. Izvor. Jutarnji list / N1. Za provjeru.
  - 1% rasta neto troška plaća povezan s padom bruto marže hotela od 3,7% (medijski navod). Izvor. medijski / CBRE kontekst. Za provjeru.
  - Turizam oko 20% BDP-a. Za provjeru i precizno izvorište.
- Mediji / izvori. Mediji. Jutarnji list, N1. Podaci o sektoru. CBRE. Institucija. FINA (GFI, `db_afs`).
- Težina. Velika. Sve nosi na nepročišćenim financijskim stupcima.
- Verdikt. Park - ceka ciscenje financijskih stupaca GFI baze.
