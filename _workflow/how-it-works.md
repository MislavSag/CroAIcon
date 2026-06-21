# How everything works

The whole machine, from a topic to a published post, on one page. Read this first.
The operational quickstart (install, preview, deploy) lives in `README.md`. The reasons
behind the rules live in `AGENTS.md` and the rest of `_workflow/`. This is the map that
ties them together.

CroAIcon is a reproducible analytics blog on Croatian economic data. Two authors write
it, each through a different AI tool, and the posts come out identical. This page
explains why: the style, the charts, and the pipeline all live in the repo, not with
the author.

## One brain, two tools

The shared brain is three things at the repo root: `AGENTS.md` (how we work),
`_workflow/` (the style guide, checklists, playbook, gates), and `MEMORY.md` (the
corrections that must never be relearned).

Two tools read that one brain:

- **Codex** reads `AGENTS.md` directly and runs its skills from `.agents/skills/`.
- **Claude Code** reads it through a one-line import in `CLAUDE.md`, runs its skills
  from `.claude/skills/`, and those skills call dedicated subagents in `.claude/agents/`
  (`style-critic`, `editor`, `number-checker`, `chart-critic`, `idea-generator`,
  `idea-critic`).

The skills are the same on both sides. `.claude/skills/` is canonical;
`scripts/sync-skills.sh` mirrors it into `.agents/skills/`. So whoever writes, on
whichever tool, runs the same `brainstorm`, `find-angle`, `chart`, `qa-post`, and `learn`
against the same docs. Only the wrapper differs.

## How a post is styled — three layers

Styling is not something an author carries. It is baked into the repo and applied when
the site renders. There are three layers.

1. **Voice (the text).** The writing bar is `_workflow/house-style-guide.md`, summarized
   in the short rules of `AGENTS.md`. Every post starts from the skeleton in
   `posts/_template.qmd`, which bakes the voice in: punchy, present tense, periods over
   colons, arrows over dashes, italics over quote marks, numbers lead.

2. **Aesthetics (the look).** `assets/styles/styles.scss` is the entire visual identity
   — the "tihi podatkovni terminal otisnut na papiru": the Roboto Mono + Source Sans 3
   fonts, the paper/ink/accent palette, tables, the bracketed `[gfi]` category chips,
   layout. `_quarto.yml` wires that SCSS into the `cosmo` theme and also loads the
   fonts, the navbar/footer, and the Croatian UI strings. A post's `.qmd` carries
   almost no styling of its own; the look is poured on at `quarto render`. That is why a
   Codex post and a Claude post are visually identical by construction.

3. **Charts.** `R/house_style.R` holds the chart palette and the ggplot theme. The
   Python chart scripts mirror it, and both are matched to the SCSS tokens, so a chart
   sits on the page as if it were typeset with it. Which chart fits which finding, and
   the traps to avoid, live in `_workflow/chart-playbook.md`; `/chart` applies it and
   `chart-critic` reviews against it.

**The caveat.** The palette lives in three places — `assets/styles/styles.scss`,
`R/house_style.R`, and the Python chart scripts. They are kept in lockstep by hand, not
enforced. Edit one, update the others, or the "identical look" quietly drifts.

## The content pipeline (topic → published post)

The flow is the same regardless of author or tool.

1. **Idea.** `/brainstorm` ranks candidates against `_workflow/idea-playbook.md`;
   `/find-angle` pressure-tests the `[KUT]` framing. Survivors land in
   `_workflow/ideas-backlog.md`.
2. **Build.** A build script queries the data and writes tables to `outputs/`, e.g.
   `python/zagreb_profit_build.py`, `python/sectors_build.py` (R can do the same, e.g.
   the GDP work in `R/prepare_gdp.R`).
3. **Charts.** A chart script reads those tables and writes PNGs into the post folder,
   e.g. `python/zagreb_profit_charts.py`, `python/sectors_charts.py`, or `R/charts.R`.
   The PNGs are built through the house style above. `/chart` picks the right chart for
   the finding and builds it, against `_workflow/chart-playbook.md`.
4. **Author.** Write `posts/<slug>/index.qmd` from the template. Embed the PNGs. Every
   number traces to a file under `outputs/` — a number is never typed from an old draft.
5. **QA.** `/qa-post` scores the post against `_workflow/review-checklist.md` and
   `_workflow/quality-gates.md`. Gates are advisory: 80 to commit, 90 to publish.
6. **Render & ship.** `quarto render` applies the shared theme into `_site`;
   `.github/workflows/publish.yml` deploys to GitHub Pages.

There is also `python/ai_draft.py`, which turns a verified facts JSON
(`outputs/facts/*.json`) into a draft, with or without an OpenAI key. Treat it as an
optional drafting helper, not the live path — the posts on the site today are
hand-authored from build and chart outputs.

## The non-negotiables

These come from `AGENTS.md` and `MEMORY.md`. They are not optional.

- **Numbers are anchored.** Every figure traces to `outputs/`. Posts read those files.
- **`[KUT]` stays human.** Markers tagged `[KUT]` hold the editorial angle. Draft around
  them, never fill one silently, resolve or delete every one before publishing.
- **Coverage is not growth.** A rising firm count in `db_afs` partly reflects wider
  coverage of the base. Say which, or say you cannot tell yet. Lead with employment when
  firm and job counts disagree.
- **Trusted columns only.** `employeecounteop` and `nacerev21` are trusted. Financial
  columns stay out of posts until cleaned and confirmed.

## Where things live

| Concern | Canonical file |
|---------|----------------|
| How we work (the brain) | `AGENTS.md` |
| Corrections, data quirks | `MEMORY.md` |
| Writing voice | `_workflow/house-style-guide.md` |
| Review bar | `_workflow/review-checklist.md` |
| Chart bar / decision rules | `_workflow/chart-playbook.md` |
| Scoring rubric | `_workflow/quality-gates.md` |
| Idea bar / backlog | `_workflow/idea-playbook.md`, `_workflow/ideas-backlog.md` |
| Visual identity (look) | `assets/styles/styles.scss` |
| Site config, fonts, UI strings | `_quarto.yml` |
| Chart palette + theme | `R/house_style.R` (mirrored in the Python chart scripts) |
| Post skeleton | `posts/_template.qmd` |
| Skills (canonical) | `.claude/skills/`, mirrored to `.agents/skills/` by `scripts/sync-skills.sh` |
| What the overlay added, manual merges | `_workflow/INTEGRATION.md` |
