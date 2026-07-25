# Chart QA. Svi naši usponi i padovi (dugi niz BDP-a)

Read-only pass, `chart-critic`. Scope: the seven figures in
`posts/2026-06-hrvatski-rast-dugi-niz/` (`gdp_1_long_index.png` …
`gdp_7_raw_panels.png`), the build script `python/gdp_charts.py`, the tables it
reads under `outputs/tables/`, and the post prose/captions in
`posts/2026-06-hrvatski-rast-dugi-niz/index.qmd`. Bar applied:
`_workflow/chart-playbook.md`. Context read: `MEMORY.md`
(`[LEARN:chart]` ribbon/line gap handling) and the prior QA pass in
`quality_reports/2026-06-hrvatski-rast-dugi-niz_qa.md`, which fixed the war-gap
interpolation on gdp_1/gdp_3/gdp_4/gdp_5 but did not touch `raw_panels()`.

This pass covers the state after today's edit: gdp_2 rebuilt to six bars split
at 1980/1990/1993 ("Rast u dva naleta, prvi jači"), gdp_4 retitled ("Socijalizam
diže liniju do 1980., pa zastoj", band label "zastoj od 1980."), gdp_5 retitled
("Slom devedesetih, smjer siguran a dubina nije"), gdp_6 retitled ("Letargija pa
COVID, plitko, dugo, pa uzlet").

## Critical

- **Figure:** `gdp_4_zoom_socialism.png`.
  **Problem:** The post caption directly under the figure still reads *"...i
  zastoj 1980-ih"* (index.qmd line 91), the same term the body prose (line 50,
  *"Zastoj minus 0,9% godišnje (1980. do 1990.)"*) and the `gdp_2` bar
  (`gdp_growth_bars.csv`: `"Zastoj 1980-ih",1980,1990,-0.9`) use for a
  **ten-year, 1980-1990** span. Today's rebuild changed the chart's own
  in-image band label to *"zastoj od 1980."* (open-ended, no end year), on a
  shaded band that only runs **1980-1986** (`zoom(1949, 1986, ...,
  bands=[..., (1980, 1986)]` in `python/gdp_charts.py`, the chart's own x-axis
  stops at 1986). A reader cannot get the 1990 endpoint from this figure at
  all, yet the caption's "1980-ih" borrows the decade framing that belongs to
  the *other* chart's 1980-1990 definition. Same word, two different spans, in
  the same post, and the two places that should agree (caption vs. the label
  it's captioning) no longer do. This is the chart (as captioned) making a
  different claim than the prose around it.
  **Fix:** Pick one span for "zastoj" and use it everywhere. Simplest: since
  gdp_4's window physically ends at 1986, change the qmd caption (line 91) to
  match what's actually drawn, e.g. *"...zastoj do 1986."* or *"...zastoj od
  1980. (do 1986.)"*, dropping "1980-ih". Leave the 1980-1990/-0,9% "Zastoj
  1980-ih" name for gdp_2 only, and don't reuse "1980-ih" for the shorter
  window in gdp_4's caption or band label.

## Major

- **Figure:** `gdp_7_raw_panels.png` (Tica panel, bottom-left).
  **Problem:** `raw_panels()` in `python/gdp_charts.py` plots the Tica series
  with `d = raw_long[raw_long.source == src].sort_values("year"); ax.plot(d.year,
  d.value, ...)` with no year-grid fill. `outputs/tables/gdp_raw_long.csv` has
  real row gaps for Tica at exactly (1913→1920) and (1939→1947), i.e. no data
  for 1914-1919 and 1940-1946, confirmed both by the CSV and visually (the
  panel draws one unbroken line from 1910 to 1989, no break, no band). This
  interpolates straight across both war gaps in the same Tica series that
  `gdp_1` and `gdp_3` correctly break (via `annual_grid()`, NaN on a complete
  year grid). Same source, drawn two different ways in the same post: a real
  break in gdp_1/gdp_3, bridged in gdp_7. This is the exact trap the playbook
  names by name ("the war years missing in Tica break the GDP line on
  purpose") and the same bug class logged in `MEMORY.md`
  ([LEARN:chart]), just missed in the one function that pipeline fix didn't
  reach.
  **Fix:** In `raw_panels()`, before plotting each panel, build a complete
  per-source year grid and left-merge, same pattern as `annual_grid()`:
  `grid = pd.DataFrame({"year": range(int(d.year.min()), int(d.year.max())+1)});
  d = grid.merge(d, on="year", how="left")`, then `ax.plot(d.year, d.value,
  ...)`. No-op for the other four sources (Eurostat, Maddison, PWT, World Bank
  have no gaps, confirmed), fixes Tica.

## Minor

None found. Specifically checked and clean:

- **Palette.** Extracted the full pixel-color set of all seven PNGs
  programmatically and matched every distinct color against the ten
  `PAPER/INK/MUTED/HAIR/ACCENT/RISE/FALL/SURFACE/AMBER/PURPLE` hex values
  defined at the top of `gdp_charts.py`. Every non-anti-aliased pixel across
  all seven figures lands on an exact palette hex (distance ≈ 0). No
  hardcoded or off-palette color anywhere. `PURPLE` is defined but unused,
  not a violation.
- **-12,3% label (gdp_2).** Cropped and zoomed the "Slom devedesetih" bar
  label. Fully visible, clear margin to the figure's left edge, not clipped.
- **gdp_2 six bars.** Labels and order match `gdp_growth_bars.csv` exactly:
  Uspon socijalizma (1952-1980, +6,1%), Zastoj 1980-ih (1980-1990, -0,9%),
  Slom devedesetih (1990-1993, -12,3%), Oporavak (1993-2008, +5,0%),
  Letargija (2008-2014, -1,4%), Novije (2014-2025, +4,0%). All value labels
  spell plus/minus and use comma decimals via `pct_hr()`. Bars start at zero
  (`ax.barh` with no `left=`, `axvline(0)` as the zero spine).
  Baseline not truncated.
- **War gaps, hero and prewar zoom.** `gdp_1_long_index.png` and
  `gdp_3_zoom_prewar.png` both show real breaks at 1914-1919 and 1940-1946
  (grey `axvspan` bands, line and ribbon genuinely absent inside them, not
  just visually thin). Confirmed against `annual_grid()`/`ribbon_grid()`
  building a complete year index so `NaN` breaks the fill/line at those
  years, and against `gdp_long.csv`/`gdp_ribbon.csv` themselves, which have
  no rows for those years.
- **Dual axes.** No `twinx`/secondary axis anywhere in `gdp_charts.py`.
- **Merged levels.** `gdp_7`'s cross-source comparison uses free-y small
  multiples (`save`-style facet, one panel per source, y-tick labels hidden
  on purpose since units differ), not a merged-level overlay. The main
  spliced index (gdp_1, gdp_4, gdp_5, gdp_6) is chained by growth rates per
  the post's own Napomene, not merged raw levels.
- **Titles.** All seven state a finding, not a variable name (checked each
  against its `titles()` call and the surrounding prose paragraph).
- **Source captions.** Present and specific on all seven, non-generic.
- **Provenance.** Every plotted series traces to a `table()` read from
  `outputs/tables/*.csv`; no value is hardcoded in `gdp_charts.py` beyond
  presentational choices (axis limits, band year cutoffs mirroring the
  prose's own era definitions, offsets).
- **Caption-to-figure match, the other six.** gdp_1, gdp_2, gdp_3, gdp_5,
  gdp_6, gdp_7 captions all describe exactly what their figure shows (spans,
  band names, source lists cross-checked line by line). Only gdp_4 (above)
  mismatches.

## Not this agent's job, flagged for awareness only

- `outputs/tables/gdp_growth_bars.csv` arithmetic (CAGRs, era cut choice) is
  a number-checker concern, not re-audited here; the chart traces to it
  faithfully, which is what this pass checks.
