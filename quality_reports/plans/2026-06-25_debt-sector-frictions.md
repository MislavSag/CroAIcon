# Plan. Debt structure, sector credit, and financial frictions

Date. 2026-06-25

Target post. `posts/2026-06-zaduzenost-hrvatskih-firmi/index.qmd`

## Goal

Extend the existing GFI debt post from a narrow debt-concentration piece into a fuller view of:

1. Detailed financing and indebtedness structure by NKD activity.
2. The investment-debt relation as a simple financial-frictions diagnostic.
3. One current literature-motivated angle that fits the data and does not overclaim.

## Constraints

- Keep the physical `db_afs` codebook as the source of truth. Do not use `codes_gfi`.
- Every new number in the post must come from `outputs/tables`.
- Every new chart must read from `outputs/tables` and write to `outputs/figures`, then copy into the post folder.
- New financial columns require an analysis-specific audit before they can enter prose or charts.
- Do not use interest coverage unless the interest column is validated in this pipeline.
- Keep `[KUT]` editorial choices human if the final framing is uncertain.

## Implementation

1. Inspect `codes_gfi_db_afs_physical` for the fixed-asset column needed for investment intensity.
2. Extend `python/debt_structure_build.py`.
   - Add the fixed-asset column to the AOP map and audit.
   - Build firm-year panel features:
     - financial debt = `b086 + b087 + b096 + b097`;
     - debt/revenue and debt/assets;
     - short-term debt share;
     - fixed-assets investment proxy = `(fixed_assets_t - fixed_assets_t-1) / fixed_assets_t-1` at firm level.
   - Save additional tables:
     - `outputs/tables/debt_by_sector_detail.csv`;
     - `outputs/tables/debt_investment_by_sector.csv`;
     - `outputs/tables/debt_financial_frictions_bins.csv`;
     - `outputs/tables/debt_literature_current.csv` if the literature angle needs a compact result table.
3. Extend `python/debt_structure_charts.py`.
   - For sector structure, use sorted bars or dot/bar small multiples. Common position scale, no dual axis.
   - For investment vs debt, use a scatter or binned dot chart. The point is the relation between leverage and investment, not precise firm-level prediction.
   - For the literature angle, prefer a simple binned chart if it adds one distinct claim.
4. Rewrite the post.
   - Preserve the existing validated debt story.
   - Add sector structure after the aggregate/maturity sections.
   - Add the frictions section after sector structure.
   - Add the current-literature section only if the output table supports it.
   - Keep notes lean, with all new columns and caveats stated once.
5. Verify.
   - Run `python python/debt_structure_build.py`.
   - Run `python python/debt_structure_charts.py`.
   - Render with `quarto render posts/2026-06-zaduzenost-hrvatskih-firmi`.
   - Report any validation or render failure plainly.

## Risks

- The fixed-asset column may not pass coverage or plausibility checks. If so, keep the frictions idea as blocked and do not publish the chart.
- Delta fixed assets is a net stock proxy, not true capex. It misses disposals, depreciation, revaluations, and accounting changes.
- Debt can proxy both access to finance and financial pressure. The post should call the pattern a friction diagnostic, not causal proof.
