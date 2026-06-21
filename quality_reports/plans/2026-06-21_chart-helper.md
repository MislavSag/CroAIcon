# Plan. Chart helper (skill + backing agent)

**Status.** Done, 2026-06-21. All three pieces built and wired, `/chart` mirrored to `.agents/skills/`.

**Date.** 2026-06-21
**Goal.** A dataviz brain for the blog that picks the right chart for the purpose, builds it in house style, and reviews existing figures. Scope chosen by author: **advise + build + review**, as a **skill + backing agent**.

## Why this shape

The project pattern is fixed: a **skill** is the thing you invoke (`/brainstorm`, `/qa-post`); an **agent** is a read-only specialist a skill calls (`style-critic`, `number-checker`). The dataviz *knowledge* has to live in a shared `_workflow/` doc so Codex gets it too (same reason `style-critic` reads `review-checklist.md` and `brainstorm` reads `idea-playbook.md`). So the build is three things plus wiring:

1. A shared knowledge doc (the bar + the decision rules).
2. A `/chart` skill (advise + build) that reads it.
3. A `chart-critic` agent (review) that reads it, called by `/chart` and `/qa-post`.

The helper never invents generic ggplot. It reasons from dataviz first principles **and** routes into the existing house system: `house_pal` + `theme_house` ([R/house_style.R](R/house_style.R)), the `save_*_chart` builders ([R/charts.R](R/charts.R)), mirrored in [python/sectors_charts.py](python/sectors_charts.py).

## Files

### New

1. **`_workflow/chart-playbook.md`** — the shared dataviz brain. Holds:
   - **Decision rules.** Message + data shape → encoding → chart type → house builder. Grounded in Cleveland's perceptual hierarchy (position on a common scale beats length beats angle beats area beats color) and the house law "one chart, one point."
   - **A decision table.** e.g. *change over time, one series* → line; *compare growth of 2+ series* → indexed line to 100 (never dual-axis); *winners vs losers across categories* → sorted horizontal bars with `rise`/`fall`; *one series across incomparable sources* → free-y facets; *reconstruction from a spread* → fan chart. Each row names the existing `save_*_chart` to reuse or "scaffold new."
   - **House visual law** (pulled from the code, stated once): palette roles (`accent` for the focal series, `rise`/`fall` for gain/loss, `muted` for context, `surface` for recession/break bands, `hair` for the baseline), `theme_house`, mono family, left-aligned bold title that states the finding, source caption, index-to-100 for comparing rates not levels, break gaps don't interpolate, no dual axes, no off-palette colors.
   - **The figure bar + severity** (the critic's checklist), mirroring `review-checklist.md`: Critical / Major / Minor for charts.

2. **`.claude/skills/chart/SKILL.md`** — `/chart`, advise + build. Steps:
   1. Read `chart-playbook.md`, `MEMORY.md`, and the finding / data / draft in play.
   2. Diagnose the message and the data shape.
   3. **Advise.** Recommend the chart type with the encoding rationale; name one runner-up and why not (e.g. "not dual-axis — implies a correlation the data doesn't claim").
   4. **Build.** If an existing `save_*_chart` fits, call it. Else scaffold a new house-styled builder in `R/charts.R` (or the python mirror) using `house_pal` / `theme_house`. Numbers come from `outputs/` only — never hardcoded.
   5. Render a preview PNG to `outputs/` and report the path.
   6. Offer a `chart-critic` pass on the result.
   - `argument-hint: "[a finding, a data file, or a post path]"`

3. **`.claude/agents/chart-critic.md`** — read-only, `tools: ["Read","Grep","Glob"]`, `model: sonnet` (match `style-critic`). Audits the figures in a post against `chart-playbook.md`: right chart for the message, on-palette, source caption present, title states the finding, no dual-axis / no merged levels / gaps not interpolated, figure traces to an `outputs/` script. Reports by severity with a concrete fix. Does not edit.

### Edited (wiring)

4. **`.claude/skills/qa-post/SKILL.md`** — step 1 runs `chart-critic` alongside `style-critic`, `editor`, `number-checker`.
5. **`_workflow/review-checklist.md`** — add a "Charts and figures" section so Codex runs the same bar.
6. **`_workflow/quality-gates.md`** — add chart rows to the deduction table (wrong chart for the message / dual-axis conflating scales = Major; off-palette or missing source caption = Minor; figure with no `outputs/` source = Critical).
7. **`AGENTS.md`** — add `/chart` to the commands table; add `chart-critic` to the agents list; add `chart-playbook.md` to the `_workflow/` folder map and the "Ideas, memory, and review" doc list.
8. **`CLAUDE.md`** (Claude notes block) — add `chart-critic` to the `/qa-post` agents line; add a one-line pointer for `/chart`.

### Codex parity

Skills are synced `.claude/skills/` → `.agents/skills/` by `scripts/sync-skills.sh`; after creating `/chart` I (or you) run that to mirror it. Agents stay Claude-only by design — Codex gets the same standard by reading `chart-playbook.md` + `review-checklist.md`, which is exactly why the knowledge lives in `_workflow/`.

## Verify

- `Rscript R/charts.R` sources clean (any new builder parses, no missing-symbol errors).
- `/chart` on a real finding (e.g. firm count vs employment) returns a recommendation, builds, and drops a preview PNG.
- `chart-critic` run on an existing post produces a severity-grouped report.
- `/qa-post` invokes the critic in its parallel run.

## Open choice

- Skill name: **`/chart`** (concrete, echoes `save_*_chart`). Alternative `/viz`. Will use `/chart` unless you say otherwise.

## Out of scope

- No rewrite of existing post figures (the critic flags; fixes are a separate pass).
- Cleaning untrusted financial columns — unchanged, still barred.
