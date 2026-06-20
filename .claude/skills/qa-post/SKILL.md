---
name: qa-post
description: Run the full quality pass on a post and return a score with a gate verdict. Applies the review checklist and the provenance checks, then the quality-gates rubric. Use before committing or publishing a post.
argument-hint: "[path to the post]"
---
# Quality pass on a post

A read only pass that scores the post and says whether it clears the gate.

## Steps

1. **Run the bar.** Apply every check in `_workflow/review-checklist.md`. On the Claude side, run the `style-critic` for voice, the `editor` for the angle, and the `number-checker` for provenance, together. On the Codex side, work the checklist top to bottom.
2. **Check the numbers.** For every figure in the post, confirm it traces to an output under `outputs/`, and that the output is current. Flag anything unsourced or stale.
3. **Score.** Apply the rubric in `_workflow/quality-gates.md`. Start at 100 and subtract per issue.
4. **Verdict.** State the score and the gate. Under 80 is blocked, fix first. 80 to 89 is commit only. 90 and up is publish ready.
5. **Report.** Write findings to `quality_reports/<slug>_qa.md`, grouped by severity, each with a location and a concrete fix. Lead the report with the score and the verdict.

You do not edit while reviewing. You report so the author or a fixer can act.
