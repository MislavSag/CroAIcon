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
