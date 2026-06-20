# Quality gates

The score a post earns and the bar it must clear. Both tools apply this. The checks live in `_workflow/review-checklist.md`. This file turns those checks into a number.

## Thresholds

- **80.** Safe to commit. Below this, fix before committing.
- **90.** Ready to publish.
- **95.** The aspiration. Rare and earned.

## How the score is built

Start at 100. Subtract for issues found against the review checklist.

| Issue | Deduction |
|-------|-----------|
| A number with no source in `outputs/` | 25 |
| An untrusted column used (revenue, profit, debt) | 25 |
| A [KUT] filled silently, or a needed one missing | 20 |
| Missing method box | 20 |
| A headline that hides the finding | 10 |
| A section header that states no claim | 8 |
| Long dashes, colons, or quote marks in prose | 5 |
| An AI tell, such as hedging or vague attribution | 5 |
| A number not rounded for memory | 3 |
| A phrase that could be tighter | 1 |

A single critical issue can drop a post below 80 on its own. That is the point. A wrong or unsourced number is not a rounding error on the score.

## The idea gate

A brainstormed idea enters the backlog as buildable only if it clears all five tests in `_workflow/idea-playbook.md`. An idea that fails any test is parked or dropped, with the reason logged.

## Where the gate runs

`/qa-post` applies this rubric and returns a score and a verdict. `/commit` reads that verdict and holds the commit when the score is under 80 or a critical issue stands.
