# Plan — "Zagreb knjiži profit, ostatak zemlje radi"

Status: in progress (author pre-approved the run on 2026-06-21).

## Finding
Grad Zagreb holds a stable ~37% of jobs but a much larger, persistently higher share of corporate
profit (~½ to ⅔). Revenue sits in between (~55%). The gap between the profit line and the employment
line is the **headquarters effect**: profit is booked at the HQ (Zagreb), not where the work happens.
Surprise: excluding financials (NKD K) barely changes it → it is not just the banks.

## Data & method (robust by construction)
- Source: `db_afs`, one row per firm-year, `reportyear` 2002–2024. Geography `countyid` (100% populated;
  Grad Zagreb = code 21) -> `ref_county`.
- Net result per firm (signed), using the blessed view logic (NOT `b183`, which is dead — 1,330/162,532
  nonzero in 2024):
  `nr = COALESCE(NULLIF(b184,0),NULLIF(b197,0),0) - COALESCE(NULLIF(b185,0),NULLIF(b198,0),0)`
- Profit pool = SUM(nr) over firms with nr>0 (robust; avoids negative-county-sum chaos).
- Jobs = SUM(`employeecounteop`); Revenue = SUM(`b125`).
- Zagreb share = Zagreb total / RH total, per measure, per year. Shares are within-year ratios -> immune
  to the HRK->EUR 2023 break and to `price_deflator` (NULL for 2024 anyway).
- Concentration index = profit share / jobs share (>1 = books more profit per job).
- Robustness: compute all-sectors AND excl-K; report they barely differ.

## Deliverables
1. `python/zagreb_profit_build.py` -> `outputs/tables/zagreb_profit_shares.csv` (county-RH shares by year,
   both all-sectors and excl-K), prints headline numbers.
2. `python/zagreb_profit_charts.py` -> 2 PNGs in `outputs/figures/`:
   - `zagreb_1_shares.png`: 3 lines 2002–2024 (profit share, revenue faint, jobs); gap = the story.
   - `zagreb_2_staircase.png`: 2023 horizontal bars, Zagreb share by measure (jobs -> revenue -> profit).
3. `posts/2026-06-zagreb-profit/index.qmd`: draft (draft: true) with [KUT] markers for interpretation,
   numbers pulled only from the CSV, full method box. Copy PNGs into the post folder.

## Caveats to surface in the post
- "Knjiži", not "stvara": measures place of BOOKING (HQ), not value creation.
- 2024 preliminary (late HQ filers depress Zagreb's 2024 profit share to ~45%); headline on 2023/structural.
- Profit pool is volatile year to year (one-off revaluations at giants) -> headline the stable jobs/revenue
  anchor and the persistent gap, not a single year's peak.
- `b125`/profit detailed P&L cleaner here because we use the view's blessed fields; still report coverage.
