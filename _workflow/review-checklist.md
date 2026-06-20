# Review checklist

The shared bar a post clears before it ships. Either tool runs it. Claude wraps it in the `style-critic` agent. Codex runs it by reading this file, or as a skill in `.agents/skills/`. Same standard, whoever writes the post.

Run it as a read only pass. Produce a report grouped by severity. Do not edit while reviewing.

## Voice and writing

- The number leads. Prose is punchy and present tense, not limp report prose.
- Headlines come in two beats. A hook, then a literal subtitle that gives a skimmer the finding.
- Every section header states a claim that stands on its own.
- Change is shown with an arrow. Numbers are rounded for memory. Magnitude sits in parentheses, plus and minus spelled out.
- Winners and losers framing appears where the data invites it.
- Punctuation follows the house. Flag every colon, long dash, and quote mark in prose.
- No AI tells. No hedging, no throat clearing, no vague attribution, no adjective standing in for a number.

## Numbers and provenance

- Every figure in the post traces to a saved output under `outputs/`.
- No number is typed from memory or carried over from an old draft.
- If a script changed since the post was written, the numbers it feeds are stale. Rerun and recheck.
- Untrusted columns are absent. No revenue, profit, or debt until confirmed.

## Editorial and method

- Every [KUT] marker is present where interpretation is needed, and none is filled silently. Flag each to the author.
- The method box is present and honest. Source, table, columns, and scripts in backticks. A plain caution about limits.

## Severity

- **Critical.** A number with no source, a filled or missing [KUT], a missing method box, an untrusted column used.
- **Major.** A limp lede, a topic header that states no finding, stacked dashes, an AI tell.
- **Minor.** A rounding slip, a phrase that could be tighter.

For each finding give the location, the problem in one line, and a concrete rewrite the author can paste.
