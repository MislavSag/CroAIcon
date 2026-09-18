# Common-sense check: does observed industry corroborate the 1991-1992 GDP fall?

**Question.** The early-1990s stretch of the long-run GDP series is reconstructed, not
observed (`R/prepare_gdp.R` flags 1991-1995 as `break_period`; the GDP plan calls the depth of
the 1990s fall "the single number to trust least"). It is annual, so it never shows *when* inside
the year the economy fell. Does an observed, hard, monthly indicator — industrial production —
sit consistently with the reconstructed annual numbers?

**What was done.** Transcribed HNB *Tablica 2, "Razina industrijske proizvodnje"* (monthly,
1991-01 to 1992-12; *Izvor: Podaci DZS obrađeni u NBH*) into
`data/reference/hnb_industrijska_proizvodnja_1991_1992.csv`, derived a monthly level index
(1990 = 100), and ran a **Chow-Lin temporal disaggregation** of annual GDP per capita (Maddison
2023, the reconstructed backbone) to monthly, with the industrial-production index as the
indicator. Script: `R/chow_lin_gdp_1991_1992.R`. Numbers below trace to
`outputs/facts/chowlin_check_1991_1992.json` and `outputs/tables/gdp_monthly_chowlin_1991_1992.csv`.

## Method and its one honest limit

Chow-Lin fits `GDP = a + b·IPI` at the annual level and distributes annual GDP to months along
the indicator, subject to each year's 12 months summing back to the annual total. We have the
indicator for **two years only**, so there are two annual benchmarks and two parameters: the model
is **exactly identified**. The two annual residuals are zero, the AR(1) term drops out, and the
estimate is the indicator **linearly rescaled to hit the annual totals** —
`GDP_month = 314.95 + 7.575 · IPI_month` (monthly per-capita units).

That is the Chow-Lin solution in this case, not a shortcut, and the closed form reproduces both
annual totals to machine precision (1991: 10296.2; 1992: 9331.9). `tempdisagg::td()` cannot run a
two-benchmark problem (insufficient degrees of freedom for the ML step; its GLS solver segfaults on
the degenerate case), and it is not needed — the closed form is exact here.

**The limit this implies.** With two benchmarks the procedure *imposes* the shape of industrial
production on GDP. It therefore cannot independently confirm the **depth** of the GDP fall; it can
only check whether the reconstructed annual numbers are **consistent** with the observed indicator
in direction, timing, and relative magnitude. That consistency is exactly what a common-sense
check is for.

## What it shows

| check | result |
|-------|--------|
| Annual totals reproduced | exact (1991, 1992) |
| **Out-of-sample 1990** | line fitted on 1991-92 predicts 1990 GDP = 12869 vs actual 12948 → **−0.6%** |
| Industry fall 1990 → 1992 | 100 → 61.1 (**−38.9%**) |
| GDP fall 1990 → 1992 | **−27.9%** (GDP "beta" to industry ≈ **0.72**) |
| Trough month | both Dec 1991 (GDP index 68.0, industry 55.3) |
| Within-1991 GDP path | 84.9 (Jan) → 68.0 (Dec), the war crash in H2-1991 |

Three things line up:

1. **Out-of-sample recovery of 1990 (the strongest evidence).** The industry→GDP relationship
   estimated purely on 1991-1992 extrapolates back to 1990 and lands within **0.6%** of the
   independent Maddison 1990 figure. Two unrelated sources — observed industrial production and a
   reconstructed national-accounts backcast — agree on the level a year outside the fitting window.
   That is hard to get by chance.

2. **Magnitude is sensibly damped.** Industry fell ~39% from 1990 to 1992; GDP ~28%. GDP moves
   about 0.72% per 1% of industry — a muted version of the industrial collapse, which is what you
   expect when industry is the most cyclical, war-exposed slice of a broader economy (services,
   agriculture, and the public sector fell too, but less).

3. **Timing matches the war.** The monthly path puts the collapse squarely in **H2-1991** — the
   index is flat-to-high through spring 1991, then falls hard from August, bottoming in December
   1991 — exactly when the war escalated. The 1990s low is dated, not assumed.

## Verdict

**The reconstruction passes the smell test.** Observed industrial production corroborates the
reconstructed 1991-1992 GDP fall in all three respects — direction, timing, and relative
magnitude — and the independent 1990 level is recovered to within a percent. The reconstructed
numbers are not contradicted by the one hard, observed indicator available for these years.

This does **not** independently validate the *depth* of the GDP fall (the two-benchmark
disaggregation imposes industry's shape; it cannot vote on how deep GDP itself went). It does say
the reconstructed depth is consistent with — and slightly milder than — the observed industrial
collapse, which is the economically sensible ordering.

## Caveats

- **Two benchmarks.** The monthly *shape* is industry's, by construction; treat the within-year
  path as illustrative, not measured.
- **Indicator is industry only** — narrower than GDP. The damping (beta 0.72) is the visible sign
  of that gap.
- **Target is a reconstruction** (Maddison per-capita, 2011 international $), not observed national
  accounts, and is shown indexed to 1990 = 100 so units do not bite. Monthly "GDP" is an analytical
  construct.

## Reproduce

```
Rscript R/chow_lin_gdp_1991_1992.R
```

Reads `data/reference/hnb_industrijska_proizvodnja_1991_1992.csv` and
`data/processed/gdp_raw.csv`; writes `outputs/tables/gdp_monthly_chowlin_1991_1992.csv`,
`outputs/facts/chowlin_check_1991_1992.json`, and
`outputs/figures/gdp_vs_ipi_monthly_1991_1992.png`. Source image and provenance:
`data/reference/hnb_industrijska_proizvodnja_1991_1992.png` and `…_source.md`.
