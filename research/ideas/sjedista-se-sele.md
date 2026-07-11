# Sjedišta se sele. Zagreb gubi firme, ali ne onome kome mislite
*Headquarters on the move. Zagreb is losing firms, but not to whom you think.*

**Status.** Brainstorm 2026-07-11, kritičar: **build now** (rang 5/5). Leća: identitet i geografija. Effort: **srednji**.

## Kuka

"Zagreb usisava cijelu Hrvatsku" je standardna linija regionalne politike — i uvijek se argumentira stokovima: koliko firmi sjedi u Zagrebu, koliki udio dobiti knjiži. Nitko nikad nije vidio TOKOVE. Panel ih vidi: `countyid` po firmi i godini znači da svaku selidbu sjedišta 2002-2024 možemo detektirati. Reframe: od statičnog udjela na origin-destination matricu selidbi.

## Očekivani nalaz

Red veličine 400-800 firmi godišnje mijenja županiju sjedišta (deseci tisuća selidbi kroz 2002-2024), a najveći pojedinačni koridor je Grad Zagreb → zagrebački prsten. Grad je plauzibilno neto GUBITNIK prema vlastitim predgrađima bez prireza (Sveta Nedelja i društvo), dok ostaje najveći bruto atraktor iz ostatka zemlje. **Headline: neto bilanca selidbi Grad Zagreb ↔ prsten 2002-2024, broj firmi i radna mjesta koja su otišla s njima — jedan predznak presuđuje raspravu "Zagreb usisava".**

## Podaci & varijable

- `db_afs` za jezgru: `countyid` po firmi-godini (POUZDAN, 100 % popunjen, Zagreb=21) kao detektor selidbe, `subjecttaxnoid` + `reportyear` (dedupe poznatih duplikata prvo), `employeecounteop` (POUZDAN) za ponderiranje selidbi poslovima, `nacerev21` (POUZDAN) za profil selilaca.
- Vanjsko samo za validaciju: sudreg API `sjediste.sifra_zupanije` — uzorak detektiranih selidbi provjeriti kao stvarne preregistracije, ne rekodiranja.

## Kako izgraditi

1. **Dedupe (`subjecttaxnoid`, `reportyear`) prije svega** — duplikat s različitim countyid fabricirao bi selidbu.
2. Selidba = promjena `countyid` između uzastopnih predanih godina istog OIB-a. **Pravilo perzistencije: nova županija mora trajati ≥ 2 godine** (filtrira rekodiranja i jednogodišnje slučajnosti). Selidba preko rupe u predajama je i dalje selidba, datirana na ponovno pojavljivanje.
3. Origin-destination matrica 21×21 za 2002-2024, brojana po firmama i ponderirana zaposlenošću (poslovi u godini selidbe). Serija neto bilance po županiji.
4. Headline rez: koridor Grad Zagreb (21) ↔ Zagrebačka županija po razdobljima (prije 2010, 2010-e, poslije 2017. kad prstenasti gradovi režu prirez na nulu).
5. **Validacija: ~50 detektiranih selidbi protiv registra** (`sjediste`), po mogućnosti i NN objava. Ako je više od par fantomskih rekodiranja → pooštriti pravilo perzistencije prije objave.

## Grafovi

- Chord/flow dijagram najvećih koridora.
- Choropleth neto bilance po županijama.
- Twin-line Zagreb vs prsten.

## Zamke

- Selidba sjedišta nije selidba proizvodnje — brass-plate selidba nosi poslove samo na papiru → employment-weighted serija je poštena, a proza kaže "sjedišta", nikad "poslovi", osim gdje je zaposlenost dokazano preselila.
- Akvizicije i preoblikovanja mogu izgledati kao selidbe; obrana je 2-godišnje pravilo + registarski audit uzorka; rezidualna greška se navodi.
- `countyid` odražava adresu predaje, može kasniti godinu za stvarnom selidbom.
- Post mjeri preregistraciju sjedišta — administrativni objekt sa stvarnim fiskalnim posljedicama (prirez, osnovica) — i tako se uokviruje.

## Logged form (idea playbook)

- **Hook.** Sjedišta se sele. Zagreb gubi firme, ali ne onome kome mislite.
- **Finding.** Najveći koridor Zagreb → prsten; Grad plauzibilno neto gubitnik prema vlastitim predgrađima, bruto atraktor iz ostatka zemlje.
- **Data.** Pouzdani stupci od kraja do kraja; registar samo kao validacijski uzorak.
- **Angle.** [KUT] Svi se svađaju oko stoka zagrebačkih firmi; tokovi kažu da centralizacijsku bitku dobiva porezna konkurencija prstena, ne metropola.
- **Effort.** Srednji. Jedan self-join panela + validacijski uzorak.
- **Verdict.** Build now. Udžbenički static-to-flow reframe, nitko nije claimao HQ tokove (zagreb-profit post je stock, drugi objekt), chord-dijagram kao identity hook, imenovana naracija za obrat.
