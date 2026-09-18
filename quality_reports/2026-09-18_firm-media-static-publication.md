# Firm-media publication checks

Pre-publication result: passed. Final post text reviewed against the house checklist, saved facts and the author's requested presentation. No blocking numerical, prose or layout issue remains in the reviewed files.

The atlas is five static HTML pages containing the 150 firms with the most accepted article–firm links from January 2025 through June 2026. Each page contains thirty firms, eighteen monthly counts and a total. A common colour scale and fixed order apply to all pages. Ordinary numbered links provide page navigation. There is no JavaScript, search, sorting, identifier display, clickable cell, modal, article evidence or evidence-file dependency. The public article describes this selection and no longer invites searches or opening articles from cells. The source-provider name and obsolete interactive wording are absent from public prose and chart credits.

## Validation

- Reran the facts builder, both figure builders and the five-page builder. All ten post-facts source fingerprints match saved CSVs. The public builder reconciles 2025 and H1 2026 totals against the existing facts before selecting the top 150.
- The static-page test verifies all 2,700 monthly values, all 150 totals, firm names and ranks, exactly five pages, page links and the absence of dynamic elements and evidence links. It passes on the source pages, the working preview and the clean publication build.
- Read the latest Croatian prose. Corrected the rank-change phrasing, made the subtitle's years explicit, described the five-page selection and removed the search instructions. The analytical interpretation and source event links remain supported. No editorial marker was filled or deleted.
- Rebuilt and visually inspected the figures. Inspected the first and fifth atlas pages, narrow-screen layout and final article using generated Chrome screenshots under `tmp/gfi-media-static-qa/`.
- Rendered the complete site from a clean worktree based on `origin/main` at `59b581a`. The worktree contains no local analytical fact files; Quarto successfully uses the committed execution freeze. All sixteen site pages render with exit code 0.
- Confirmed the post appears in the clean homepage, search index and RSS. Confirmed all static pages and chart resources match source hashes. The old explorer and article-evidence directory are absent from the clean output.

## Publication scope

Only this post, its four image assets, five static atlas pages, three builders, HTML template, static validation script, execution freeze, this report, plan and the relevant memory correction are included. Private CSVs, facts, full research explorers, captured article evidence and unrelated local changes remain outside the commit. The post preserves its explicitly unassigned author and is marked `draft: false`.

Publishing to the main branch and GitHub Pages is explicitly authorized by the user's instruction. Deployment and live-page results are recorded separately after the push.
