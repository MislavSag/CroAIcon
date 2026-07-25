# Plan. Sedmi pad, velika depresija 1929.–1932.

Post `posts/2026-06-hrvatski-rast-dugi-niz/index.qmd` broji šest padova, a vlastiti
niz sadrži i sedmi. Depresija 1929.–1932. u Tici: 1655 → 1364, minus 17,6%,
razina iz 1929. tek 1938. Dublja od Informbiroa koji post broji. Vidljiva na
grafu 3, u tekstu neimenovana. Nalog autora: ugraditi je, proći sve propuste,
ništa ne smije nedostajati.

## Nalazi izvida (podatci)

- Depresija: indeks 15,99 (1929.) → 13,18 (1932.), minus 17,6%. Dvostruko dno
  1935., povratak 1938. Devet godina. Oba ruba pojasa procjena padaju
  (lo 14,15 → 11,67, hi 16,7 → 14,34), smjer robustan preko izvora.
- Informbiro u istim podatcima: 19,41 → 15,99, minus 17,6%. Post kaže minus 16%,
  po vlastitoj konvenciji (letargija se računa iz nezaokruženih) treba minus 18%.
  Ista dubina kao depresija, drugi uzrok. Dar za tezu raznolikosti.
- Manji trzaji ispod praga: 1927. (minus 4,2%), 1935. (minus 4,5%), 1956.
  (minus 4,9%), 1999. (minus 0,5%). Najplići brojeni pad je COVID (minus 7,4%).
  Prag postaje eksplicitan: brojimo padove od oko 7% naviše plus ratne rupe.
- Tipfeleri: "grafuu", dupli razmaci ("Smjer  je", "Dubini  vjerujemo"),
  "blitz+duboka".

## Koraci

1. Workflow provjere (3 agenta, paralelno): literatura o depresiji u
   međuratnoj Jugoslaviji (cjenovna vs. proizvodna kriza, Stajić/Vinski/Maddison),
   revizija svih brojki posta prema `outputs/`, pregled proze prema stilskom vodiču.
2. Nova skripta `scripts/gdp_drawdowns.R` čita `outputs/tables/gdp_long.csv` i
   piše `outputs/tables/gdp_drawdowns.csv` (vrh, dno, dubina, povratak, za sve
   padove). Brojke depresije u postu vuku se odatle. Jedna skripta, jedan posao.
3. `python/gdp_charts.py`. Graf 3 (prewar zoom) dobiva sivu traku 1929.–1932.
   s oznakom *depresija*, naslov i podnaslov se prilagode. Regeneracija grafova.
4. Proza u `index.qmd`. Podnaslov i uvod šest → sedam ("pet kriza"). Naslov
   sekcije "Sedam padova, ni jedan isti". Novi blok depresije između ratova i
   blokade, s mostom prema blokadi (ista dubina, drugi uzrok). Informbiro
   minus 16% → oko minus 18%. Rečenica o trzajima ispod praga. Karta
   pouzdanosti i Napomene dopunjene. Tipfeleri počišćeni.
5. `quarto render` posta, pregled PNG-ova.
6. `/qa-post` na kraju, plus popravci po nalazu.

## Datoteke

- `posts/2026-06-hrvatski-rast-dugi-niz/index.qmd`
- `python/gdp_charts.py`, regenerirani `gdp_*.png`
- nova `scripts/gdp_drawdowns.R`, nova `outputs/tables/gdp_drawdowns.csv`

Status: dovršeno (vidi dnevnik izmjena u sesiji).
