# HNB monthly industrial production, 1991-1992 (transcription provenance)

**File.** `hnb_industrijska_proizvodnja_1991_1992.csv`
**Source image.** `hnb_industrijska_proizvodnja_1991_1992.png` (HNB document scan, originally
supplied as `for Chow-Lin.png`).
**Source.** Hrvatska narodna banka (HNB), **Tablica 2 — "Razina industrijske proizvodnje"**,
subtitle *"- stope rasta -"* (growth rates). Footer: *Izvor: Podaci DZS obrađeni u NBH* (DZS data
processed by the NBH).
**Coverage.** Monthly, 1991-01 to 1992-12 (24 observations). Hand-transcribed from the scan.

## Columns

Every value in the table is a growth rate (percent). Left to right:

| column | table header | meaning |
|--------|--------------|---------|
| `m_dezez` | Mjesečne, dezezonirane | month-on-month, deseasonalised |
| `m_orig` | Mjesečne, originalne | month-on-month, original |
| `yoy_month` | Međugodišnje, mjesečne | year-on-year, single month |
| `yoy_cumul` | Međugodišnje, kumulativ | year-on-year, cumulative (year to date) |
| `idx1990_orig` | 1990=100, originalne | % deviation of the level from the 1990 average, original |
| `idx1990_dezez` | 1990=100, dezezonirane | % deviation from the 1990 average, deseasonalised |
| `seas_idx` | Sezonski indeks (stopa) | seasonal index, as a rate |
| `idx1991_orig` | 1991=100, originalne | % deviation from the 1991 average, original |
| `idx1991_dezez` | 1991=100, dezezonirane | % deviation from the 1991 average, deseasonalised |

## Deriving a level index (1990=100)

`idx1990_orig` is the percent deviation of the monthly level from the 1990 average, so the level
index is simply:

```
ipi_1990_100 = 100 + idx1990_orig
```

(Use `idx1990_dezez` for the deseasonalised level.)

## Transcription cross-checks (passed)

- `idx1990_orig` reproduces the year-on-year column: Jan-1992 level 56.2 / Jan-1991 level 79.3 − 1
  = −29.1% ≈ the −29.0 cell in `yoy_month`.
- Monthly levels average to the cumulative-YoY cells: 1991 averages **71.7** (vs −28.5 in
  `yoy_cumul[1991-12]`), 1992 averages **61.1** (vs −14.6 in `yoy_cumul[1992-12]`).

## Caveats

- Original (`*_orig`) series carry the industrial seasonal pattern; deseasonalised (`*_dezez`)
  remove it. The Chow-Lin disaggregation in `R/chow_lin_gdp_1991_1992.R` uses the original level
  index as the indicator.
- This is industrial production only — a hard, observed indicator, but narrower than GDP (no
  services, agriculture, or public sector). That gap is the point of the common-sense check.
