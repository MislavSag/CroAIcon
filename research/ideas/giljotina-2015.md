# Giljotina iz 2015. Automatski stečaj pobio je desetke tisuća firmi. Jesu li ijedna bile žive?
*The 2015 guillotine. Automatic bankruptcy erased tens of thousands of firms. Were any of them alive?*

**Status.** Brainstorm 2026-07-11, kritičar: **build now** (rang 2/5). Leća: novi izvori podataka (sudreg API). Effort: **srednji**.

## Kuka

Stečajni zakon iz 2015. (automatizam za blokirane preko 120 dana + masovna brisanja) proizveo je val brisanja 2015-2018. Rasprava je ostala moralna i statična: HOK i dio medija tvrdili su da je automatizam "ubio održive male firme", ministarstvo da je počistilo mrtve. Nitko nije napravio obdukciju. Reframe: zakon je mjerljivi event, a panel zna kako je svaka pobijena firma izgledala u zadnjem GFI-ju.

## Očekivani nalaz

Red veličine 20-40 tisuća brisanja u valu 2015-2018, ali ~80-90 % giljotiniranih imalo je nula zaposlenih u zadnjem predanom GFI-ju, uz medijan 3-5 godina šutnje (nepredavanja) prije sječe. Smrti firmi SA zaposlenima nisu se pomaknule. **Headline: udio giljotiniranih bez ijednog zaposlenog pri zadnjem GFI-ju + medijan godina šutnje prije brisanja.** Giljotina je uglavnom odrubila glave leševima — ili, ako vidljiva manjina ima radnike, kritičari dobivaju svoj broj. Presuda u oba smjera.

## Podaci & varijable

- **sudreg open-data API** (`sudreg-data.gov.hr`, besplatan, verificiran srpanj 2026): `subjekti?only_active=0` → `datum_brisanja`, `postupak.datum_stecaja`, šifra načina izlaska, `mbs`, `oib`. Caveat: javni sloj je snapshot trenutnog stanja.
- `db_afs` na zadnjoj predanoj godini svake firme (join preko OIB-a): `employeecounteop` (POUZDAN), `nacerev21` (POUZDAN), `b110` prihod (AUDITIRAN), `b063` kapital (AUDITIRAN), neto rezultat preko COALESCE konstrukcije b184/b185/b197/b198 (AUDITIRAN).
- e-Oglasna XLSX od ~rujna 2015 (vanjski, neauditiran) za razdvajanje skraćenog od klasičnog stečaja.

## Kako izgraditi

1. **Prvi zadatak nakon OAuth registracije:** harvest `subjekti?only_active=0` i dump DISTINCT šifri načina izlaska s brojevima po godini brisanja. Taksonomija je pretpostavljena, ne enumerirana — cijeli legal-route split visi o njoj. Ovo je go/no-go gate.
2. Izolirati spike brisanja 2015-2018. Join na `db_afs` preko OIB-a, MBS fallback za retke bez OIB-a.
3. Za svaku mrtvu firmu: zadnji `reportyear` + `employeecounteop`, `b110`, `b063`, neto rezultat u toj godini.
4. **Audit 0-vs-NULL na `employeecounteop`** na mrtvom poduzorku prije bilo kakve tvrdnje "nula zaposlenih".
5. Jezgra: udio pobijenih s nula zaposlenih; medijan godina od zadnje predaje do brisanja; before/after serija brisanja firmi koje su IMALE zaposlene (diff koji odgovara na HOK-ovu tvrdnju).

## Grafovi

- Event-study linija s okomitim markerom na zakonu 2015. i dvije populacije: prazne ljušture vs firme s radnicima.
- Kompozicijski bar: papirnate vs žive među pobijenima.

## Zamke

- Zaposlenost iz zadnjeg GFI-ja mjerena je 1-5 godina prije brisanja — pošten ali nesavršen proxy za "živa u trenutku smrti"; reći otvoreno.
- Spike miješa 120-dnevni automatizam i odvojeno masovno brisanje nikad pokrenutih firmi → ako šifra ne razdvaja čisto, suziti headline na "val brisanja 2015-18" i pustiti da distribuciju priča godina šutnje.
- Povijest blokada je paid-only → nikad ne tvrditi "120 dana blokade" kao opaženo, samo kao zakonsku rutu.
- Provjeriti potpunost `datum_brisanja` za 2015-2018 u prvom pullu.
- Razgraničenje: parkirana ideja "kroz koja vrata umiru firme" posjeduje dugoročni door-mix; ovaj post posjeduje samo reformski event.

## Logged form (idea playbook)

- **Hook.** Giljotina iz 2015. Jesu li ijedna od pobijenih firmi bile žive?
- **Finding.** ~80-90 % giljotiniranih bez zaposlenih pri zadnjem GFI-ju; smrti firmi s radnicima bez pomaka.
- **Data.** sudreg API (besplatan, verificiran) + pouzdani/auditirani db_afs stupci.
- **Angle.** [KUT] Najnasilnija intervencija države u demografiju firmi bila je egzekucija već mrtvih — a diff na firmama sa zaposlenima presuđuje je li itko živ stradao.
- **Effort.** Srednji. Jedan API harvest + jedan join.
- **Verdict.** Build now. Imenovana, datirana tvrdnja (HOK vs ministarstvo) s presudom u oba smjera; najmanji od sudreg-obitelji kandidata; harvest je ujedno infrastruktura za zombi-studiju.
