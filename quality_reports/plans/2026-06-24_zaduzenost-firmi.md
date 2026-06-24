# Plan. Zaduzenost hrvatskih firmi iz GFI-ja

## Goal

Build a Croatian Quarto post about debt structure in Croatian non-financial firms
from the GFI MySQL database, but only if the financial debt fields pass a
reproducibility audit. If the audit fails, stop at the audit and do not write the
post.

## Data

- Source: FINA / GFI, MySQL table `db_afs`, one row per firm-year.
- Validation source for physical `bNNN` mapping:
  MySQL table `codes_gfi_db_afs_physical`, imported from
  `D:/data/poslovni_subjekti/sifrarnik/sifrarnici/financije_sifrarnik.xlsx`,
  sheet `cb_afs`. This workbook maps the physical `db_afs.bNNN` positions
  correctly; `codes_gfi` does not match this layout for these fields.
- Intended period: 2008-2024.
- Universe: active non-financial firms, `b110 > 0`, valid `nacerev21` sections
  `A` to `S`, excluding `nacerev21 = 'K'`.

## Validation Gates

- Do not use debt/assets unless `b061` has stable coverage and balance-sheet
  identity checks are credible.
- Do not use financial debt unless long-term debt components fit within
  `b084` and short-term debt components fit within `b094`.
- Do not use ICR until interest expense is explicitly mapped and validated.
  `b166 + b168` is not interest in the physical codebook.
- Every denominator must be positive, with firm counts reported by year.

## Implementation

- `python/import_gfi_db_afs_codebook.py` imports the local workbook into
  MySQL table `codes_gfi_db_afs_physical`.
- `python/debt_structure_build.py` writes:
  - `outputs/tables/debt_structure_aop_map.csv`
  - `outputs/tables/debt_structure_audit.csv`
  - `outputs/tables/debt_structure_yearly.csv`
  - `outputs/tables/debt_profitability_bins.csv`
  - `outputs/tables/debt_by_sector_size.csv`
- `python/debt_structure_charts.py` reads only `outputs/tables`. If the audit
  blocks the post, it exits cleanly without creating figures.
- If validation passes, create
  `posts/2026-06-zaduzenost-hrvatskih-firmi/index.qmd` with `draft: true` and
  no `[KUT]` markers.

## Literature Motifs

- Myers (2001): pecking order vs trade-off logic; profitability can lower
  leverage when firms finance from internal funds.
- Martinis and Ljubaj, HNB: Croatian corporate debt overhang and investment.
- Pepur, Curak and Poposki: determinants of capital structure in large Croatian
  companies.
- Sarlija and Harc: Croatian SMEs and the role of profitability in leverage.
- IMF, ECB, ESRB: leverage shocks, rollover risk, and financial fragility.

## Verification

- Run `python python/debt_structure_build.py`.
- Inspect `outputs/tables/debt_structure_audit.csv`.
- Only if `go_no_go` passes, run charts, write post, render the post, and QA
  against `_workflow/review-checklist.md`.

## Correction. 2026-06-24

The first implementation used `codes_gfi` and therefore mapped financial debt
to the wrong physical columns. The corrected implementation uses
`codes_gfi_db_afs_physical` imported from `financije_sifrarnik.xlsx`:
long-term financial debt is `b086 + b087`,
short-term financial debt is `b096 + b097`, total assets are `b061`, total
passive is `b108`, equity is `b063`, revenue is `b110`, and net result is
`b152 - b153`.
