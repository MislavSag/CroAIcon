# QA. Potpora za mnoge, novac za malobrojne

**Score. 100/100 after the fix pass.**

**Verdict. Publish ready.** The post clears the 80 commit gate and the 90 publish score. Mislav authorized a public web preview on 2026-07-17. The two unresolved `[KUT]` choices remain visible in the source as HTML comments and are not shown to readers.

## Critical

None.

## Major

None.

## Minor

None after the fix pass. The figure alt text no longer hardcodes the concentration share, and the full unknown-size limitation now lives only in *Napomene*.

## Author decisions

- `[KUT]` after the concentration section. Choose whether the post asks a sharper question about criteria for large awards or stays strictly descriptive.
- `[KUT — glavna interpretacija]` before the payoff. Choose whether the final emphasis is transparency of large schemes or the distinction between beneficiary counts and amount distribution.

Neither marker was filled silently. They are correctly left to Mislav.

## Provenance check

| Post content | Current output | Result |
|---|---|---|
| Opening award counts and amounts | `outputs/facts/state_aid_concentration.json` | Pass |
| Top 1%, next 9%, bottom 90% | `outputs/tables/state_aid_concentration_groups.csv` | Pass. Shares sum to 100%; amounts sum to EUR 5,351,335,813.24. |
| Top ten, median and valid-OIB universe | `outputs/facts/state_aid_concentration.json` | Pass |
| Company-size amounts, counts and averages | `outputs/facts/state_aid_concentration.json`; `outputs/tables/state_aid_concentration_by_size.csv` | Pass. Size amounts sum to the same EUR 5,351,335,813.24. |
| Aid-type counts and amounts | `outputs/tables/state_aid_concentration_by_type.csv` | Pass. Type amounts sum to the same EUR 5,351,335,813.24. |
| Verification and excluded-warning facts | `outputs/tables/state_aid_concentration_validation.csv` | Pass |
| Concentration figure | `outputs/tables/state_aid_concentration_groups.csv`; `outputs/figures/state-aid-concentration-groups.png` | Pass |
| Company-size figure | `outputs/tables/state_aid_concentration_by_size.csv`; `outputs/figures/state-aid-concentration-size.png` | Pass |

The build and chart scripts were rerun on 2026-07-17 immediately before this review. No untrusted GFI financial columns are used. The post uses only state-aid register fields named in *Napomene*.

## Checklist summary

- Voice. Pass. Punchy Croatian analytical register; no vague attribution or unsupported causal claim.
- Headline. Pass. Hook plus literal subtitle.
- Structure. Pass. Concentration → company size → program type → forward analytical step.
- Payoff. Pass, subject to the final `[KUT]` choice.
- Notes. Pass. Source, physical table, exact columns, scripts and material limits are present.
- Charts. Pass. Common-position encodings, zero baseline for bars, generated finding titles, source captions and house palette.
- Render. Pass with `draft: false`. The current frozen execution result is suitable for the GitHub Pages build, which does not have access to the private analytical database.
