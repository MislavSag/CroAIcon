# Hrvatski zombiji: pet blog-tema iz GFI baze

Hrvatska je gotovo savršen prirodni laboratorij za proučavanje zombi-firmi. Imala je jednu od najduljih recesija u EU (šest godina kontrakcije, 2009.–2014.), kreditni boom-bust u građevini i nekretninama oko 2008., korporativne NPL-ove koji su dosegli ~30 %, te bankovni sustav koji je ~90 % u stranom vlasništvu i dobro kapitaliziran — što mijenja kanal evergreeninga u odnosu na "slabe banke". Na to se nadovezuju COVID-jamstva (HAMAG-BICRO, HBOR) i moratoriji, uvođenje eura 1. siječnja 2023. i ECB-ovo zaoštravanje 2022.–2023. kao oštar test "kraja jeftinog novca". Sve teme ispod oslanjaju se isključivo na knjigovodstvene varijable koje GFI baza ima (EBIT, EBITDA, kamatni rashod, dug, kapital, prihodi, dob, sektor, vlasništvo) — bez tržišnih vrijednosti, plaćene kamatne stope ili mreža povezanih društava.

---

## 1. Naslov: "Izgubljeno polu-desetljeće" — kako je duga recesija uzgojila zombije
*The Lost Half-Decade: How Croatia's Six-Year Recession Bred Its Zombies*

**Kuka.** Niske kamate i slab "cleansing effect" u dugim recesijama klasično su leglo zombija (Banerjee-Hofmann, BIS 2018; Adalet McGowan i dr., OECD 2017). Pitanje: je li udio hrvatskih zombi-firmi rastao kroz šest godina kontrakcije i ostao povišen i nakon oporavka 2015.?

**Hrvatski kut.** Hrvatska je imala 5.–6. uzastopnu godinu pada BDP-a do 2013. (IMF 2014 Article IV: "unusually drawn out recession"), nezaposlenost ~17 %, korporativne NPL-ove ~27–30 %. Ako recesija nije "očistila" neodržive firme, udio zombija trebao bi rasti upravo u tom razdoblju.

**Podaci & varijable.** `vw_db_afs_financial_subject_year` + raw `db_afs` (`reportyear` 2008–2024). ICR = (`b125` − `b131`) / (`b166` + `b168`); dob preko spoja na `subjekti_26012026.godina_osnivanja` (OIB = `subjecttaxnoid`). **Definicija: OECD/ICR** — dob ≥ 10 i ICR < 1 tri uzastopne godine.

**Izračun & graf.** Jedna linija: udio zombi-firmi (% svih nefinancijskih firmi) po godini, 2008.–2024. Preklopiti sivu pozadinsku traku za recesijske godine 2009.–2014. X-os = godina, Y-os = % zombija. Priča: vrhunac u recesiji, sporo splašnjavanje.

**Težina.** Srednje. Caveat: 3-godišnji uvjet ICR-a "pojede" prve godine uzorka; dob je *partial* (neki OIB-ovi bez godine osnivanja → izvijestiti coverage).

---

## 2. Naslov: Zombiji ne umiru tiho — sektorska karta građevine, turizma i nekretnina
*Zombies Don't Die Quietly: A Sectoral Map of Construction, Tourism and Real Estate*

**Kuka.** Zombiji se globalno gnijezde u netrgovinskim sektorima — nekretnine, ugostiteljstvo, građevina (Albuquerque-Iyer, IMF 2023; ESRB WP143). Pitanje: nose li upravo ti sektori nesrazmjeran teret hrvatskih zombija?

**Hrvatski kut.** Kičma hrvatskog gospodarstva je točno tamo gdje zombiji klasteriraju: turizam (direktno ~11 % BDP-a, ~24,5 % sa povezanim djelatnostima) i građevina/nekretnine koje su prošle kreditni boom-bust oko 2008. To je strukturni, a ne ciklički "porez na produktivnost".

**Podaci & varijable.** `db_afs` sektor preko `nacerev21` (slovo sekcije) ili `nkd2007` + `codes_nkd2007` za nazive. **Definicija: ESRB WP143** (ne treba pretpostavku o kamatnoj stopi): negativan ROA (`b183`/`b065`) + negativan net investment (Δ`b002`) + EBITDA/dug < 5 % (((`b125`−`b131`)+`b141`) / (`b100`+`b101`+`b112`+`b113`)), ≥ 2 godine.

**Izračun & graf.** Horizontalni bar-chart: udio zombi-firmi (%) po NKD sekciji za najnoviju potpunu godinu (2024.), sortirano silazno; istaknuti F (građevina), I (smještaj/ugostiteljstvo), L (nekretnine). Opcionalno: udio ponderiran zaposlenima (`employeecounteop`) kao druga traka.

**Težina.** Lako. Caveat: Δ`b002` traži self-join na prethodnu godinu; izbaciti financije (K) i komunalije.

---

## 3. Naslov: Kraj jeftinog novca — euro i ECB-ove kamate kao test za žive mrtvace
*The End of Cheap Money: The Euro and ECB Hikes as a Zombie Stress Test*

**Kuka.** Niske kamate su omogućavale zombije; zaoštravanje bi ih trebalo natjerati na izlazak, osim ako ih nebankovni kreditori održe (Albuquerque, IMF 2023/192). Pitanje: je li nakon 2022. udio zombija pao — ili su firme s ICR < 1 i dalje "žive"?

**Hrvatski kut.** Hrvatska je uvela euro 1. siječnja 2023. točno dok je ECB dizao depozitnu stopu s −0,5 % na 4,0 % (do rujna 2023.). Budući da je hrvatski kredit bankocentričan i nebankovni sektor tanak, zaoštravanje bi trebalo "ugristi" jače i brže nego u dubljim financijskim sustavima — čist prirodni eksperiment s oštrim prijelomom 1.1.2023.

**Podaci & varijable.** `db_afs` `reportyear` 2019–2024. ICR = (`b125`−`b131`)/(`b166`+`b168`); kamatni rashod (`b166`+`b168`) kao zasebna linija. **Definicija: OECD/ICR** (ili samo "ICR < 1" za udio firmi koje ne pokrivaju kamate). `price_deflator` po retku za realne iznose.

**Izračun & graf.** Linija: udio firmi s ICR < 1 (%) po godini 2019.–2024., s okomitom linijom na 2023. (euro/hikes). Druga linija na istom grafu: agregatni kamatni rashod kao % EBIT-a. Priča: rastu li kamate bržе nego što firme mogu pokriti?

**Težina.** Srednje. Caveat: efekt fiksacije kamata znači blag/odgođen prijenos (IMF 2023 Article IV) → komentirati da 2024. možda još ne pokazuje pun udar.

---

## 4. Naslov: Koliko smo zombija slučajno spasili u COVID-u? Hibernacija ili zombifikacija
*How Many Zombies Did COVID Accidentally Save? Hibernation vs. Zombification*

**Kuka.** Francuska je zaključila "hibernacija, ne zombifikacija" — potpora je sačuvala održive firme jer su najjači prediktori propasti ostali niska produktivnost i visok dug, ne COVID-izloženost (Cros-Epaulard-Martin 2020; ECB FSR 2021: korist zombijima "skromna"). Pitanje: vrijedi li to i za turistički koncentriranu Hrvatsku?

**Hrvatski kut.** Hrvatska je 2020. pala ~8 % uz ~25 % ovisnosti o turizmu i potrošila ~5,5 % BDP-a na potpore (HZZ: 7,7 mlrd HRK, 697.126 radnika) plus moratorije i HBOR/HAMAG-BICRO jamstva. Test: je li udio zombija skočio 2020.–2021. pa se vratio (hibernacija) ili ostao trajno povišen (zombifikacija)?

**Podaci & varijable.** `vw_db_afs_financial_subject_year` 2018.–2024. **Definicija: ESRB WP143** (robusna, bez pretpostavke o kamati) ili **IMF multi-indikator** (ICR < 1 + leverage iznad sektorskog mediana + negativan realni rast prodaje). Realni rast prodaje: `b125` / `price_deflator`, self-join na `reportyear`−1.

**Izračun & graf.** Linija udjela zombija 2018.–2024., s istaknutim COVID-prozorom 2020.–2021.; idealno dvije linije — turizam/ugostiteljstvo (NKD I) vs. ostatak gospodarstva. Priča: skok i povratak (V) = hibernacija; trajni plato = zombifikacija.

**Težina.** Srednje. Caveat: bez flagova primatelja potpore u GFI-u test je *indirektan* (vremenski, ne tretmanski) — to jasno reći; perzistencija od ~4 god. znači da COVID-kohorta još "hoda" 2024.

---

## 5. Naslov: Koji ravnalo koristiti? Isti uzorak, pet definicija zombija
*Which Ruler? The Same Firms Under Five Zombie Definitions*

**Kuka.** Koliko firmi je "zombi" ovisi isključivo o tome koga pitate; izbor definicije nije neutralan (CEPR/VoxEU; ESRB WP143). Pitanje: koliko se headline-brojka mijenja za isti hrvatski uzorak ovisno o definiciji?

**Hrvatski kut.** Slavni Tobin's-Q test (Banerjee-Hofmann) beskoristan je u Hrvatskoj jer su firme praktički sve neuvrštene — pa za privatnu, FX-zaduženu ekonomiju treba pravo ravnalo. Ovo je metodološki temelj za sve ostale tekstove i izravan dodatak Berisi (2023) i Martinis-Ljubaj (2017), koji nisu radili modernu multi-definicijsku prebrojavu.

**Podaci & varijable.** `db_afs` jedna godina (npr. 2023.). Izračunati paralelno: ICR (`b125`−`b131`)/(`b166`+`b168`); EBITDA/dug; ROA (`b183`/`b065`); net investment (Δ`b002`); Z''-score komponente (WC=`b037`−`b107`, RE=`b081`, EBIT, knjig. kapital `b067`, ukupne obveze `b123`−`b067`). **Definicije: OECD/ICR, ESRB WP143, IMF multi-indikator, De Jonghe EBITDA, Altman Z''.**

**Izračun & graf.** Bar-chart: udio firmi klasificiranih kao zombi (%) pod svakom od 5 definicija za istu godinu, plus mali Venn/overlap-broj (koliko ih je zombi pod ≥ 3 definicije). X-os = definicija, Y-os = % zombija. Priča: ista populacija, brojka se njiše.

**Težina.** Lako–Srednje. Caveat: Z'' bez tržišne vrijednosti → koristiti samo knjigovodstveni `b067` (već to brief traži); uskladiti uvjet perzistencije među definicijama radi poštene usporedbe.

---

## Zajednička metoda (jedan pipeline za svih pet tekstova)

Jedan ponovno iskoristiv "zombie-flag" cjevovod, mapiran na GFI polja:

1. **Univerzum.** `db_afs` / `vw_db_afs_financial_subject_year`, sve nefinancijske firme. **Izbaciti** financije i osiguranje (NKD K) i komunalije/energetiku (NKD D/E) jer im kapitalna struktura iskrivljuje ICR/leverage; izbaciti firme s prihodom = 0 i bez zaposlenih.
2. **Jezgrene varijable (jedan red).** EBIT = `b125`−`b131`; kamatni rashod = `b166`+`b168`; EBITDA = (`b125`−`b131`)+`b141`; financijski dug = `b100`+`b101`+`b112`+`b113`; ukupne obveze = `b123`−`b067`; ukupna imovina = `b065`; kapital = `b067`; ROA = `b183`/`b065`; prihodi = `b125`.
3. **Lag varijable (self-join na `subjecttaxnoid`, `reportyear`−1).** Realni rast prodaje (`b125`/`price_deflator`), net investment (Δ`b002`).
4. **Dob.** Spoj na `subjekti_26012026` (OIB = `subjecttaxnoid`); `age = reportyear − godina_osnivanja`. Izvijestiti coverage (partial).
5. **Perzistencija.** Primijeniti pravilo definicije (OECD: 3 uzastopne god.; IMF/ESRB: ≥ 2 god. + 2-god. ulaz/izlaz) preko window funkcije po firmi.
6. **Čišćenje.** Winsorizirati ICR, leverage i EBITDA/dug na 1./99. percentilu; ICR tretirati kao nedefiniran kad je dug/kamata ≈ 0. Sve realne iznose deflacionirati kroz `price_deflator` (po retku) zbog HRK→EUR prijeloma 2023.
7. **Dimenzije za rez.** Sektor (`nacerev21`/`nkd2007` + `codes_nkd2007`), županija (`countyid` + `codes_municipal`), vlasništvo (`foreigncontrol` > 50), veličina (`subjectsizeeurev2`), zaposleni (`employeecounteop`).

Default definicija za "brzi" tekst: **ESRB WP143** (ne treba kamatnu stopu, robusna na FX-dug). Default za "klasični" headline: **OECD/ICR**. Oba se vade iz istih devet jezgrenih varijabli gore.