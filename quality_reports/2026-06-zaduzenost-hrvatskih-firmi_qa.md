# QA. Zaduzenost hrvatskih firmi

Score: 95
Verdict: publish ready

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

- Location: `posts/2026-06-zaduzenost-hrvatskih-firmi/index.qmd`
  Problem: The notes are more technical than a typical public-facing post because they name the physical codebook table and AOP columns.
  Fix: Keep as written for this post because the article corrects a previous codebook mapping error and the provenance detail is material.

## Number Checks

- `37%`, `32%`, `50%`, `8,0%`, `6,6%`, `42%`, short-term shares, profitability-bin values, sector values, and firm counts trace to `outputs/tables/debt_structure_yearly.csv`, `outputs/tables/debt_profitability_bins.csv`, and `outputs/tables/debt_by_sector_size.csv`.
- AOP mapping traces to `outputs/tables/debt_structure_aop_map.csv`, generated from MySQL table `codes_gfi_db_afs_physical`.
- Figures trace to `outputs/figures/debt_*.png` and are copied into the post directory.

## Render And Chart Checks

- `python -m py_compile python/import_gfi_db_afs_codebook.py python/debt_structure_build.py python/debt_structure_charts.py` passed.
- `python python/debt_structure_build.py` passed validation gates and rebuilt output tables.
- `python python/debt_structure_charts.py` regenerated all four figures.
- `quarto render posts/2026-06-zaduzenost-hrvatskih-firmi` completed successfully.
- Visual check: charts are nonblank, sourced, and consistent with the post text.
