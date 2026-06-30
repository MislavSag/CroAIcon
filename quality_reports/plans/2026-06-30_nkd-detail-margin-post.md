# NKD detail margin extension

## Goal

Extend the sector margin post with more detailed NKD cuts.

## Scope

- Keep the existing aggregate sector chart.
- Add a level 2 ranking table/output.
- Add one chart for level 3 and one chart for level 4.
- Update the post and render the public site.

## Method

1. Inspect `db_afs` for available NKD detail columns and any reference tables with labels.
2. Query 2021 and 2024 revenue and net result by NKD detail levels.
3. Use the same net-margin definition as the aggregate post.
4. Apply a minimum 2024 revenue threshold at each detail level to avoid tiny categories dominating the chart.
5. Use sorted horizontal bars for level 3 and level 4 because the task is ranking categories by margin-change magnitude.

## Verification

- Rerun the build script.
- Rerun the chart script.
- Render `posts/2026-06-rast-marzi-po-sektorima`.
- Run full `quarto render`.
- Update the QA report with any remaining caveats.
