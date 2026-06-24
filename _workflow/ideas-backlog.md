# Ideas backlog

The running memory of post ideas. The brainstorm skill reads this to avoid repeats and to build on what is parked, then appends new candidates. Move an idea between sections as its status changes.

## Buildable

Ideas that cleared the playbook and are ready to draft.

- **Croatia vs the frontier: 130 years of (non-)convergence.** Where Croatia sits
  relative to other countries, USA = 100. Data is ready and machine-readable:
  Tica (2004) Table 16, transcribed in `data/reference/Tica_2004_Croatia_GDP_data.xlsx`,
  sheet `T16_country_USA100_growth` (28 countries; cols idx_1870, idx_1913, idx_1920,
  idx_1939, idx_1950, idx_1987, idx_1993, idx_2000, plus period growth rates).
  Headline nugget for Croatia (USA=100): **25 (1870) → 24 (2000)** — a century and a
  half of real growth (~1.86%/yr) but essentially the *same relative position*. The
  arc inside that: socialist catch-up **19 (1950) → 38 (1987)**, then the 1990s collapse
  wipes it out (**38 → 20 by 1993**), back to ~24 by 2000. This is the comparison the
  long-run GDP post (`posts/2026-06-hrvatski-rast-dugi-niz`) deliberately could NOT make
  from its single-country splice — a natural follow-up. Extend/cross-check the modern
  end with Maddison 2023 or PWT 10.01 (both already wired in via `R/get_maddison.R`,
  `R/get_pwt.R`). Angle: growth happened, convergence didn't.

## Parked

Good ideas waiting on data, on a cleaner column, or on the right moment.

- Anything resting on financial columns (revenue, profit, debt). Waiting on the GFI financial cleanup.
- **Financije na razini firme. deset tema iz medija, sve Park dok GFI financijski stupci nisu pročišćeni.**
  Puni preliminarni nacrti (kostur posta + blok za izradu) u `drafts/balance-sheet/`, mapa u
  `drafts/balance-sheet/00-index.md`. Brojke u nacrtima su medijske, za provjeru, nisu naš nalaz.
  - **Visoka poluga, plitka likvidnost.** Spoj visoke poluge i niske likvidnosti predviđa kasniji stečaj,
    pokriće kamata ispod 1 najjači signal. D/E, tekuća likvidnost, pokriće kamata + ishod. Effort velik.
    → `drafts/balance-sheet/01-zaduzenost-i-likvidnost.md`
  - **Pune sobe, tanke marže.** Trošak osoblja jede hotelsku maržu brže nego što dolasci rastu, laka
    bilanca (najam) izmiče stisku. Trošak osoblja/prihod, iskorištenost imovine. Effort velik.
    → `drafts/balance-sheet/02-turizam-marze-i-troskovi.md`
  - **Cijene rastu na ekranu, bilance se pune u tišini.** Rast cijena sjeda kao zaliha i dug kod
    investitora (NKD 41, 68), ne kao prodaja. Zalihe, potraživanja, hipoteka/imovina. Effort velik.
    → `drafts/balance-sheet/03-nekretnine-investitori.md`
  - **Struja koja jede maržu.** Energetski šok stišće EBITDA maržu izloženih industrija, prijenos troška
    dijeli pobjednike od gubitnika. Energija/OPEX, EBITDA marža (diff-in-diff). Effort velik.
    → `drafts/balance-sheet/04-energija-i-konkurentnost.md`
  - **Plaće rastu brže od učinka.** Jedinični trošak rada raste, marža se stišće prvo u ugostiteljstvu i
    trgovini. Trošak osoblja/prihodi, bruto i operativna marža. Effort velik.
    → `drafts/balance-sheet/05-place-i-marze.md`
  - **Police pune, marže tanke.** Hrvatski lanci po dodanoj vrijednosti i marži zaostaju za
    internacionalnima, sporiji obrtaj zaliha. Obrtaj zaliha, neto marža, ciklus obrtnog kapitala. Effort velik.
    → `drafts/balance-sheet/06-trgovina-marze.md`
  - **Gubitak je proračunska stavka.** Jezgra državnih firmi reže operativni gubitak pokriven transferima,
    teret raste izvan bilance. Operativni gubitak, dokapitalizacije, jamstva. Effort velik.
    → `drafts/balance-sheet/07-drzavne-firme.md`
  - **Subvencije ulaze, rezultati ne izlaze.** Udio subvencija u prihodu raste a ROA stoji, jaz priljeva i
    rezultata u agrobiznisu. Subvencija/prihod, ROA, poluga (NKD 01, 10, 11). Effort velik.
    → `drafts/balance-sheet/08-poljoprivreda-subvencije.md`
  - **Likvidni, a žedni kapitala.** MSP nisu prezaduženi i sjede na gotovini, a financiranje teško stiže
    do onih s pravim ograničenjem. Poluga, capex, gotovina/imovina, ročnost duga. Effort velik.
    → `drafts/balance-sheet/09-msp-financiranje.md`
  - **Bilanca bez tvornice.** ICT firme (NKD 62, 63) nose vrijednost u nematerijalnoj imovini i
    pretplatama, klasični omjeri promaše narav. Nematerijalna imovina, cash burn, odgođeni prihodi. Effort velik.
    → `drafts/balance-sheet/10-ict-i-startupi.md`
- **Yugoslav-era sector growth decomposition** (where the socialist boom came from).
  Data in `data/reference/Tica_2004_Croatia_GDP_data.xlsx`: `T4_YU_GDP_sector_gr_1965_88`
  and `T5_HR_sector_gr_RA_1958_90` (industry, agriculture, construction, trade, hotels,
  utilities... annual growth). Parked pending an angle that isn't just a table dump.

## Published

Shipped posts, so we do not repeat them and can follow up.

- Firms grow, jobs move. Sectors of the Croatian economy, 2002 to 2024. GFI `db_afs`, employment and firm counts by NKD area.

## Dropped

Ideas we set aside, each with one line of why, so we do not revisit them by accident.

- [none yet]
