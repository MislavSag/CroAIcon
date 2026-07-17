# State-aid concentration post

## Goal

Make Mislav-authored posts use `mislav-humanizer`, then build a reproducible CroAIcon post on the concentration of verified Croatian state-aid awards in 2017 to 2025.

## Skill order

1. `learn`. Record the author-specific writing rule in project memory.
2. `chart`. Choose and build figures from saved outputs in the house chart system.
3. `mislav-humanizer`. Edit the analytical draft into Mislav Sagovac's public-facing analytical voice without changing evidence or scope.
4. `qa-post`. Run a read-only score after scripts and rendering pass.

## Files and outputs

- Update `AGENTS.md`, `_workflow/how-it-works.md`, and `MEMORY.md` with the Mislav-specific writing rule.
- Add one state-aid build script under `python/` and one house-style chart script under `R/`.
- Save every reported number and every chart input under `outputs/tables/`.
- Add the post under `posts/2026-07-drzavne-potpore-koncentracija/` with figures built from those outputs.
- Add the final QA report under `quality_reports/` and update the idea status in the backlog.

## Analytical rules

- Source `odvjet12_znalac.state_aid_awards_current` or the published snapshot behind it.
- Keep awards dated 2017 to 2025, `verification_status = 'Ispravan'`, and `gross_amount_eur > 0`.
- State separately when a statistic requires a valid 11-digit recipient OIB.
- Exclude the implausible EUR 18.75bn warning record and document that decision.
- Treat concentration as descriptive. Do not infer favoritism, capture, effectiveness, or causality from the register alone.
- Distinguish award counts, recipient counts, and euro amounts throughout.
- Keep all outputs aggregate. Do not save recipient names or row-level identifiers.

## Verification

1. Re-run both Python scripts from the repository root.
2. Check that every post number traces to a current CSV under `outputs/tables/`.
3. Inspect generated PNGs and run the chart checklist.
4. Render the Quarto post successfully.
5. Apply `mislav-humanizer` without changing any number, source, or limitation.
6. Run `qa-post`, write the score, and fix any issue that blocks the 80 commit gate before reporting completion.
