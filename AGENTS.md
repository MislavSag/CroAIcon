# AGENTS.md. CroAIcon analytical blog

This is the shared brain for the blog. Codex reads it from the repo root. Claude Code reads it through a one line import in `CLAUDE.md`. It sits on top of an existing Quarto site, so it governs how we work, not how the site is built.

**Project.** AI.econ. A reproducible analytics blog built on Croatian economic data.
**Mission.** Cut the distance from data to insight. Posts are short, purposeful, atractive and reproducible. Aimed to general public, even though hard core economics in the background.
**Stack.** R and Python for analysis and charts. Quarto for the site and the posts. Git for everything.
**Authors.** [Luka Sikic] on Claude Code. Mislav Sagovac on Codex.

**New here?** Read `_workflow/how-it-works.md` first. It maps the whole machine in one page. How a post gets its voice, its look, and its charts, how content flows from a topic to a published post, and how the two tools share one brain.

## Core principles

1. **Plan first.** Think before editing on any task that touches more than one file or changes an analysis. Save the plan under `quality_reports/plans/`.
2. **Verify after.** Rerun the scripts and render the post before reporting a task done. Never claim done from memory.
3. **Numbers are anchored.** Every figure in a post traces to a saved output under `outputs/`. A number is never typed from an old draft.
4. **House style is law.** Posts follow the style guide. Punchy and present tense. Periods over colons, arrows over long dashes, italics over quote marks. Full guide in `_workflow/house-style-guide.md`.
5. **[KUT] stays human.** Markers tagged [KUT] hold the editorial angle. Draft around them, never fill one silently, flag every one back to the author. Add max 3 of the best possible ones for a human to decide 
6. **Learn once.** Read `MEMORY.md` before you write or review. When the author corrects you, capture it with the `learn` skill so it never repeats.

## Writing a post, the short rules

- A draft is written up from `drafts/`. The finished post lands in `posts/`.
- Open with an opener and a bridge. The opener orients the reader on the subject, a question is one device among many. The bridge invites them in, reach for the hortative (*Odgovorimo*) over the flat *Ovaj post gleda*, and names the promise the body keeps. Connect the opening up to the subtitle and down to the first number.
- Headlines come in two beats. A vivid hook, then a literal subtitle that hands a skimmer the finding. Leave `description` empty when it would only echo them.
- Section headers are claims that stand on their own.
- Coin a phrase only when it explains itself. If the reader has to decode it, say the thing plainly.
- Show change with an arrow. 65.000 → 162.000. Round so the number sticks. Magnitude in parentheses, plus and minus spelled out. Put change in bold.
- Sort the world into winners and losers when the data invites it.
- A post is one argument. A hook that opens, a build where every section, chart, and number advances the one finding and stays consistent with it, and a payoff that lands a *so what* before the notes box. Cut any section that does not move the story. Take care that there are narative bridges between sections of the post. 
- After the payoff, the notes box closes the page, heading *## Napomene*, kept lean. Source, the columns the post used, scripts in backticks, and a plain caution about limits. Leave out internal schema detail and cautions about columns the post never touched.
- The body and the notes box do not repeat each other. The span, the column definitions, and the full coverage caveat live once, in the notes box. The body points to a limit subtly rather than restating it (*...broj firmi je rastao (više o obuhvatu u Napomenama), a zaposlenost padala.*). The coverage caveat still gets flagged, in the box. No repetition means no full caveat in two places, not no flag at all.
- The full writing bar and the full review bar live in `_workflow/house-style-guide.md` and `_workflow/review-checklist.md`. Read the checklist before you call a post done.

## Data and reproducibility

- Name the source, the table, and the exact columns in every post. The sectors work uses the GFI base, table `db_afs`, from FINA annual reports.
- For GFI financial columns in `db_afs`, do not use `codes_gfi` as the physical `bNNN` map. Use MySQL table `codes_gfi_db_afs_physical`, imported from `D:/data/poslovni_subjekti/sifrarnik/sifrarnici/financije_sifrarnik.xlsx`, sheet `cb_afs`.
- Keep untrusted columns out of posts. Financial columns (revenue, profit, debt) need the physical codebook and an analysis-specific audit before use.
- Separate a real change in the world from wider coverage of the base. A rising firm count can be coverage, not growth. Say which, or say you cannot tell yet.
- Reproduce someone else's headline number before extending it. Match first, build second.

## Analysis conventions, R and Python

- `set.seed()` in R, a fixed seed in Python, once at the top. Load libraries at the top. Paths relative to the repo root.
- One script, one job. Reading, cleaning, modelling, and charting hand off through saved outputs.
- Numbers that land in a post are written to `outputs/` as csv or figures, in R or in Python. Posts read those files. A post never hardcodes a number a script produced.
- One chart, one point. The title states the finding. One house palette, sourced from one place. The full chart bar, which chart fits which message and the house look, lives in `_workflow/chart-playbook.md`.

## Ideas, memory, and review

The system is built to get better with use. Four shared files carry that.

- `_workflow/idea-playbook.md` is the bar a post idea must clear.
- `_workflow/ideas-backlog.md` is the running memory of candidate, parked, and published ideas.
- `MEMORY.md` is the log of corrections and data quirks that must never be relearned.
- `_workflow/quality-gates.md` is the scoring rubric and the thresholds.

The skills that drive them, all in shared SKILL.md form, are `brainstorm`, `find-angle`, `chart`, `learn`, and `qa-post`. On the Claude side they call dedicated agents in `.claude/agents/`. On the Codex side they run from `.agents/skills/` against the same docs.

## Folder map

| Path | Holds |
|------|-------|
| `posts/` | Published Quarto posts |
| `drafts/` | Approved analytical drafts, written up into posts |
| `outputs/` | Tables and figures the scripts write and posts read |
| `R/`, `python/` | The two analysis pipelines |
| `data/` | Source data and provenance notes. Raw is gitignored |
| `_workflow/` | Style guide, review checklist, chart playbook, idea playbook, quality gates, ideas backlog, provenance template |
| `MEMORY.md` | Corrections and learnings, read every session |
| `editorial/`, `research/`, `prompts/` | Your editorial space, exploration, and prompt snippets |
| `.claude/skills/` | Skills, canonical. Codex reads the same set from `.agents/skills/` |
| `quality_reports/` | Review reports, plans, and logs |

## Commands

| Command | Does |
|---------|------|
| `quarto render posts/<slug>` | Build a post to HTML |
| `quarto preview` | Live preview while editing |
| `Rscript R/<script>.R` | Run an R script |
| `python python/<script>.py` | Run a Python script |
| `/brainstorm` | Generate and rank post ideas from the data |
| `/find-angle` | Surface and test [KUT] angles for a finding |
| `/chart` | Recommend the right chart for a finding and build it in house style |
| `/qa-post` | Score a post against the quality gate |
| `/learn` | Capture a correction or a discovery |

## Quality gates (advisory)

80 to commit, 90 to publish, 95 is the aspiration. Below 80 means fix first. The full rubric and what each issue costs are in `_workflow/quality-gates.md`. `/qa-post` applies it and returns a score and a verdict.

## Current state

- **Sectors post** (firms grow, jobs move, 2002 to 2024). Draft for the editorial pass. GFI `db_afs`, reliable columns only. Build scripts in `python/`.
- **GFI financial columns.** Physical `db_afs.bNNN` labels are in MySQL table `codes_gfi_db_afs_physical`. Use that table, not `codes_gfi`, and still audit each ratio before publishing.
- [add posts and datasets here as they land]

## Per tool harness

The shared brain is this file plus `_workflow/` and `MEMORY.md`. Each tool wraps it differently.

- **Claude Code** reads `CLAUDE.md`, which imports this file and `MEMORY.md`, and runs the agents in `.claude/agents/`.
- **Codex** reads this file directly. It reads the skills from `.agents/skills/`, kept in sync with the canonical copies in `.claude/skills/` by `scripts/sync-skills.sh`.
- **Settings.** Start from `.claude/settings.example.json` and merge it into your own `.claude/settings.json`. Personal settings stay out of git, in `.claude/settings.local.json` for Claude and `~/.codex/AGENTS.md` or `AGENTS.override.md` for Codex.
