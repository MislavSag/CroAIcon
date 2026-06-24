# Subvencije ulaze, rezultati ne izlaze -> Jaz između priljeva potpora i poslovnih pokazatelja u agrobiznisu sve je veći

*Bilješka za budući post. Sve konkretne brojke su vanjske, za provjeru, nisu naš nalaz. Tema čeka čišćenje financijskih stupaca GFI baze.*

[Otvaranje. Novac ulazi, rast ne izlazi. Subvencije teku u poljoprivredu i preradu hrane već cijelo desetljeće, a poslovni pokazatelji se ne mrdaju za njima. Pogledajmo razmak između priljeva potpora i onoga što firme zapravo pokazuju u bilanci.]

## Subvencija je sve veći dio prihoda, a ne sve manji

[Caption grafa. Udio prihoda od subvencija u ukupnom prihodu, NKD 01 / 10 / 11, prije i poslije ulaska u EU (2013.).]

[Stub proze. Brojka bi vodila. [Očekujemo da udio subvencija u ukupnom prihodu raste nakon 2013. umjesto da pada, što bi značilo da potpora ne pokreće tržišni prihod nego ga zamjenjuje.] Pisati strelicom kad brojka bude izračunata: udio (prije EU) -> udio (zadnja godina).]

[KUT] Je li potpora poluga koja podiže tržišni prihod ili jastuk koji ga zamjenjuje.

## Imovina veže kapital, prinos ostaje nizak

[Caption grafa. ROA i intenzitet dugotrajne imovine (zemljište, oprema) prema prihodu, po djelatnostima.]

[Stub proze. [Očekujemo nizak ROA u NKD 01 uz visok intenzitet dugotrajne imovine (zemljište, oprema vežu kapital), nešto bolji ROA u preradi hrane (10) i pićima (11).] Dodati obrtni kapital vezan u sezonske zalihe kao treći pokazatelj. Sve traži financijske stupce -> danas nepouzdano.]

[KUT] Sektor koji drži puno imovine a vraća malo prinosa ovisi o tome tko pokriva razliku.

## Bliže potrošaču znači viši prinos, primarna proizvodnja zaostaje

[Samo ako tema ponudi pobjednike i gubitnike kad brojke budu izračunate. Podjela ide po djelatnosti, ne po pojedinoj firmi.]

Dobitnici. [Očekivano, prerada hrane (10) i pića (11) -> bliže potrošaču, viši ROA, manje vezane imovine.]

Gubitnici. [Očekivano, primarna poljoprivreda (01) -> visoka poluga, niska marža, najveća ovisnost o subvenciji.]

[KUT - glavna interpretacija] Ako potpora godinama raste a poslovni pokazatelji stoje, pitanje nije koliko novca ulazi nego pretvara li se taj novac u održiv posao ili samo u održavanje statusa quo.

[Payoff. Stub za so-what. [Održivost agrobiznisa ne mjeri se priljevom potpora nego time što ostane kad se potpora oduzme. Ovaj post traži tu razliku u bilanci, ne u proračunu.] Ne sažetak.]

## Napomene

- Izvor. FINA, Godišnji financijski izvještaji (`db_afs`) plus dopunski izvor za kontekst subvencija (DZS, APPRRR / EU isplate).
- Tablica. `db_afs`
- Stupci / omjeri. Prihod od subvencija / ukupan prihod, ROA (dobit / imovina), obrtni kapital vezan u sezonske zalihe, intenzitet dugotrajne imovine (zemljište plus oprema) / prihod, poluga (dug / imovina). Razrez po NKD 01 (poljoprivreda), 10 (prerada hrane), 11 (pića).
- Oprez. Svi navedeni omjeri počivaju na financijskim stupcima GFI baze koji još nisu pročišćeni (mapiranje bNNN != FINA AOP je nepouzdano). Gdje tema dira broj firmi u djelatnosti, širi obuhvat baze nije stvarni rast.

---

## Bilješke za izradu

- Nalaz (očekivani). Ako bi se omjeri izračunali, očekivali bismo da udio subvencija u prihodu raste a ROA u primarnoj poljoprivredi (01) ostaje nizak nakon ulaska u EU, dok prerada hrane (10) i pića (11) stoje bolje. Sve u kondicionalu dok stupci nisu pročišćeni.
- Podaci. `db_afs`. Omjeri: subvencija / ukupan prihod, ROA, obrtni kapital u sezonskim zalihama, dugotrajna imovina / prihod, poluga. Svi traže financijske stupce -> danas NEPOUZDANO.
- Kut. Pretvara li priljev potpora agrobiznis u održiv posao ili samo financira opstanak.
- Vanjske brojke za provjeru. Za provjeru, ne naš nalaz, iz medija. Poljoprivreda plus 0,4% godišnje (prvih 9 mj. 2024.), oko 8x sporije od gospodarstva (Index.hr / Jutarnji list). Realni poljoprivredni dohodak minus 6,3% u 2024. na 1,6 mlrd EUR (DZS, prema medijima). Trgovinski deficit hrane i živih životinja narastao na 2,2 mlrd EUR. EU subvencije 8,3 mlrd EUR u razdoblju 2013. -> 2025. Sve provjeriti uz primarni izvor prije bilo kakve upotrebe.
- Mediji / izvori. Mediji: Index.hr, Jutarnji list, HUP. Institucije / izvori: FINA, DZS (plus APPRRR / EU isplate za kontekst subvencija).
- Težina. Velika. Tema počiva na nepročišćenim financijskim stupcima i na povezivanju više omjera kroz tri NKD razreda i dva razdoblja.
- Verdikt. Park - čeka čišćenje financijskih stupaca GFI baze.
