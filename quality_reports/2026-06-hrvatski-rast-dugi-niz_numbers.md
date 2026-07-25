# Number check: posts/2026-06-hrvatski-rast-dugi-niz/index.qmd

Reviewed as the post stands now (post prose mtime 2026-07-25 21:46). Read-only pass, no edits made.

## Staleness verdict (timeline steps 1-6)

File mtimes found:
- `scripts/gdp_drawdowns.R`: 18:58:20 -> `outputs/tables/gdp_drawdowns.csv`: 18:58:26
- `python/gdp_charts.py`: 21:40:18 -> chart PNGs in post folder: 21:40:27
- `posts/.../index.qmd`: 21:46:20
- `R/prepare_gdp.R`: 21:47:18 (final edit, two summary rows added)
- `outputs/tables/gdp_growth_eras.csv`, `gdp_growth_bars.csv`, `gdp_long.csv`, `gdp_anchors.csv`, `gdp_depth.csv`, `gdp_ribbon.csv`: 21:47:30-33 (final `scripts/update_gdp.R` rerun)

**Check requested: does `gdp_growth_bars.csv` match the era rows of `gdp_growth_eras.csv`?** Yes, exactly, all 6 rows (era, year0, year1, cagr, total, positive) are byte-identical between the two files. Confirmed in `R/prepare_gdp.R`: `gdp_growth_bars.csv` is written from `build_gdp_growth(long)` alone, and the step-5 edit only touched `build_gdp_growth_summary()` (added `"Socijalizam do vrha 1986 (odbaceni rez)"` and `"Cijeli niz 1952-2025 (trend)"`), never `build_gdp_growth()` or `build_gdp_long()`. So the values behind the chart (`gdp_2_growth_eras.png`, rendered at 21:40, before the final table regen at 21:47) are unchanged. **Charts are not stale.**

**Extra check on `gdp_drawdowns.csv` (oldest file, 18:58, computed before the post prose edit and before the final table regen):** independently recomputed all 8 peak/trough/fall_pct/recovery rows directly from the current (21:47) `gdp_long.csv` index column. Every value reproduces exactly (peak/trough index, fall_pct to 1dp, recovery_year). `gdp_drawdowns.csv` is **not stale** either, because `build_gdp_long()` (its input) was not touched by the step-5 edit.

No untrusted GFI column appears anywhere in the post (`grep -i` for `gfi|codes_gfi|db_afs|nacerev|employeecounteop|b[0-9]{3}` returns zero hits). This post is GDP-only, as expected.

## Findings table

| # | Number in post | Line(s) | Source | Status |
|---|---|---|---|---|
| 1 | "155 godina" (1870-2025 span) | 3 | 2025-1870=155; endpoints in `gdp_long.csv` rows 1 & 108 | matched |
| 2 | "Sedam padova i sedam povrataka" | 3, 14-15, 58, 122-124 | 2 war gaps (no data) + 5 `major=TRUE` rows in `gdp_drawdowns.csv` (1929, 1949, 1986, 2008, 2019) | matched |
| 3 | "pet kriza" | 14 | count of `major=TRUE` rows in `gdp_drawdowns.csv` = 5 | matched |
| 4 | Indeks 2015. = 100 (base year) | 22, 211 | `build_gdp_long(base_year = 2015)` in `scripts/update_gdp.R` | matched |
| 5 | 1870 -> 2025, "oko 26 puta"; indeks 6 -> indeks 150 | 29-30 | `gdp_long.csv`: 1870 index 5.8246 -> 6; 2025 index 149.5748 -> 150; 149.5748/5.8246 = 25.68 -> 26 | matched |
| 6 | +6,1% (1952-1980) | 39 | `gdp_growth_eras.csv` "Uspon socijalizma" cagr=6.1 | matched |
| 7 | +5,0% (1993-2008) | 40 | `gdp_growth_eras.csv` "Oporavak" cagr=5 | matched |
| 8 | +4,0% (2014-2025) | 40-41 | `gdp_growth_eras.csv` "Novije" cagr=4 | matched |
| 9 | Lomovi rasta 1980., 1994., 2009. | 44-45 | Bićanić, Deskar-Škrbić i Zrnc (2016), named in-text | literature |
| 10 | Counterfactual "po 5,0% godišnje" (1986 cut) | 46-48 | `gdp_growth_eras.csv` "Socijalizam do vrha 1986 (odbaceni rez)" cagr=5, matches "Oporavak" cagr=5 exactly (both 5.0, deliberately, per code comment) | matched |
| 11 | -0,9% (1980-1990) | 50 | `gdp_growth_eras.csv` "Zastoj 1980-ih" cagr=-0.9 | matched |
| 12 | -12,3% (1990-1993) | 50-51 | `gdp_growth_eras.csv` "Slom devedesetih" cagr=-12.3 | matched |
| 13 | -1,4% (2008-2014) | 51-52 | `gdp_growth_eras.csv` "Letargija" cagr=-1.4 | matched |
| 14 | +1,6% (1870-1900, Habsbursko) | 52 | `gdp_growth_eras.csv` "Habsbursko 1870-1900" cagr=1.6 | matched |
| 15 | +1,8% (1920-1939, Medjuratno) | 53 | `gdp_growth_eras.csv` "Medjuratno 1920-1939" cagr=1.8 | matched |
| 16 | Rat 1914.-1919. (gap) | 63-64 | `gdp_long.csv` has no rows 1914-1919 (jumps 1913->1920) | matched |
| 17 | Rat 1940.-1946. (gap) | 64 | `gdp_long.csv` has no rows 1940-1946 (jumps 1939->1947) | matched |
| 18 | Indeks 16 (1929.) -> indeks 13 (1932.), oko minus 18% | 69-70 | `gdp_drawdowns.csv` row 2: peak_index 15.99->16, trough_index 13.18->13, fall_pct -17.6->-18% | matched |
| 19 | Nominalni dohodak oko 40%, cijene "gotovo prepolovljene" | 72-73 | Gnjatović (2017), named in-text | literature |
| 20 | Realni proizvod oko 18% (cross-ref of #18) | 73 | Same as #18, cross-cited to Gnjatović (2017) | matched + literature |
| 21 | "dvostruko više robe" | 74 | Gnjatović i Aleksić (2011), named in-text | literature |
| 22 | Povratak 1938. (devet godina) | 75 | `gdp_drawdowns.csv` row 2: recovery_year=1938, recovery_years=9 | matched |
| 23 | Indeks 19 (1949.) -> indeks 16 (1952.), oko minus 18% | 80-81 | `gdp_drawdowns.csv` row 3: peak_index 19.41->19, trough_index 15.99->16, fall_pct -17.6->-18% | matched |
| 24 | Povratak 1955. (šest godina) | 82 | `gdp_drawdowns.csv` row 3: recovery_year=1955, recovery_years=6 | matched |
| 25 | Indeks 16 (1952.) -> indeks 83 (1980.) | 93-94 | `gdp_long.csv`: 1952 index 15.986->16; 1980 index 82.868->83 | matched |
| 26 | "Otprilike peterostruko" | 94 | 82.868/15.986 = 5.18x (also 84.17/15.986 = 5.26x for 1986) | matched |
| 27 | Sljedećih šest godina (1980->1986 stall) | 99 | `gdp_drawdowns.csv` row 5: peak_year=1980, recovery_year=1986, recovery_years=6 | matched |
| 28 | Indeks 84 (1986. vrh) | 100 | `gdp_long.csv` 1986 index 84.1698 -> 84 | matched |
| 29 | Indeks 105 (2008.) -> indeks 96 (2012.), oko minus 9% | 104-105 | `gdp_drawdowns.csv` row 7: peak_index 105.44->105, trough_index 95.83->96, fall_pct -9.1->-9% | matched |
| 30 | "šest godina" (era length 2008-2014) | 105-106 | `gdp_growth_eras.csv` "Letargija" year1-year0 = 2014-2008=6 | matched |
| 31 | Vrh iz 2008. prijeđen 2017. | 106 | `gdp_drawdowns.csv` row 7: recovery_year=2017 | matched |
| 32 | Indeks 119 (2019.) -> 110 (2020.) -> 125 (2021.) | 113-114 | `gdp_long.csv`: 2019 idx 119.218->119; 2020 idx 110.374->110; 2021 idx 125.425->125 | matched |
| 33 | Indeks 150 (2025.) | 115-116 | `gdp_long.csv` 2025 index 149.575 -> 150 (same as #5) | matched |
| 34 | Trzaji 1927., 1956., zastoj 1980-ih, 1999.; "nijedan ne prijeđe minus 5%" | 118-119 | `gdp_drawdowns.csv`: 1927 fall -4.2%, 1956 fall -4.9%, 1980-83 fall -2.5% (all <5%); 1999 not in this table, see #45 | matched |
| 35 | "devet godina" (depresija povratak, recap) | 122 | Same as #22 | matched |
| 36 | "šest" (blokada povratak, recap) | 122 | Same as #24 | matched |
| 37 | "devet godina" (letargija vrh, recap) | 122-123 | Same as #31 (2017-2008=9) | matched |
| 38 | "gotova u dvije" (pandemija recovery) | 123 | `gdp_drawdowns.csv` row 8: peak_year=2019, recovery_year=2021, recovery_years=2 | matched |
| 39 | "12 do 14%" (BDP vs društveni proizvod) | 136, 249 | Dubey, Miljković via Bićanić, Deskar-Škrbić i Zrnc (2016), named in-text | literature |
| 40 | Ribbon: oba ruba pojasa padaju 1929->1932 | 141-142 | `gdp_ribbon.csv`: lo 14.15->11.67, hi 16.70->14.34, both decline | matched |
| 41 | Od 1986. (indeks 84) pad minus 39% | 160 | `gdp_anchors.csv` row 1: peak_index 84.2->84, fall_pct -39.4->-39% | matched |
| 42 | Od 1990. (indeks 76) minus 33% | 160 | `gdp_anchors.csv` row 3: peak_index 75.6->76, fall_pct -32.5->-33% | matched |
| 43 | Vrh 1989., pad oko minus 37% | 161-163 | `gdp_anchors.csv` row 2: peak_index 81.5, fall_pct -37.4->-37% | matched |
| 44 | Maddison/PWT/Svjetska banka "svi ... oko minus 33%" | 178-179 | `gdp_depth.csv`: Maddison -32.5 (->33%, matches), PWT -34.8 (->35%), Svjetska banka -33.5 (->34%) | **mismatch** (see below) |
| 45 | Vrh 1986. prijeđen 2003.; povratak "jedanaest do sedamnaest" | 187-189 | `gdp_drawdowns.csv` row 6: recovery_year=2003, recovery_years=17 (from 1986); from 1990 anchor (75.6), `gdp_long.csv` 2001 idx 77.38 first exceeds it -> 2001-1990=11 | matched |
| 46 | "od dvije godine do sedamnaest" (closing) | 204-205 | min/max of measurable `recovery_years` in `gdp_drawdowns.csv`: 2 (2019) to 17 (1986) | matched |
| 47 | Trend 2,3% vs 3,1% (cijeli niz od 1952.) | 214-216 | `gdp_growth_eras.csv`: "Cijeli niz 1952-2025 (trend)" cagr=2.3, "Cijeli niz 1952-2025" cagr=3.1 | matched |
| 48 | Eurostat od 1995.; Maddison 1952-1994.; Tica do 1910.; desetljetne točke do 1870. | 219-222 | `gdp_long.csv` segment/granularity columns: "modern" from 1995, "maddison" 1952-1994, "tica" annual from 1910, "tica" benchmark 1870-1900 | matched |
| 49 | Prag pada "oko 7%" | 224-226 | `scripts/gdp_drawdowns.R` line 53: `draw$major <- draw$fall_pct <= -7` | matched (consistent with #34's "minus 5%", see note below) |
| 50 | Zastoj 1999. "oko minus 0,5%" | 227-229 | `gdp_long.csv`: 1998 idx 69.813, 1999 idx 69.473 -> (69.473/69.813-1)=-0.49% | matched |
| 51 | Depresija "oko minus 18%" (Napomene restatement) | 230-231 | Same as #18 | matched |
| 52 | Maddison 2023. "oko minus 17% za Jugoslaviju" | 231-232 | Named source "Maddison 2023" in-text, Yugoslavia-level figure, not in the 7 listed output tables (Croatia-only) | literature/named-source, not independently re-verified (out of scope of the 7 outputs/tables files) |
| 53 | "oko desetine stanovništva i četvrtine teritorija" | 243 | Aslund (2001); Bićanić, Deskar-Škrbić i Zrnc (2016), named in-text | literature |

## Flag: item #44, Maddison/PWT/World Bank "oko minus 33%"

Post text (line 178-179): *"Maddison, Penn World Table i Svjetska banka svi pokazuju isti pad, oko **minus 33%** od 1990."*

`outputs/tables/gdp_depth.csv`://
| source | fall_pct | rounds to (house convention, half away from zero) |
|---|---|---|
| Maddison | -32.5 | -33% |
| PWT | -34.8 | -35% |
| Svjetska banka | -33.5 | -34% |

Only Maddison's own figure (which is also literally the post's own -32.5 estimate, "u skladu s našom procjenom") rounds to -33%. PWT rounds to -35% and Svjetska banka to -34%, using the same rounding convention the post applies everywhere else (e.g. -32.5 -> "minus 33%" at line 160). "Oko" (roughly) gives some rhetorical cover and the three values do cluster within about 2.3 points of each other, but citing a single "minus 33%" for all three understates PWT's gap by 2 points, in a paragraph whose entire point is to caution against over-reading source agreement. Recommend either "oko minus 33 do 35%" or naming each source's own rounded figure.

No other mismatches, unsourced, or stale numbers found.

## Summary

53 numbers/figures/spans/counts traced. 48 matched to a current output table or direct arithmetic on one. 5 are literature-attributed (named source in prose): break years 1980/1994/2009, the 12-14% BDP/društveni proizvod gap, the 10%/25% population/territory figures, the Yugoslavia-level -17% Maddison figure, and the nominal-income/price/debt figures from Gnjatović. 1 flagged as a soft mismatch (item #44). Zero unsourced. Zero stale (both `gdp_growth_bars.csv` vs `gdp_growth_eras.csv` era rows and `gdp_drawdowns.csv` against the current `gdp_long.csv` were independently re-verified to match exactly, despite the drawdowns file and chart PNGs having older mtimes than the final table regen). No untrusted GFI column present.
