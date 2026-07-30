# Plan. Noć bez cijene. Turizam koji brojimo i turizam koji naplaćujemo

*Rename on execution to `quality_reports/plans/2026-07-30_noc-bez-cijene.md`.*

## Context

Croatia counts tourist nights to the decimal and never counts what they are worth. DZS publishes
arrivals, nights, beds and capacity down to the settlement, but **no price anywhere in the entire
63-table collection**. FINA GFI holds firm revenue. Nobody has put the two together.

A new DZS tourism dump landed at `C:\Users\lsikic\Documents\DZS-Turizam` (63 tables, 98 files,
2005–2026). This plan turns it plus `db_afs` into one post that answers seven questions the author
short-listed, under a single argument, in the house's short readable format.

**The argument.** We measure the biggest industry in the country with the wrong number. Count nights
and Croatia looks like a giant. Count euros per night and the map rearranges.

**Author.** Luka Šikić. `draft: true` until reviewed (per standing memory, one post live at a time).

## What the exploration settled

Four findings changed the design, all verified live against the DB this session:

| Question going in | Answer | Consequence |
|---|---|---|
| Is the join stuck at county? | **No.** `db_afs.municipalityid`, 100% coverage, 556 units, indexed. 542 of 552 DZS names match on normalised compare. | Municipality-level analysis, not 21 counties. |
| Is detailed NKD a stale snapshot? | **No.** `nacerev22/23/24` are per-firm-year at 100% coverage, 1995–2024. | Hotels (551), apartments (552), camps (553), restaurants (561), bars (563) all separable. |
| Does the head-office effect ruin coastal revenue? | **Largely no**, for accommodation. Poreč 555 M EUR is #1, Rovinj #3; Zagreb holds only 13,8% of national NKD 55. Croatian hotel groups register in their home towns. | The euro-per-night map is trustworthy for NKD 55. Restaurants (NKD 56) *are* Zagreb-heavy — real, not an artefact. |
| Can GFI measure seasonality? | **No.** `employeecounthw / employeecounteop` ≈ 1,0 for coastal hotels, same as manufacturing. `monthofoperation` = 12 for 92% of firms. | Seasonality section runs on DZS monthly data only. No estimated "true workforce" multiplier. |

Traps to code against: NKD **79 sits in section N**, not I. `codes_nkd2007.OPIS_DJEL` and
`codes_municipal.naziv` are latin2, mojibake under utf8mb4. `nacerev22/23` are unindexed, so every
query must lead with `nacerev21` + `reportyear`.

## The post

`posts/2026-07-noc-bez-cijene/index.qmd`

- **Title.** Noć bez cijene
- **Subtitle.** Hrvatska broji noćenja do zadnje znamenke. Koliko jedna noć donese, ne broji nitko. Evo brojke.
- **Target.** ~1.000 words body, 6 figures, three numbers the reader keeps. All caveats in `## Napomene`, none in the body.

Six sections, each one claim, one number, one chart. All seven short-listed questions land:

| # | Header (claim) | The number | Chart | Q |
|---|---|---|---|---|
| 1 | Jedna noć u Hrvatskoj vrijedi oko X eura | National revenue ÷ nights, 2013–2024, nominal and real | Line, two series (smještaj; smještaj + ugostiteljstvo) | Q1 |
| 2 | Ista noć, dvostruko različita cijena | Top 15 / bottom 15 municipalities, EUR per night | Sorted horizontal bars, `rise`/`fall` | Q1, Q4 |
| 3 | Većina kreveta nema firmu iza sebe | Beds per municipality vs beds backed by a filing company | Scatter or sorted bars, corporate share of beds | Q11 |
| 4 | Dva mjeseca nose cijelu godinu | July + August share of nights, by county; assets that wait out the year | Monthly curve + Jul/Aug share | Q6 |
| 5 | Hrvati su sve manji dio vlastite obale | Domestic share of nights 2005–2025, plus residents' spend abroad | Line, domestic share | Q2 |
| 6 | Vez je najskuplji kvadrat na obali | Marina revenue per berth, by coastal county | Sorted bars | Q7 |

COVID recovery (Q8) is carried as a visible feature of the section 1 and 5 time series, not its own
section. Section 2 absorbs the "where the money is booked" question (Q4) — reframed from accusation
to value map, which is what the data actually supports.

**Payoff.** Resolves to: nights are the wrong scoreboard. Croatia optimises the number it publishes.

**`## Napomene`** carries every caveat: the household-bed gap, the head-office effect, `z` vs `-`,
the NKD 56 locals problem, the seasonality blind spot in GFI employment, and the DZS coverage break.

## Scripts

Both new, Python, matching the `debt_structure_*` pattern exactly (`project_root()`, `load_env_file()`,
`connect()` copied verbatim from `python/debt_structure_build.py` lines 67–118).

### `python/tourism_value_build.py`

Reads DZS CSVs + queries `db_afs`, writes `outputs/tables/*.csv` and `outputs/facts/tourism_value.json`.

DZS inputs (all `encoding="utf-8-sig"`):
- `BS_TU11.csv` national monthly 2005–2026 → domestic/foreign split, seasonality
- `BS_TU12.csv` county monthly 2013–2026 → county nights, Jul/Aug share
- `BS_TU19.csv` municipality annual 2021–2025 → nights, beds, population
- `BS_TU18_02.csv` berths by county, `BS_TU18_11.csv` marina revenue by county
- `T11.csv` residents' travel spending

GFI queries, one per grain, each leading with `nacerev21` + `reportyear`:
- national NKD 55 and 56 revenue by year 2013–2024
- NKD 55 revenue, assets, employment by `municipalityid` × year
- marina firms by county for the DZS cross-check

Outputs: `tourism_eur_per_night_national.csv`, `_by_municipality.csv`, `tourism_beds_vs_firms.csv`,
`tourism_seasonality.csv`, `tourism_domestic_share.csv`, `tourism_marina_per_berth.csv`,
`tourism_validation.csv`.

### `python/tourism_value_charts.py`

Reads those CSVs, writes 6 PNGs to `outputs/figures/` and copies to the post folder. Palette and
`titles()` / `spines()` / `save_and_copy()` helpers copied from `python/debt_structure_charts.py`
(figsize ~8,4×4,7, dpi 170). Refuses to draw if the validation gate failed, exactly like
`audit_passed()` in `debt_structure_charts.py`.

**Dependency.** `matplotlib` is not installed in `.venv` (it is declared in `pyproject.toml` under
the `charts` extra but never installed). One `pip install matplotlib` into `.venv` is required. R is
the fallback but `Rscript` is not on PATH and `ggplot2`/`DBI` are not installed, so Python is the
lower-risk path.

## Data handling rules to code against

Non-negotiable, each one verified in the source files this session:

1. **Filter the annual total from every month dimension.** It is spelled three ways: `Ukupno`
   (BS_TU11), `UKUPNO` (BS_TU12), `01.-12.` (BS_TU13/14). Miss it and every total doubles.
2. **`z` is not zero.** `z` = confidential, `-` = true zero, `..`/`....` = not published. Parse `-`
   to 0, everything else to `NaN`. BS_TU19 is 12,6% `z`, concentrated in exactly the small
   municipalities a ranking would surface.
3. **BS_TU19 has duplicate labels.** `Otok`, `Privlaka`, `Sveta Nedelja` each name two different
   municipalities, and `Grad Zagreb` appears as three consecutive identical blocks (region, county,
   city). Reconstruct county context from row order before deduplicating; never `groupby` the label
   alone.
4. **Drop the 26 non-leaf rows in BS_TU19** (1 country + 4 NUTS-2 + 21 counties) before ranking.
   `is_aggregate` in the codebook is reliable for non-geo dimensions only — for geo it is broken
   (it flags all 22 BS_TU13 counties and all 7 marina counties as aggregates).
5. **Marina money: euro members only.** Kuna and euro run in parallel across the whole period; kuna
   is `-` after 2023. Summing the measure dimension double-counts.
6. **Municipality crosswalk.** Normalise (lowercase, strip diacritics, collapse spaces and hyphens),
   then hand-map the ~10 residuals: `buje-buie`, `ivanic grad`, `kastelir-labinci`, `malinska-dubasnica`,
   `motovun` (DZS has a typo, `Montana` for `Montona`), `murter-kornati`, `novigrad zadarski` vs
   `novigrad`, `tar vabriga`, `umag-umago`, `zlatar bistrica`, Zagreb. Store the map as a literal dict
   in the build script so it is auditable.
7. **DB charset `latin2`** for the municipality and NKD label lookups, or the names come back mojibake.
8. **Real terms.** Deflate the euro-per-night series with `price_deflator`; the 2013–2024 span
   includes both high inflation and the euro changeover.

## Validation gate

`tourism_validation.csv`, with a `go_no_go` row the chart script checks before drawing anything:

- **Reproduce DZS first.** National nights from BS_TU11 must equal the BS_TU12 national row and the
  BS_TU19 national row for the overlapping years. Match before building. If they disagree, stop.
- **Coverage.** `b110` populated for ≥85% of NKD 55 firms; municipality name match ≥98%.
- **Balance identity.** `b061 ≈ b108` on the accommodation subsample.
- **Macro anchor.** National euros per night must land in a sane band (expected ~30–40 EUR for
  accommodation alone). A wrong column or a doubled total will blow straight past it.
- **Marina cross-check.** DZS marina revenue vs GFI marina firms' revenue, reported as a ratio.
  This is the house rule — reproduce someone else's headline before extending it. If they diverge
  badly, section 6 is reported as a discrepancy or cut, not published as a berth price.

## Verification

1. `python python/tourism_value_build.py` → inspect `tourism_validation.csv`, confirm `go_no_go` passed.
2. `python python/tourism_value_charts.py` → 6 PNGs in `outputs/figures/` and the post folder.
3. Eyeball every chart against `_workflow/chart-playbook.md`: title states the finding, source
   caption present, house palette, no dual axis, bars from zero.
4. `quarto render posts/2026-07-noc-bez-cijene` → builds clean.
5. Cross-check three published DZS headline figures by hand against the computed tables.
6. Run `/qa-post` on the finished post. Gate is 80 to commit, 90 to publish.

## Risks, and what happens if they bite

| Risk | Mitigation |
|---|---|
| Nights and revenue count different populations (all beds vs only firms) | This is section 3, not a hidden flaw. The headline is stated as *revenue per night*, never as a room rate. Caveat in Napomene. |
| Section 6 marina cross-check fails | Report the discrepancy as the finding, or cut the section. ACI operates across counties from one registration and may smear it. |
| Small municipalities with few firms give unstable ratios | Minimum thresholds on firms and nights before a municipality enters the ranking. State the threshold in Napomene. |
| Post grows past the house length | Sections 5 and 6 are the cut candidates. The spine survives on 1–4. |

## Open for the author

Up to three `[KUT]` markers, left unfilled per house rule:

- Is a low euro-per-night a failure or a business model. Volume tourism is a choice, not an accident.
- Does the household bed layer explain the low price, or the housing market.
- Whether the honest read is *Croatia is cheap* or *Croatia is not paid for what it gives up*.
