# Plaće rastu brže od učinka -> Jedinični trošak rada raste, a marže firmi se stišću prvo u ugostiteljstvu i trgovini

*Bilješka za budući post. Sve brojke su za provjeru, nisu naš nalaz. Tema čeka čišćenje financijskih stupaca GFI baze.*

[Otvaranje. Opener. Plaća raste, ali raste li i ono što radnik proizvede. Bridge, hortativ. Pogledajmo gdje se rast mase plaća sudara s maržom, sektor po sektoru, kroz omjer troška osoblja i prihoda. Obećanje. Pokazujemo tko apsorbira skok plaća, a tko ga prelijeva u cijenu ili u izgubljenu maržu.]

## Trošak rada raste brže od onog što firma proizvede

[Caption grafa. Prihod po zaposlenom naspram troška osoblja po zaposlenom, indeks, po godini.]

[Stub proze. Brojka bi vodila. Jedinični trošak rada je trošak rada na jedinicu učinka. [Očekujemo da je trošak osoblja po zaposlenom rastao brže od prihoda po zaposlenom, pa da omjer trošak osoblja / prihodi raste.] Magnitudu upisujemo tek nakon izračuna iz baze, ne iz medija.]

[KUT] Je li ovo pad konkurentnosti ili samo dohvaćanje plaća koje su predugo kasnile.

## Maržu prvi gube radno intenzivni sektori

[Caption grafa. Promjena operativne marže naspram promjene mase plaća, po djelatnosti.]

[Stub proze. Gdje plaća čini velik dio troška, skok plaća se najbrže vidi u marži. [Očekujemo da ugostiteljstvo i trgovina, kao radno intenzivni, pokazuju jaču vezu rasta mase plaća i pada operativne marže nego kapitalno intenzivna industrija.] Brojku, koeficijent te veze, upisujemo nakon izračuna.]

[KUT] Je li stiskanje marže znak da je prostor za apsorpciju plaća iz dobrih godina potrošen.

## Tko je apsorbirao skok plaća, a tko ga prelio dalje

Dobitnici. [Sektori koji su rast plaća pokrili rastom produktivnosti ili cijena, marža im se drži. Popuniti iz baze.]

Gubitnici. [Sektori gdje masa plaća raste, a operativna marža pada. Kandidati po hipotezi su ugostiteljstvo i trgovina. Popuniti iz baze.]

[KUT. glavna interpretacija] Skok dobiti iz 2022. i 2023. dao je firmama jastuk za rast plaća. Pitanje za bazu je je li taj jastuk još tu ili se 2025. i 2026. pretvara u stisnutu maržu. To je razdjelnica između privremenog troška i strukturnog pritiska.

[Payoff. Stub za so-what. Ako jedinični trošak rada raste, a marža pada baš ondje gdje plaća čini najveći dio troška, onda rast plaća više nije besplatan za firmu. Pitanje nije raste li plaća, nego tko plaća rast. Zatvoriti tek kad brojke iz baze potvrde smjer.]

## Napomene

- Izvor. FINA, Godišnji financijski izvještaji (`db_afs`), uz DZS za makro kontekst plaća i produktivnosti.
- Tablica. `db_afs`
- Stupci / omjeri. Trošak osoblja, prihodi, bruto i operativna marža, prihod po zaposlenom (`employeecounteop` kao nazivnik), rezerviranja za otpremnine i obveze prema zaposlenima. Veza rasta mase plaća i promjene operativne marže po djelatnosti (`nacerev21`).
- Oprez. Svi financijski stupci traženi za ovu temu još su nepročišćeni. Mapiranje `bNNN` na FINA AOP je nepouzdano, pa nijedan omjer marže ni troška rada još ne stoji kao nalaz. Gdje tema dira broj firmi, širi obuhvat baze nije stvarni rast (više u izračunu kad bude gotov).

---

## Bilješke za izradu

- Nalaz (očekivani). Ako bi se trošak rada po zaposlenom kretao brže od prihoda po zaposlenom, jedinični trošak rada bi rastao, a operativna marža bi se stiskala najjače u radno intenzivnim sektorima (ugostiteljstvo, trgovina). Magnituda u kondicionalu dok je baza ne potvrdi.
- Podaci. `db_afs`. Omjeri trošak osoblja / prihodi, bruto marža, operativna marža, prihod po zaposlenom, rezerviranja za otpremnine i obveze prema zaposlenima. Sektorska regresija rasta mase plaća na promjenu marže po `nacerev21`. Status povjerenja. SVI traže financijske stupce -> danas NEPOUZDANO. Pouzdano je samo `employeecounteop` i `nacerev21`.
- Kut. Je li rast plaća privremeni trošak koji firme apsorbiraju ili strukturni pritisak koji jede maržu.
- Vanjske brojke za provjeru. Realni rast plaća veći od 10% u 2023. (mediji, DZS, za provjeru). Indeks troškova rada Q1 2026. na razini 161 (baza 1995. = 100, za provjeru). EK. rast plaća nadmašuje rast produktivnosti (za provjeru). IMF 2024. Article IV. nakon skoka dobiti 2022. i 2023. firme su imale prostora apsorbirati rast plaća u 2024., ali 2025. i 2026. mogu pokazati novi pritisak (za provjeru). NIJEDNA od ovih brojki ne ulazi u tijelo kao naš nalaz.
- Mediji / izvori. Jutarnji list, Lider, DZS. Institucije. FINA, DZS, uz EK i IMF kao vanjski kontekst.
- Težina. Velika. Tema stoji ili pada na pročišćenim financijskim stupcima i na sektorskoj vezi mase plaća i marže.
- Verdikt. Park - čeka čišćenje financijskih stupaca GFI baze.
