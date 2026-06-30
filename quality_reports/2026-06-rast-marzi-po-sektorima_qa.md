# QA. 2026-06-rast-marzi-po-sektorima

Score. 88.

Verdict. Commit only / review draft. The page renders and the numbers are reproducible, but the topic uses GFI financial columns, so a stronger audit should precede treating it as a final publish-ready macro claim.

## Major

- [posts/2026-06-rast-marzi-po-sektorima/index.qmd:40] Financial-column reliance is disclosed, but the audit is still narrow. The post uses operating revenue and net result from the physical GFI codebook, and the script writes a codebook audit table. Before final publication, add a short analysis-specific audit table that checks aggregate revenue and net result plausibility by year against known FINA totals or another internal control.

## Minor

- [posts/2026-06-rast-marzi-po-sektorima/index.qmd:36] The payoff is clear, but it opens the next analysis rather than landing a fully closed angle. This is acceptable for a quick diagnostic page, weaker for a flagship post.

## Passed

- The post has a two-beat headline and an empty description.
- The opener leads quickly to the central number. 8,4% (2021.) → 16,0% (2024.), plus 7,5 postotnih bodova.
- Section headers state claims.
- The chart is the right type for a ranking. Horizontal bars use position on a common scale.
- The chart reads from `outputs/tables/sector_margin_growth_2021_2024.csv` and writes to both `outputs/figures/` and the post folder.
- The notes box names the source, measure, sample rule, limitations, and scripts.
- `quarto render posts/2026-06-rast-marzi-po-sektorima` passed.
- `quarto render` passed and refreshed `_site/index.html`.
