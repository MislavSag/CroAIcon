# Plan. Restructure the long-run GDP post into a chart-driven growth story

**Status: DONE (2026-06-21).** Built 7-chart structure, growth-by-era bars, four era
zooms, methodology section; dropped the fan. Verified via style-critic, number-checker,
chart-critic; all flagged number/chart issues fixed (summary growth rows added, crisis-2
band margin, crisis-1 retitle). Five+ [KUT] left for the author; `draft: true`.

## Context

The current post (`posts/2026-06-hrvatski-rast-dugi-niz/index.qmd`) tells the 1870–2025
story off a single hero line plus two robustness charts. The author's feedback: it
does not flow. The post should instead **demonstrate** long-term growth with a chart
per era, **quantify** the long-term growth rates (bar chart), **explain the reasons
between crises**, and **discuss how the series is calculated and the problems with
interpolating it**. The pre-1952 "ten estimates" fan chart does not communicate and is
cut. Decisions taken with the author: four individual per-era zoom charts; growth bars
by era; drop the fan chart.

## New chart set

Keep the hero line. Add a growth-rate bar chart and four era zoom charts. Drop the fan.
Keep the cross-source panels for the methodology section.

| Chart | File | Status | Point |
|------|------|--------|-------|
| Hero long-run line 1870–2025 | `gdp_1_long_index.png` | keep | the whole arc, five up five down |
| Growth by era (bars) | `gdp_2_growth_eras.png` | NEW | how fast it grew, by era |
| Zoom. Deep past 1870–1952 | `gdp_3_zoom_prewar.png` | NEW | thin, flat, interpolated start |
| Zoom. Socialism 1952–1986 | `gdp_4_zoom_socialism.png` | NEW | the +5%/yr boom |
| Zoom. First crisis 1986–2000 | `gdp_5_zoom_crisis1.png` | NEW | deep, fast plunge |
| Zoom. Second crisis + COVID 2008–2025 | `gdp_6_zoom_crisis2.png` | NEW | shallow, long, then surge |
| Cross-source panels | `gdp_7_raw_panels.png` | keep (renamed) | the splice is not an artifact (methodology) |
| ~~Pre-1952 estimate fan~~ | ~~`gdp_3_prewar_estimates.png`~~ | **DROP** | confused readers |

Verified era growth (real GDP p.c., from `data/processed/gdp_long.csv`), the bar chart payload:

- Socijalizam 1952–1986. **+5.0%/yr** (+427%)
- Prva kriza 1986–1993. **minus 6.9%/yr** (minus 39%)
- Oporavak 1993–2008. **+5.0%/yr** (+107%)
- Druga kriza 2008–2014. **minus 1.4%/yr** (minus 8%)
- Novije 2014–2025. **+4.0%/yr** (+55%)

Pre-1952 rates (benchmark/interpolated, kept to prose, not bars): Habsburg 1870–1900
~+1.6%/yr, interwar 1920–1939 ~+1.8%/yr.

## Code changes

**`R/charts.R`** (reuse `theme_house()`, `house_pal` from `R/house_style.R`):
- Add `save_gdp_zoom_chart(long, year_min, year_max, path, title, subtitle, caption, bands = list())`.
  One windowed line chart in house style. Reuses the grid-completion + benchmark
  (points + dashed) + war-gap-break logic already in `save_gdp_index_chart`; refactor
  that shared logic into a small internal helper so both use it. Optional shaded crisis
  bands per window.
- Add `save_gdp_growth_bars(eras, path, title, subtitle, caption)`. Horizontal bars,
  green (`house_pal$rise`) for positive, red (`house_pal$fall`) for negative, value
  labels with plus/minus in words. Mirror the existing python `sectors_4_change` look.
- Remove `save_gdp_fan_chart()` (no longer used). `load_tica_estimates()` in
  `R/get_tica.R` stays (harmless, may serve a future cross-country post).

**`R/prepare_gdp.R`**:
- Add `build_gdp_growth()` returning a data.frame (era label, year0, year1, cagr,
  total, positive flag) for the five post-1952 eras above, computed from the spliced
  `long` series. One source of truth for the bar chart and the prose numbers.

**`scripts/update_gdp.R`**:
- Build growth eras, write `outputs/tables/gdp_growth_eras.csv`, render
  `gdp_2_growth_eras.png`.
- Render the four zoom charts via `save_gdp_zoom_chart` with the windows above
  (first/second crisis windows pass shaded bands).
- Keep the raw-source panel, rename output to `gdp_7_raw_panels.png`.
- Remove the fan chart build and its `outputs/tables/gdp_prewar_estimates.csv` write.
- Update the post-figure copy block to the new filename set (hero, growth, 4 zooms,
  raw panels). Drop the old `gdp_2_raw_panels.png` / `gdp_3_prewar_estimates.png`
  copies.

**`posts/2026-06-hrvatski-rast-dugi-niz/index.qmd`** restructure:
1. Lede + hero line. The arc, the thesis (linija se uvijek vrati), the two-crises tease.
2. `## Koliko brzo je rasla, i kada` — growth bars. Winners (socialism, recovery,
   recent ~4–5%/yr) vs losers (two crises). The long-term-growth-rate payload.
3. Era walk, each its own zoom chart + a short "reasons" paragraph:
   - `## Prije 1900. ...` deep-past zoom. Low, flat, thin, interpolated. Touches
     interpolation lightly (points to the methodology section).
   - `## Socijalizam ...` socialism zoom. +5%/yr, industrijalizacija i sustizanje.
   - `## Prva kriza ...` crisis-1 zoom. Rat i tranzicija, minus 6.9%/yr.
   - `## Druga kriza ...` crisis-2 + COVID zoom. Globalna kriza + duga domaća
     recesija, pa COVID, pa uzlet.
4. `## Pet puta dolje, pet puta natrag` — recurrence synthesis (short).
5. `## Kako je ovo izračunato` — methodology. Chain-link splice (rast, ne razine);
   the interpolation problems (dekadne benchmark točke do 1910., ratne rupe,
   rekonstrukcija 1991.–1995.); the cross-source check (`gdp_7_raw_panels.png`)
   showing the splice is not an artifact. This is the "how it's calculated / problems
   with interpolating" the author asked for.
6. Closing `[KUT]` + `## Napomene` (lean, as now).
- Keep `[KUT]` markers at interpretation forks (socialism meaning, the reason each
  crisis cut as it did, the closing resilience-or-ceiling verdict). State only
  uncontroversial drivers in the body; leave the angle to `[KUT]`.
- Remove all references to the dropped fan chart.
- Cleanup: delete the now-orphan `posts/.../gdp_3_prewar_estimates.png` and the old
  `gdp_2_raw_panels.png` (replaced by `gdp_7_raw_panels.png`).

## Verification

1. `Rscript scripts/update_gdp.R` builds clean, writes the new figures to
   `outputs/figures/` and copies them into the post folder, plus
   `outputs/tables/gdp_growth_eras.csv`.
2. Visually check each new PNG (zooms read correctly, growth bars green/red with
   labels, deep-past zoom shows benchmark points + war-gap breaks).
3. `quarto render posts/2026-06-hrvatski-rast-dugi-niz/index.qmd --to html -M draft:false`
   renders; all six/seven figures resolve in `_site`.
4. Run the `style-critic`, `number-checker`, and `chart-critic` agents on the post;
   every figure in the growth bars + prose must trace to `outputs/tables/gdp_growth_eras.csv`
   and `gdp_long.csv`; no stray dashes/colons; headers are standalone claims.
5. Confirm no residual fan-chart references and no orphan PNGs.

## Out of scope / left to the author

- The five `[KUT]` interpretation lines stay unfilled (house rule).
- Draft flag stays `draft: true` until the `[KUT]`s are resolved.
- The cross-country (T16) comparison remains a separate future post in the backlog.
