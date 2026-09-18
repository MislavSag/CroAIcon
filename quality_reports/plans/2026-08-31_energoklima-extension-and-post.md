# EnergoKlima extension and CroAIcon post

## Objective

Extend the EnergoKlima media corpus from 2025-03-31 through 2025-06-30, validate the merged corpus and all downstream layers, then publish a reproducible CroAIcon analytical draft comparing the media picture of Croatian energy with physical-sector and GFI evidence.

## Scope

- Source archive remains read-only: `C:/Users/lsikic/Luka C/Determ_mediaspace_full`.
- New source interval: 91 daily workbooks, 2025-04-01 through 2025-06-30.
- Existing EnergoKlima corpus is extended additively. The merge keeps its automatic timestamped backup.
- Primary post comparison window is 2021-2023, where the media collection regime is stable and the EIZ/GFI benchmark aligns. April 2024-June 2025 is shown only as a separately marked continuation.
- Main GFI universe is NKD section D / division 35. INA and C19 remain a separate fossil benchmark rather than being pooled into one sector margin.

## Implementation

1. Make extension provenance derive its range and file count from the actual source artefacts; update stale date descriptions after a successful run.
2. Run the resumable extension build. Stage A should process only the 91 new days; stages B and C rebuild full-drop denominators and deduplicated extension artefacts.
3. Dry-run, then apply the additive merge. Extend outlet mappings, rebuild platform counts and population views, rematch entities, rebuild tone/report/observatory payloads, and run the full corpus validator.
4. Export post-specific media tables from `energoklima_corpus.duckdb` using `population`, never a blind sum over `denominators`.
5. Reproduce the 2023 EIZ company benchmark before extending GFI results. Resolve financial labels from `codes_gfi_db_afs_physical`; use `b145` total revenue, `b147` pre-tax result, `b151` net result, and `employeecounteop`. Account explicitly for the absent HEP 2022 row.
6. Build a small set of one-point charts in CroAIcon house style and write a Croatian Quarto post with one argument: media move at the speed of crises and promises, while the physical and financial energy system moves at the speed of infrastructure and incumbents.
7. Run number checks, inspect every chart, render the post, and report remaining evidence limits.

## Planned analytical modules

1. Energy attention and the 2022 crisis peak.
2. The shift from prices/LNG toward solar, grids, renovation and electromobility.
3. Renewable headline versus legacy composition: hydro, biomass, transport and solar.
4. Company revenue/ownership versus media visibility.
5. A short 2024-2025 continuation, broken at collection-instrument seams.

## Gates

- No raw document count is used as a time trend across a collection seam.
- Category comparisons are descriptive attention measures, not claims that reporting is false.
- Tone or blame claims stay out unless classifier evidence supports them.
- Company visibility uses mutually exclusive ownership unions for the headline; it does not double-count HEP and subsidiaries.
- Every post number traces to a generated file under `outputs/`.
- The task is complete only after the corpus validator passes, charts are visually inspected, and Quarto renders successfully.
