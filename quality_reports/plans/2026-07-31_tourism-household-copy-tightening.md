# Tourism post. Household split and copy tightening

## Goal

Revise `posts/2026-07-noc-bez-cijene/index.qmd` without removing any chart or analytical section.

## Scope

1. Add the official HTZ 2024 household-accommodation nights and commercial-total nights to `data/external/tourism_external.csv`.
2. Carry those inputs through `python/tourism_value_build.py` into `outputs/facts/tourism_value.json`, with a validation check on the resulting share.
3. Replace the broad claim that tourism statistics do not distinguish household accommodation with the narrower, supportable claim that the DZS object-type table cannot be matched directly to company revenue.
4. Use the direct HTZ result in the prose without naming the collection system.
5. Tighten repetition and sentence-level excess while preserving every figure and substantive analytical result.
6. Bold every quantitative finding in the body consistently. Keep years and numbers in the technical notes unbolded unless they are themselves the finding.

## Verification

1. Run `python python/tourism_value_build.py`.
2. Run `python python/tourism_value_charts.py`.
3. Confirm all validation checks pass and inspect the changed facts.
4. Scan the body for unbolded inline numerical outputs and stale claims about the household split.
5. Render with `quarto render posts/2026-07-noc-bez-cijene`.
