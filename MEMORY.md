# MEMORY.md. Shared learnings

Corrections and facts that must not be relearned. Both tools read this before they write or review. Append, do not rewrite history. Keep it under a few hundred lines and prune stale lines when it gets noisy.

Format for a correction. [LEARN:category] what was wrong → what is right, with the file or moment that taught it.

## Facts that do not change

- The stack is R for analysis, Quarto for posts, git for everything.
- The GFI base is FINA annual reports, table `db_afs`, one row per firm and year.
- Trusted columns today are `employeecounteop` and `nacerev21`. Financial columns are not.

## Data quirks

- [LEARN:data] A rising firm count in `db_afs` partly reflects wider coverage of the base, not real growth → say coverage, not growth, unless you can separate the two.
- [LEARN:data] Employee counts are end of period headcounts and more robust than firm counts → lead with employment when the two disagree.

## Corrections log

- [LEARN:style] (seed example) A long dash slipped into a method box → the house uses periods, arrows, and parentheses, never long dashes.
- [add corrections here as they happen, newest at the bottom]

## Workflow learnings

- [add reusable fixes here. If one is a multi step procedure, capture it as a skill instead of a line]
