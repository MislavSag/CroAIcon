# Plan. Annotate the 1949-52 Cominform dip on both GDP charts

**DONE 2026-06-22.** Both charts regenerated via Rscript and re-synced. Hero chart
carries the "Informbiro" band + "šest padova" subtitle; socialism zoom now starts at
1949 with the band and visibly dips into 1952. Post caption updated, post renders clean.

Date 2026-06-22. Script `scripts/update_gdp.R`, helper `R/charts.R` (no change needed).
Follows on from `2026-06-22_gdp-sixth-crisis.md` (text already counts six falls).

## Why

The text now names the Cominform blockade as the sixth fall, but no chart shows it.
The socialism zoom starts at 1952, after the dip. The author wants it annotated on
both the full-series hero chart and the socialism zoom, matching how the other
crises already get grey bands with labels.

## How (all in `update_gdp.R`, the band system is already data-driven)

1. **Hero chart `gdp_1_long_index` (lines 46-54).**
   - Add a band `list(from = 1949, to = 1952, label = "Informbiro")` to the `bands`
     list, in chronological position between the WWII band (1940-1946) and the
     Domovinski rat band (1991-1995).
   - Update subtitle line 46: "pet padova, pet povrataka" → "šest padova, šest
     povrataka".
   - Caption already says "sive trake = ratovi i krize", no change.

2. **Socialism zoom `gdp_4_zoom_socialism` (lines 89-92).**
   - Change the zoom window from `zoom(1952, 1986, ...)` to `zoom(1949, 1986, ...)`
     so the dip is inside the frame.
   - Add a band `list(from = 1949, to = 1952, label = "Informbiro")` alongside the
     existing 1980-1986 "zastoj" band.
   - Subtitle line 91: "1952. do 1986." → "1949. do 1986." to match the new window.
   - Title line 90 can stay; the section is still about the socialist rise.

3. No edit to `R/charts.R`. `.add_bands` already staggers labels and takes a
   one-band span. `save_gdp_zoom_chart` filters to [y0, y1], so widening the window
   pulls in 1949-1951 automatically.

## Caption / label wording

- Band label "Informbiro" (short, fits the staggered label slot). The full story
  (raskol 1948., blokada, Tica-only) stays in the prose and Napomene, not on the chart.

## Verify

- `Rscript scripts/update_gdp.R` reruns and re-syncs the post's figure copies
  (`gdp_1_long_index.png`, `gdp_4_zoom_socialism.png`) automatically (lines 156-169).
- Eyeball both PNGs: the 1949-52 band shows, the socialism zoom now starts at 1949
  and the line visibly dips into 1952 before the takeoff.
- Re-render the post and confirm figures update.
- Check the image alt-text / caption in `index.qmd` for the socialism chart still
  reads right now the window starts at 1949 (currently "1952. do 1986.").

## Risk

- Low. Pure data edits to an existing, working chart pipeline. If `Rscript` is not
  on PATH or a package is missing, the figures will not regenerate; fall back to
  reporting that and asking how to run the R pipeline.
