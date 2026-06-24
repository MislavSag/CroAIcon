# Bilance kao tema. Deset budućih postova

Mapa deset ekonomskih tema iz hrvatskih medija koje se čitaju iz podataka na razini firme (bilanca, RDG, novčani tok). Svaka tema ima svoju bilješku u ovoj mapi. Bilješke su placeholderi za budućnost, ne gotove analize.

**Sve teme su Park.** Svaka počiva na financijskim stupcima GFI baze (`db_afs`) koji još nisu pročišćeni. Mapiranje `bNNN` na FINA AOP je nepouzdano, pa danas pouzdano stoje samo metapodatkovni stupci (`employeecounteop`, `nacerev21`). Dok se financijski stupci ne potvrde, ovo su hipoteze, ne nalazi.

**Brojke su za provjeru.** Postoci i iznosi u bilješkama dolaze iz medija i sekundarnih izvora. Žive samo u bloku *Vanjske brojke za provjeru* u svakoj bilješci, nikad u tijelu kao naš nalaz. Kućno pravilo. svaka objavljena brojka vodi do `outputs/`.

Svaka bilješka ima dvije zone. gore kostur posta koji se može dizati (dvotaktni naslov, naslovi-tvrdnje, [KUT] mjesta, *## Napomene*), dolje blok *## Bilješke za izradu* (nalaz, podaci, kut, vanjske brojke, težina, verdikt).

## Deset tema

| # | Tema | Ključni omjeri | Izvor podataka | Mediji | Bilješka |
|---|------|----------------|----------------|--------|----------|
| 1 | Zaduženost i likvidnost | D/E, tekuća likvidnost, pokriće kamata | FINA, HNB | Lider, Jutarnji | [01-zaduzenost-i-likvidnost.md](01-zaduzenost-i-likvidnost.md) |
| 2 | Turizam, marže i troškovi | trošak osoblja / prihod, iskorištenost imovine | FINA, CBRE | Jutarnji, N1 | [02-turizam-marze-i-troskovi.md](02-turizam-marze-i-troskovi.md) |
| 3 | Nekretnine, investitori | zalihe, potraživanja, hipoteka / imovina | FINA, Porezna uprava | Index, Nacional | [03-nekretnine-investitori.md](03-nekretnine-investitori.md) |
| 4 | Energija i konkurentnost | EBITDA marža, energija / OPEX | FINA, HGK | Lider, Index | [04-energija-i-konkurentnost.md](04-energija-i-konkurentnost.md) |
| 5 | Plaće i marže | trošak osoblja / prihodi, bruto marža | FINA, DZS | Jutarnji, Lider | [05-place-i-marze.md](05-place-i-marze.md) |
| 6 | Trgovina, marže | obrtaj zaliha, neto marža, dodana vrijednost / zaposleni | FINA, DZS | Index, Jutarnji | [06-trgovina-marze.md](06-trgovina-marze.md) |
| 7 | Državne firme | operativni gubitak, dokapitalizacije, jamstva | FINA, Sudski registar | Nacional, Index | [07-drzavne-firme.md](07-drzavne-firme.md) |
| 8 | Poljoprivreda i subvencije | subvencija / prihod, ROA | FINA, DZS | Index, Jutarnji | [08-poljoprivreda-subvencije.md](08-poljoprivreda-subvencije.md) |
| 9 | MSP, financiranje | poluga, capex, gotovina / imovina | FINA, HNB, HBOR | Lider, HGK | [09-msp-financiranje.md](09-msp-financiranje.md) |
| 10 | ICT i startupi | nematerijalna imovina, cash burn, kapital | FINA, ZSE | Lider, Poslovni | [10-ict-i-startupi.md](10-ict-i-startupi.md) |

## Kako koristiti

- Tema se otključava kad se financijski stupci GFI baze pročiste i potvrde. Tek tada bilo koja od deset prelazi iz Park u Buildable.
- Prije izrade, reproduciraj svaku vanjsku brojku iz primarnog izvora. Ne dizati medijsku brojku u tijelo posta.
- Metoda je u svakoj bilješci (panel, difference-in-differences, usporedba segmenata). Najtežih nekoliko traži i čisto izdvajanje pojedinih firmi po OIB-u ili nazivu.
- Krovni razlog Parka i pokazivač na ovu mapu stoje u `_workflow/ideas-backlog.md`.
