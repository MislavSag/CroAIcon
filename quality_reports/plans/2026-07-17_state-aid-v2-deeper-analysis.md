# State-aid post V2. Deeper analysis

## Goal

Expand the published state-aid concentration post with the four analytical layers requested by Mislav, while correcting the interpretation of historical register coverage.

## Author workflow

- Apply `mislav-humanizer` after the analytical rewrite.
- Do not run `qa-post`; Mislav has disabled it by default for his posts.
- Keep reproducibility, provenance, visual inspection, and Quarto rendering as hard checks.

## Analytical layers

1. Reconcile the public-register snapshot with the Ministry of Finance official totals for 2021 to 2023.
2. Compare award counts and registered amounts by aid type in aligned panels.
3. Calculate the top-1% recipient share separately within each major aid type.
4. Compare one-year and two-year recipients in the complete 2023 to 2024 window.

## Outputs

- Add a tracked reference CSV for the Ministry's official 2021 to 2023 totals.
- Extend `python/state_aid_concentration_build.py` with aggregate-only coverage, within-type concentration, and recurrence outputs.
- Extend `R/state_aid_concentration_charts.R` with four house-style figures.
- Update the post and its frozen Quarto execution result.

## Verification

1. Re-run the build and chart scripts.
2. Confirm that all new reported numbers trace to current files under `outputs/`.
3. Inspect every new PNG for clipping, scale, source, and one-point clarity.
4. Render the post successfully without `qa-post`.
5. Reproduce a clean GitHub Pages build before deployment.
