# QA. 2026-06-rast-marzi-po-sektorima

Score. 88.

Verdict. Commit only / review draft. The page renders, the NKD detail charts and the new Eurostat price diagnostic are reproducible, and the post is useful for review. It still uses GFI financial columns, so a stronger analysis-specific audit should precede treating it as a final publish-ready macro claim.

## Major

- [posts/2026-06-rast-marzi-po-sektorima/index.qmd:80] Financial-column reliance is disclosed, but the audit is still narrow. The post uses operating revenue and net result from the checked GFI fields, and the script writes a codebook audit table. Before final publication, add an analysis-specific audit table that checks aggregate revenue and net result plausibility by year against known FINA totals or another internal control.

## Minor

- [posts/2026-06-rast-marzi-po-sektorima/index.qmd:58] The Eurostat block correctly avoids a causal claim, but the phrase "najvjerojatnije pretvorio u bolji rezultat" is still a diagnostic inference rather than proof. This is acceptable for a working post, weaker for a flagship inflation claim.

## Passed

- The post has a two-beat headline and an empty description.
- The opener leads quickly to the central number. 8,4% (2021.) → 16,0% (2024.), plus 7,5 postotnih bodova.
- The added NKD numbers trace to `outputs/tables/sector_margin_growth_nkd2_2021_2024.csv`, `outputs/tables/sector_margin_growth_nkd3_2021_2024.csv`, and `outputs/tables/sector_margin_growth_nkd4_2021_2024.csv`.
- The Eurostat price numbers trace to `outputs/tables/price_margin_winners_2021_2024.csv`.
- All five charts are the right type for ranked categories. Horizontal bars use position on a common scale.
- The chart scripts read from `outputs/tables/` and write PNGs to both `outputs/figures/` and the post folder.
- The notes box names the source, measure, NKD levels, sample thresholds, limitations, and scripts.
- `python python/sector_margin_growth_2021_2024.py` passed.
- `python python/price_margin_winners.py` passed.
- `python python/sector_margin_growth_charts.py` passed.
- `python python/price_margin_charts.py` passed.
- `quarto render posts/2026-06-rast-marzi-po-sektorima` passed.
- `quarto render` passed and refreshed `_site/index.html`. It emitted the existing non-blocking 404 title warning.
