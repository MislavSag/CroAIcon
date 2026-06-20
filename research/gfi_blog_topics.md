# Iza zombija: deset novih blog-tema iz GFI baze

GFI baza (godišnji financijski izvještaji predani FINA-i) već je iznjedrila dvije velike priče bloga — žive mrtvace (solventnost, ICR, perzistencija) i realokaciju zaposlenosti po sektorima. Ali ~2,3 milijuna redaka, jedan po firmi po godini, krije puno više od toga: cijelu anatomiju vlasništva, regija, marži, likvidnosti i demografije poduzeća. Ovdje su teme koje ne diraju ni jednu od prve dvije: tko bere profit, gdje se on knjiži, koliko firma čeka novac, je li inflacija pojela maržu ili plaću, i stari li hrvatsko gospodarstvo jednako brzo kao i njegovi ljudi. Sve počiva isključivo na knjigovodstvenim varijablama GFI-ja — bez tržišnih vrijednosti, carinske statistike ili anketa — uz hrvatsku makro pozadinu koja te brojke čini naslovnima: euro 2023., inflacija 2022.–2024., ovisnost o turizmu, duboko strano vlasništvo, Zagreb-vs-ostatak jaz, tradicija blokade i demografski pad. Svaka tema ispod prošla je kroz adversarijalni stres-test; popravci skeptika ugrađeni su izravno u definicije i caveate.

---

# I. Vlasništvo i regije

*Tko zapravo posjeduje hrvatski profit i gdje se on slijeva. Dvije teme o tome da kapital nije rasut nego koncentriran — po vlasniku i po gradu.*

## 1. Naslov: "Zagreb knjiži profit, ostatak zemlje radi"
*Zagreb Books the Profit, the Rest of the Country Works*

**Kuka.** Svi znaju da je Zagreb najveći. Iznenađenje je KOLIKO je veći u dobiti nego u radu → grad drži ~trećinu radnih mjesta, ali blizu polovice neto dobiti gospodarstva. Profit je centraliziraniji od ljudi, jer se dobit knjiži tamo gdje je sjedište, a ne gdje se radi.

**Hrvatski kut.** Regionalni jaz uvijek se mjeri brojem firmi ili plaćama. Ovdje je kut efekt sjedišta: banke, telekomi i trgovački lanci posluju po cijeloj zemlji, ali dobit knjiže u Zagrebu. Fiskalni i razvojni kapacitet (porez na dobit, reinvestiranje) curi prema centru brže nego sama radna mjesta → oštriji prikaz monocentričnosti od pukog broja firmi.

**Podaci & varijable.** `db_afs`, jedan redak po firmi i godini, `reportyear` 2002.–2024. Geografija: `countyid` → `ref_county` (21 županija, uklj. Grad Zagreb). Po (`countyid`, `reportyear`) zbrojiti: neto dobit = `b183` (i robusnija `b184` samo dobit), zaposlenost = `employeecounteop`, poslovni prihod = `b125`. Udio Zagreba = total_Zagreb / total_RH za svaku mjeru. Indeks koncentracije profita = (udio u dobiti) / (udio u zaposlenosti); > 1 znači da Zagreb knjiži više dobiti po radnom mjestu.

**Izračun & graf.** Dvije linije kroz 2002.–2024.: udio Zagreba u neto dobiti (%) vs udio u zaposlenosti (%). Razmak između linija = vizualni dokaz efekta sjedišta. Blijeda treća linija = udio u poslovnom prihodu (`b125`), koja bi trebala ležati između; ako ne leži, signal je da nešto ne valja s agregacijom. Prikazati dvije varijante: sa i bez NKD K (financije) — banke same nose velik dio koncentracije.

**Težina.** Lako. Caveat: glavnu liniju graditi na `b184` (samo dobit), a `b183` (neto) kao sekundar — udjeli neto dobiti divljaju 2009.–2014. kad su županijski zbrojevi negativni. Prije svega provjeriti pokrivenost `countyid` (udio NULL) i jasno navesti tretman. Efekt sjedišta znači da podaci mjere mjesto KNJIŽENJA, ne mjesto stvaranja vrijednosti → naslov i tekst moraju biti pošteni ("knjiži", ne "stvara").

---

## 2. Naslov: "Četvrtina dobiti, desetina firmi: koliko strani kapital zaradi, a koliko zadrži"
*A Quarter of the Profit, a Tenth of the Firms*

**Kuka.** Strane firme su mala manjina po broju, ali divovi po dobiti → ~10 % firmi, ~18 % zaposlenosti, ali ~25 % neto dobiti (2023.). Pitanje koje nitko ne kvantificira: koliko te dobiti ostane u zemlji kao zadržana dobit, a koliko je potencijalno na putu van kao dividenda?

**Hrvatski kut.** Hrvatska je ekonomija dubokog stranog vlasništva banaka, telekoma i trgovine, sa starom raspravom o odljevu dividendi (osobito bankarskih). Nakon eura 2023. i visokih kamata 2022.–2024. korporativni su profiti rekordni. Ovaj tekst stavlja broj na staru tezu: koliko profita strani sektor generira po radniku, i koliko ga zadržava naspram onoga što teoretski može otići van.

**Podaci & varijable.** `db_afs`, `reportyear` 2008.–2024. (vlasništvo ~100 % popunjeno od 2008.). Vlasništvo: **`foreigncontrol >= 0.5`** (POZOR: polje je udio na skali 0–1, ne 0–100 → `> 50` vraća prazan skup). Neto dobit = `b183` (raspis `b184`/`b185`); zadržana dobit = `b081`; kapital = `b067`; zaposleni = `employeecounteop`; prihod = `b125`. Po godini izračunati udio stranog sektora u: ukupnoj neto dobiti, broju firmi, zaposlenosti, prihodu. Profit po radniku = `b183` / `employeecounteop`. Stopa zadržavanja ≈ Δ`b081` / `b183` (self-join na `subjecttaxnoid`, `reportyear`−1). Realno preko `price_deflator`.

**Izračun & graf.** Tri linije na osi 0–100 % kroz 2008.–2024.: udio stranog sektora u neto dobiti vs u zaposlenosti vs u broju firmi. Glavni vizual = širina razmaka između "udio u dobiti" i "udio u zaposlenosti". Sekundarni rez: udio stranog profita po `nacerev21` (očekivano K financije, J info-telekom, G trgovina).

**Težina.** Srednje. Caveat: GFI NE bilježi isplaćene dividende → "odljev" je nužno POTENCIJAL (neto dobit minus reinvesticija), ne stvarna repatrijacija. `b275`/`b276` su PRIMLJENE dividende, ne isplaćene → ne smiju se prodavati kao odljev. IZBACITI capex-nogu preko `b278` (mrtvo polje, 0 % od 2016.); zadržati samo bilančni proxy preko Δ`b081`, uz oprez na dokapitalizacije.

---

# II. Likvidnost i krhkost

*Hrvatski nacionalni sport: blokada. Tri teme o tome koliko su firme krhke ispod linije profita — koliko gotovine drže, kako se međusobno financiraju, i kome obveze prerastu imovinu a da bilanca ne piše crveno.*

## 3. Naslov: "Koliko dana firma čeka novac, a koliko dana gotovine ima"
*How Many Days a Firm Waits for Money, and How Many Days of Cash It Holds*

**Kuka.** Prosječna firma naplati račun tek za desetke dana, a u banci drži gotovine za tek nekoliko dana poslovanja. Ta dva broja zajedno objašnjavaju zašto se blokada širi kao zaraza: kad jedan platni domino padne, firme s tankim jastukom nemaju čime preživjeti. Otvoreno pitanje: stanjuje li se gotovinski jastuk nakon eura/ECB-a?

**Hrvatski kut.** Blokada je lanac nelikvidnosti gdje neplaćeni račun jedne firme obara sljedeću. Mjerimo dvije poluge krhkosti: koliko firma čeka da naplati (DSO) i koliko dana troškova pokriva samom gotovinom (cash runway). Euro 1.1.2023. + skok ECB stope daju test: kad gotovina počne nositi prinos, drže li firme manje keša i postaju ranjivije?

**Podaci & varijable.** `db_afs` nefinancijske firme, `b125 > 0` i `b131 > 0`, isključ. K. DSO = `b049` / `b125` * 365 (primarno; `b034 + b049` kao osjetljivost — `b034` je dugoročno potraživanje pa unosi šum). Cash runway = `b063` / ((`b131` − `b141`) / 365) — `b141` (amortizacija) je negotovinski pa se obavezno skida iz odljeva. Dani zaliha = `b038` / `b135` * 365; DPO = (`b103` + `b115`) / (`b133` + `b136`) * 365; cash-conversion cycle = DSO + dani zaliha − DPO. Dimenzije: `nacerev21`, `subjectsizeeurev2`, `reportyear`.

**Izračun & graf.** Dvo-osni linijski graf 2008.–2024.: lijevo medijan DSO (dani), desno medijan cash runway (dani), okomita linija na 2023. Robusnost: dodatna linija realnog runwaya (deflacionirani `b063` / realni opex) da inflacija 2022.–24. ne maskira "dobrovoljno" stanjivanje. Sekundarni panel: kvadrant ranjivosti po sektoru (visoki DSO + niski runway = najkrhkiji, vjerojatno F građevina).

**Težina.** Srednje. Caveat: `b063` je stanje na 31.12. → hvata sezonu (turizam drži više keša nakon sezone). Postaviti minimalni prag veličine (npr. `employeecounteop > 0`) povrh winsorizacije 1/99 da medijani ne skaču u tankim ćelijama. Tvrdnja o euru/kamatama je OPISNA, ne kauzalna: dodati panel koji dijeli firme po tome drže li financijsku imovinu koja nosi novi prinos — ako runway pada SVUGDJE jednako, uzrok je inflacija/COVID-normalizacija, ne kamate.

---

## 4. Naslov: "Tko koga financira: lanac trgovačkog kredita kroz gospodarstvo"
*Who Finances Whom: The Trade-Credit Chain*

**Kuka.** Svaka firma koja kupcu pusti da plati za 90 dana de facto mu daje beskamatni zajam. Pitanje koje nitko ne postavlja: koji sektori su neto vjerovnici cijelom ostatku gospodarstva, a koji žive na tuđim leđima? Iznenađenje: najveći neto kreditor često nije banka nego industrija, dok trgovina i građevina (preko javnih naručitelja) sustavno kasne.

**Hrvatski kut.** Trgovački kredit je tihi paralelni bankovni sustav: u bankocentričnoj ekonomiji s tankim tržištem kapitala firme financiraju jedna drugu preko odgode plaćanja. Mjerimo tko subvencionira ostatak gospodarstva, a tko je neto dužnik → strukturna karta financijske ovisnosti koja se ne vidi ni u jednoj službenoj statistici, izravno povezana s tradicijom blokade u građevini.

**Podaci & varijable.** OPREZ — PRIJE svega rekonstruirati stvarno značenje stupaca iz `codes_gfi` (AOP → fizički stupac) i provjeriti nacionalne sume protiv makro sidra (korporativni prihod ~150–200 mlrd EUR, BDP ~70 mlrd), jer dokumentirani b-cheat-sheet ne mapira pouzdano na ovu tablicu. Tek nakon validacije: potraživanja od kupaca ≈ (dugoročna + kratkoročna), obveze prema dobavljačima ≈ (dugoročne + kratkoročne). Neto pozicija = potraživanja − obveze; skalirana na poslovni prihod sektora radi usporedivosti. Kao nazivnik za robusnost koristiti bilančni total (ukupna imovina) prije nego prihod. Sektor: `nacerev21`. Realno: `price_deflator`. Isključ. K.

**Izračun & graf.** Horizontalni divergentni bar (tornado): svaka NKD sekcija = neto trgovačko-kreditna pozicija kao % prihoda sektora, nula u sredini. Desno (zeleno) = neto vjerovnici; lijevo (crveno) = neto dužnici. Istaknuti F građevinu, G trgovinu, C preradu. Ponoviti za 2008. / 2014. / 2024. da se vidi mijenja li se lanac.

**Težina.** Teško. Caveat: NAJVEĆI rizik je da fizički stupci ne nose značenje iz cheat-sheeta → bez validacije protiv `codes_gfi` i makro sidra ideja NIJE izvediva. Restringirati na firme koje su zaista predale prilog (coverage izvijestiti po sektoru), i prikazivati sve kao "unutar firmi koje prijavljuju", nikad kao nacionalni total. Bilanca je stanje na 31.12. (sezona). Lanac je agregatan, ne mrežni (ne vidimo tko kome konkretno duguje).

---

## 5. Naslov: "Kad obveze prerastu imovinu: tiha insolventnost koja ne piše crveno"
*When Liabilities Outgrow Assets: The Hidden Insolvency*

**Kuka.** Standardni test insolventnosti (negativan kapital, `b067 < 0`) u hrvatskim GFI bilancama gotovo NE postoji → obrazac stišće kapital na nulu, pa firma s rupom u kapitalu prijavljuje `b067 = 0`. Pravu sliku daje ekonomski test (obveze > imovina), a on otkriva insolventnost upravo u dobrim godinama, ne u recesiji.

**Hrvatski kut.** Tradicija blokade dobiva novi sloj: kapitalna erozija koja se produbljuje u ekspanziji, koncentrirana oko 2023. (euro + ECB zaoštravanje). Naivni test bi je potpuno promašio → poruka i o tome kako se hrvatske bilance zapravo čitaju.

**Podaci & varijable.** `db_afs`, univerzum OBAVEZNO `b065 > 0` ILI `b123 > 0` (ne samo `b065` — taj je popunjen u samo ~8 % redaka i raste kroz vrijeme, što fabricira lažni trend). Robustan test: rekonstruirati obveze kao `b088 + b095 + b107` i provjeriti taj zbroj > `b065`, na ćeliji gdje `b065 ≈ b123` (tolerancija) da se izbace nekonzistentni reci. Naivni test za usporedbu = `b067 < 0`. Dodatni signal erozije: udio firmi s `b067 = 0`. Sektor `nacerev21`, vlasništvo `foreigncontrol >= 0.5`.

**Izračun & graf.** Glavna linija: udio ekonomski insolventnih (%) po godini 2008.–2024., s tankom drugom linijom za naivni test `b067 < 0` koja leži na nuli (vizualni dokaz da klasični test ne radi), okomita oznaka na 2023. Sekundarni panel: rez po sektoru za 2024. OBAVEZNI panel robusnosti: broj firmi s popunjenom bilancom po godini, da čitatelj vidi da je promjena obuhvata moguć pokretač. Po mogućnosti restringirati na uravnotežen panel firmi prisutnih svake godine.

**Težina.** Teško. Caveat: glavni rizik je nekonzistentnost stupaca — `b123` i `b065` (računovodstveni blizanci, trebali bi biti jednaki) razlikuju se u >99 % redaka i `b123` je 0/NULL za ~četvrtinu firmi, što test čini trivijalno istinitim ako se ne filtrira. Najpouzdaniji headline koji preživljava jest: naivni `b067 < 0` je strukturno mrtav (0 % svake godine, ~94 % bilančnih firmi prijavljuje `b067 = 0`) → hrvatske bilance nikad ne ispisuju crveni kapital jer ga obrazac podiže na nulu. Analiza vrijedi SAMO za firme s popunjenom bilancom.

---

# III. Cijene, marže i euro

*Inflacija 2022.–24. + euro 2023. = prirodni eksperiment. Dvije teme koje obaraju ili potvrđuju "greedflation" tezu: kamo je otišao novac od rasta cijena — u marže ili u plaće?*

## 6. Naslov: "Tko je zaradio na inflaciji? Marže su 2022. PALE"
*Who Profited From Inflation? Margins Fell in 2022*

**Kuka.** Svi su 2022.–23. optuživali firme za pohlepnu inflaciju: cijene rastu, marže debljaju. Hrvatski podaci kažu suprotno → agregatna neto marža velikih firmi pala je s ~6 % (2019.) na ispod 1 % u 2022., na vrhuncu inflacije, pa se oporavila tek 2023. Inflacija je najprije pojela maržu, a nije je napuhala.

**Hrvatski kut.** Hrvatska je ušla u euro 1.1.2023. usred europskog vala inflacije i optužbi za greedflation. Domaći narativ (sindikati, mediji) bio je da su trgovci i ugostitelji dizali cijene više od troškova, uz strah od zaokruživanja na euro. GFI marže daju prvi knjigovodstveni test: ako su firme profitirale na inflaciji, marža bi 2022.–23. trebala skočiti.

**Podaci & varijable.** `db_afs`, full-P&L podskup (`b125 > 0` AND `b127 > 0` → ~7–8 tis. firmi/god, veliki/revidirani obveznici). PRIMARNA metrika = NETO marža = SUM(`b183`)/SUM(`b125`) (agregatni omjer). NE koristiti `b125 − b131` kao "poslovnu maržu": `b131` je nepopunjen za ~90 % podskupa pa daje artefakt (~88 % ravno). Po želji predporezna marža SUM(`b179`)/SUM(`b125`). Za pravi pritisak troškova: udio troška osoblja `b137`/(`b125 − b133 − b136 − b153`). Isključ. K. Sektor `nacerev21`.

**Izračun & graf.** Linija agregatne neto marže (%) 2017.–2023. (2024. preliminarno), okomita oznaka na 1.1.2023. Dolina u 2022. i oporavak u 2023. su poanta. Rez po `nacerev21` za 6–8 najvećih sektora kao NALAZ (ne potvrda): gotovo svi veliki sektori bili su stisnuti 2022., ugostiteljstvo (I) i promet (H) išli su u minus → jači anti-greedflation rezultat od polazne hipoteze.

**Težina.** Srednje. Caveat: detaljni P&L u `db_afs` pokriva samo ~5 % redaka → nalaz vrijedi za segment velikih obveznika, NE cijelo gospodarstvo (jasno reći). Deflator je IRELEVANTAN za marže (omjer je bezdimenzijski; valutu HRK→EUR neutralizira sam omjer) → ne prodavati ga kao "ispravak". Sidrnu "bazu od ~6 %" vezati na prosjek 2017.–2021., ne na jedinu povišenu 2019. godinu. Firm-level prosjek marže je beskoristan (ekstremi) → agregat ili winsorizirani medijan.

---

## 7. Naslov: "Euro je hranio plaće, ne marže"
*The Euro Fed Wages, Not Margins*

**Kuka.** Ako firme nisu zaradile na inflaciji (vidi temu 6), kamo je otišao novac? U plaće. Među velikim poslodavcima udio troška osoblja u prihodu raste, dok marža miruje → suprotno greedflationu, hrvatska inflacija izgleda kao plaćama-vođena, a ne profitno-vođena.

**Hrvatski kut.** Hrvatska se 2022.–24. bori s dvostrukim pritiskom: inflacija nakon eura i akutni manjak radnika zbog iseljavanja (brain drain). Teza: poslodavci su digli plaće da zadrže ljude brže nego cijene, pa je inflacija ušla u troškovni kanal plaća, a marža je amortizirala udar → hrvatski obrat na globalnu raspravu, price-wage spirala umjesto profit-price.

**Podaci & varijable.** `db_afs`, podskup `b138 <> 0` AND `employeecounteop > 0` AND `b125 > 0`, isključ. K. POZOR na valutu: NIKAD ne uspoređivati nominalnu/realnu razinu plaće preko prijeloma 2023. — `b138` je u mješovitim jedinicama/valutama oko HRK→EUR. Pred-euro (2017.–2022., HRK) i post-euro (2023.–24.) tretirati kao odvojene režime, ili 2022. i ranije pretvoriti u EUR po fiksnom 7,53450 PRIJE deflacioniranja. Mjera unutar firme: medijan firminog log-rasta plaće na URAVNOTEŽENOM panelu (ne agregat SUM/SUM, koji vodi kompozicija). Udio troška osoblja = `b137`/`b125` samo na firmama gdje su oba popunjena u uzastopnim godinama, prikazati n po godini.

**Izračun & graf.** Linija unutar-firminog rasta plaće (uravnotežen panel) i udjela troška osoblja u prihodu, indeks bazne godine = 100, odvojeno po režimu valute, s neto maržom kao kontra-linijom. Poanta: plaća/trošak osoblja gore, marža ravna. Po sektoru samo 3–4 najveća (G, C, F, I) jer je n malen.

**Težina.** Teško. Caveat: NAJVEĆI rizik — naivni agregat SUM(`b138`)/SUM(emp) je nemonoton i kompozicijski; na uravnoteženom panelu nominalna plaća čak PADA 2023. zbog HRK→EUR prijeloma. Zato isključivo unutar-firmin rast u jednoj valuti. `b137` ima tanak i prelomljen obuhvat (~3 tis. firmi nakon 2015.) → restringirati i izvijestiti n. Obavezan audit jedinica `b138` protiv `employeecounteop` na ručno provjerenom poduzorku prije ijedne tvrdnje o razini. Podskup su veliki poslodavci, NE tržište rada; nije zamjena za DZS prosjek.

---

# IV. Dinamika, koncentracija i kapital

*Oblik gospodarstva, ne njegova razina. Tri teme: koliko je profit koncentriraniji od prihoda, stari li populacija firmi, i gradi li Hrvatska zidove umjesto ideja.*

## 8. Naslov: "Tisuću firmi nosi naciju: dobit je koncentriranija od prihoda"
*A Thousand Firms Carry the Nation*

**Kuka.** Svi znaju da je prihod koncentriran. Iznenađenje je koliko je dobit KONCENTRIRANIJA od prihoda → šačica divova kupi gotovo cijeli profit nacije, dok ostatak gospodarstva kolektivno jedva izlazi na nulu.

**Hrvatski kut.** Hrvatski rast sve više počiva na nekolicini velikih igrača (banke u stranom vlasništvu, energetika, lanci, turistički divovi), dok je dno populacije krhko i sklono blokadi. Ako vrh kupi gotovo svu dobit, porezna baza, investicijski kapacitet i otpornost na šok koncentrirani su u nekoliko stotina firmi.

**Podaci & varijable.** `db_afs`, nefinancijske firme (isključ. K), `b125 > 0`, 2002.–2024. Prihod = `b125`; neto rezultat = `b183`. Po godini rangirati firme posebno po `b125` i po `b183`. Udio top-1 % = SUM(`b125` vrhnjih 1 %)/SUM(svih `b125`); isto za pozitivnu dobit (SUM `b183` gdje `b183 > 0`). FIKSIRATI univerzum eksplicitno: "aktivna firma" = `b125 > 0`, i računati udjele NAD aktivnim skupom, ne nad svim predanim GFI obrascima. Realno: `b183`/`price_deflator`, `b125`/`price_deflator`.

**Izračun & graf.** Dvije linije kroz 2002.–2024.: udio top-1 % u ukupnom prihodu (`b125`) vs udio top-1 % u ukupnoj pozitivnoj dobiti (`b183`). Razmak između linija JE priča. Anotacija na 2023. (euro), siva traka 2022.–24. (inflacija/marže). Robusnost: prikazati udio i kao FIKSNI broj firmi (top-500/top-1000) uz postotnu definiciju — ako obje serije daju isti trend, headline je čvrst; ako se razilaze, signal je artefakta obuhvata.

**Težina.** Srednje. Caveat: vrlo male/neaktivne firme napuhuju brojnik firmi pa top-1 % mijenja prag ovisno o definiciji univerzuma → fiksirati i navesti. Profitni bazen je osjetljiv na jednokratne revalorizacije pojedinih divova → prikazati i s isključenih top-3 ekstrema ili 3-godišnji medijan. Banke/osiguranja izbaciti (K).

---

## 9. Naslov: "Hrvatsko gospodarstvo stari: sve manje mladih firmi"
*Croatia Inc. Is Getting Old*

**Kuka.** Gospodarstvo se mjeri rastom, ali starenje se krije u dobnoj strukturi firmi. Prosječna firma 2002. imala je nekoliko godina; do 2024. zrela je. Iznenađenje: apsolutni broj rođenja je čak na rekordu, ali STOPA ulaska pada, a stare firme odbijaju nestati → gospodarstvo gomila zrele firme.

**Hrvatski kut.** Demografski pad i iseljavanje uvijek se mjere na ljudima. Ovdje se isti fenomen vidi na firmama. Mlade firme nose nesrazmjeran udio neto novih radnih mjesta i produktivnosti, pa pad njihova udjela znači manje dinamizma. Euro 2023. i inflacija trebali su biti test obnove poduzetništva.

**Podaci & varijable.** Dob = `reportyear` − `godina_osnivanja`, spojem `subjekti_26012026` na `oib = db_afs.subjecttaxnoid` (~90 % pokriveno). KORISTITI ISKLJUČIVO `godina_osnivanja` kao mjeru rođenja (ne "prvu pojavu u `db_afs`", koja je kontaminirana širenjem obuhvata baze). Dobne košare: 0–2, 3–5, 6–10, 11–20, 20+. Po godini: prosjek/medijan dobi i udio firmi po košari. Ponder zaposlenima = `employeecounteop` (sekundarno). Bez deflatora i financijskih stupaca → robusno na HRK→EUR.

**Izračun & graf.** Stacked area udjela firmi po dobnim košarama 2002.–2024., tanka linija prosječne dobi na desnoj osi. Vidi se kako se tanji donji (mladi) sloj. Dodati neovisnu seriju: broj NOVIH firmi po godini (`godina_osnivanja == reportyear`) kao korroboracija koja ne ovisi o preživjeloj zalihi. Rezovi: po `nacerev21` (mladi J/M vs zreli C/G), Zagreb vs ostatak.

**Težina.** Srednje. Caveat: `godina_osnivanja` je snapshot registra iz siječnja 2026. → firme rođene i ugašene davno su ISČIŠĆENE (survivorship bias), pa su pred-2010 udjeli mladih nizvodno pristrani; voditi trend od ~2012. `godina_osnivanja` nedostaje za ~10 % → izvijestiti coverage. Datum osnivanja ≠ ekonomski početak (preuzimanja, reaktivacije).

---

## 10. Naslov: "Hrvatska gradi zidove, ne ideje: nematerijalni kapital je ekstremno koncentriran"
*Croatia Builds Walls, Not Ideas*

**Kuka.** Globalna ekonomija prešla je na nematerijalni kapital (softver, patenti, baze, brendovi), ali hrvatska bilanca je i dalje beton i strojevi. Pravi headline nije "udio je nizak i ravan" (nije — makro udio raste do ~6,7 % 2024.), nego: ~59 % operativnih firmi prijavljuje NULA nematerijalne imovine, a top-20 firmi drži ~70 % svega → nematerijalni kapital je ekstremno koncentriran, većina firmi ga nema.

**Hrvatski kut.** Naslanja se na hrvatski model rasta: ovisnost o turizmu, građevini i fizičkoj imovini, uz kronično nisko ulaganje u znanje. Ako nematerijalni kapital drži šačica divova i u doba EU fondova i digitalne tranzicije, to objašnjava zašto produktivnost stagnira i zašto talent odlazi tamo gdje se plaća znanje, a ne zidovi.

**Podaci & varijable.** `db_afs`, operativne firme (`b125 > 0`), isključ. K, 2008.–2024. Nematerijalna imovina = `b003` (ukupno); dugotrajna imovina (nazivnik) = `b002`. Udio = `b003`/`b002`. NE crtati medijan po firmi (degeneriran na 0 %, jer ~59 % firmi ima nulu). Umjesto toga: (1) % firmi s ne-nul `b003` (~37–40 %, blago raste); (2) koncentracija = udio top-20 firmi u ukupnom `b003`, ili p75/p90 udjela. Makro udio = SUM(`b003`)/SUM(`b002`), OBAVEZNO popraćen serijom sa i bez top-N firmi. Eksplicitno: `b003` ≠ `b004 + b005 + b006` (razlika su predujmovi).

**Izračun & graf.** Glavni graf: dvije linije 2008.–2024. — makro udio nematerijalne imovine (SUM `b003`/SUM `b002`) i ista serija BEZ top-20 firmi; razmak pokazuje koliko je riječ o nekoliko divova. Sekundarni bar: udio nematerijalnog po `nacerev21` za 2024. (J informacije i M stručne vode; F građevina, I turizam, G trgovina zaostaju).

**Težina.** Srednje. Caveat: namjenska polja za tok ulaganja (`b278` capex, `b282` R&D, `b285` zeleno) PRAKTIČKI SU MRTVA (`b278` ne-nul <1,1 % firmi, 0 % od 2016.) → oslanjamo se na STANJE bilance (`b002`, `b003`), pokriveno ~87–89 % kod operativnih firmi. Nematerijalna imovina je podcijenjena u računovodstvu (interni brend/znanje se ne kapitalizira) → razina je donja granica, ali usporedivost kroz godine vrijedi. Udjeli su omjeri pa je HRK→EUR prijelom neutralan (prednost).

---

# Zajednička metoda

Većina ovih tema dijeli isti, ponovljiv cjevovod:

- **Univerzum:** `db_afs`, jedan redak po firmi po godini, nefinancijske firme (isključiti `nacerev21 = 'K'`; po potrebi i L, D, O). Definirati "aktivnu firmu" eksplicitno (`b125 > 0` i/ili popunjena bilanca) i navesti definiciju.
- **Vlasništvo:** `foreigncontrol >= 0.5` (skala 0–1, NIKAD `> 50`). Isto za `domesticcontrol`.
- **Realne vrijednosti:** dijeliti nominalne iznose s `price_deflator` po retku; PAZITI da je `price_deflator` NULL za 2024. (realne serije završiti 2023.). Omjeri (marže, udjeli) bezdimenzijski su → neutralni na HRK→EUR prijelom, pa za njih deflator nije potreban.
- **Ekstremi:** winsorizirati firm-level omjere na 1./99. percentilu; preferirati agregat SUM/SUM ili medijan nad prosjekom omjera; postaviti minimalni prag veličine u tankim ćelijama.
- **Coverage je obavezan dio teksta, ne fusnota:** za svako annex polje (`b231`–`b287`) i za rijetke detaljne bilance (`b065`) izvijestiti udio firmi i udio prihoda s ne-nul vrijednošću po godini PRIJE svake tvrdnje. Mrtva polja (`b278`, `b252`, `b259`–`b261`, `b273` od 2016., `b243`) ne koristiti kao nosioce nalaza.
- **Validacija stupaca:** gdje cheat-sheet sumnjivo mapira (trgovački kredit, bilančni identiteti), rekonstruirati značenje iz `codes_gfi` i provjeriti nacionalne sume protiv makro sidra prije analize.

## Brza ljestvica

| Naslov | Težina | Zašto vrijedi |
|---|---|---|
| 1. Zagreb knjiži profit, ostatak radi | Lako | Efekt sjedišta u jednoj slici → profit centraliziraniji od ljudi |
| 2. Četvrtina dobiti, desetina firmi | Srednje | Stavlja broj na FDI-odljev tezu; ~25 % dobiti, ~10 % firmi |
| 3. Koliko dana firma čeka novac | Srednje | Anatomija blokade kroz DSO + cash runway, euro-test |
| 4. Tko koga financira (trgovački kredit) | Teško | Nova os: paralelno bankarstvo među firmama, tornado-karta |
| 5. Kad obveze prerastu imovinu | Teško | Metodološki twist: naivni test mrtav, prava insolventnost raste u boomu |
| 6. Tko je zaradio na inflaciji | Srednje | Obara greedflation: marže su 2022. PALE, ne narasle |
| 7. Euro je hranio plaće, ne marže | Teško | Suprotna strana inflacije: price-wage spirala + brain drain |
| 8. Tisuću firmi nosi naciju | Srednje | Dobit dramatično koncentriranija od prihoda, čist headline |
| 9. Hrvatsko gospodarstvo stari | Srednje | Demografija firmi = demografija ljudi, stopa ulaska pada |
| 10. Hrvatska gradi zidove, ne ideje | Srednje | Nematerijalni kapital ekstremno koncentriran, većina firmi ga nema |
