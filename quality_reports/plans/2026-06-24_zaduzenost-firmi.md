# Plan. Zaduzenost hrvatskih firmi iz GFI-ja

## Goal

Build a Croatian Quarto post about debt structure in Croatian non-financial firms
from the GFI MySQL database, but only if the financial debt fields pass a
reproducibility audit. If the audit fails, stop at the audit and do not write the
post.

## Data

- Source: FINA / GFI, MySQL table `db_afs`, one row per firm-year.
- Validation source for physical `bNNN` mapping:
  `D:/data/poslovni_subjekti/sifrarnik/sifrarnici/financije_sifrarnik.xlsx`,
  sheet `cb_afs`. This workbook maps the `db_afs` balance-sheet positions
  correctly; `codes_gfi` does not match the physical `bNNN` layout for these
  fields.
- Intended period: 2008-2024.
- Universe: active non-financial firms, `b125 > 0`, valid `nacerev21`,
  excluding `nacerev21 = 'K'`.

## Validation Gates

- Do not use debt/assets unless `b065` has stable coverage and balance-sheet
  identity checks are credible.
- Do not use financial debt unless long-term debt components fit within
  `b095` and short-term debt components fit within `b107`.
- Do not use ICR unless the sign of `b166 + b168` is consistent enough to
  normalize interest expense.
- Every denominator must be positive, with firm counts reported by year.

## Implementation

- `python/debt_structure_build.py` writes:
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
`financije_sifrarnik.xlsx`: long-term financial debt is `b086 + b087`,
short-term financial debt is `b096 + b097`, total assets are `b061`, total
passive is `b108`, and equity is `b063`.
