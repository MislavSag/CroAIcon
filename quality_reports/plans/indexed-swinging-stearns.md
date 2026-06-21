# Plan. Onboarding doc — how everything works

**Status: done (2026-06-21).** Created `_workflow/how-it-works.md`, added the pointer in `AGENTS.md`, linked it from `README.md`, genericized the hardcoded path, and reframed the AI-nacrt section. All referenced paths verified to exist; doc stays out of the rendered site.

## Context

A new collaborator (or Mislav, arriving via Codex) has no single place that explains
how the project fits together: how a post gets its **text style**, its **visual
aesthetics**, and its **charts**, how content flows from a topic to a published post,
and why the same post comes out identical whether it was written on Codex or Claude
Code. Today that knowledge is spread across `AGENTS.md`, `_workflow/`,
`assets/styles/styles.scss`, `R/house_style.R`, and `_quarto.yml`, and
[_workflow/INTEGRATION.md](../../_workflow/INTEGRATION.md) only documents *what the
overlay added*, not *how it works end to end*. [README.md](../../README.md) is an
operational quickstart in Croatian and is partly stale.

Goal. One onboarding doc that explains the whole machine, linked from the two surfaces
a newcomer actually opens (`AGENTS.md` and `README.md`), plus a surgical fix of the
stale README bits.

## Decisions (confirmed with the author)

- **Placement.** New `_workflow/how-it-works.md`, pointers from `AGENTS.md` and `README.md`.
- **Language.** English (matches `AGENTS.md` and every other `_workflow/` doc; both tools read it).
- **Stale README.** Fix it as part of this change.

## Correction to the original premise

`python/ai_draft.py` **exists and its offline flow works** — it is not broken. The real
issue is that the README frames the *AI-draft-from-facts* flow as how posts are made,
when the live pipeline is **`*_build.py` → `*_charts.py` → hand-authored `index.qmd`**
with every number anchored to `outputs/` and charts embedded as pre-built PNGs. So the
README fix is a **reframe + path fix**, not a deletion of the ai_draft section.

## Changes

### 1. New file — `_workflow/how-it-works.md` (English)

Matches the register of `house-style-guide.md` / `INTEGRATION.md`. Sections:

1. **What this is.** One paragraph. CroAIcon, two authors, two AI tools, one shared brain. Cut the distance from data to insight.
2. **One brain, two tools.** `AGENTS.md` + `_workflow/` + `MEMORY.md` is the shared brain. Codex reads `AGENTS.md` directly and runs skills from `.agents/skills/`. Claude Code reads it via the `CLAUDE.md` import and runs skills from `.claude/skills/`, which call agents in `.claude/agents/`. Skills are canonical in `.claude/skills/`, mirrored into `.agents/skills/` by `scripts/sync-skills.sh`. Same docs, same skills, same output — only the wrapper differs.
3. **How a post is styled — three layers.** The core of the doc.
   - *Voice (text).* `_workflow/house-style-guide.md` + the short rules in `AGENTS.md` + the `posts/_template.qmd` skeleton.
   - *Aesthetics (look).* `assets/styles/styles.scss` is the whole visual identity, wired into the `cosmo` theme by `_quarto.yml`; fonts and Croatian UI strings also live in `_quarto.yml`. Applied at render time, not per author.
   - *Charts.* `R/house_style.R` (palette + ggplot theme), mirrored by the Python chart scripts, matched to the SCSS tokens.
   - *Punchline + caveat.* Style lives in the repo, not with the author or the tool, so any post renders identical. The one risk: the palette is duplicated in three places (SCSS, `R/house_style.R`, the Python chart scripts) and kept in lockstep by hand — edit one, update the others.
4. **The content pipeline (topic → published post).** idea (`/brainstorm`, `/find-angle`) → build (`python/*_build.py` or R → `outputs/` tables) → charts (`python/*_charts.py` or `R/charts.R` → PNGs in the post folder) → author (`posts/<slug>/index.qmd` from the template, numbers anchored to `outputs/`) → QA (`/qa-post`, gates 80 commit / 90 publish) → render (`quarto render` → `_site` → GitHub Pages). Note `python/ai_draft.py` as an optional/experimental drafting helper, not the live path.
5. **The non-negotiables.** Numbers anchored to `outputs/`; `[KUT]` stays human; coverage ≠ growth and lead with employment (point to `MEMORY.md`); trusted columns only. Pointers, not restatement.
6. **Where things live.** Compact table mapping each concern (voice, look, charts, brain, skills, gates) to its canonical file.

### 2. `AGENTS.md` — pointer

Add one "start here" pointer near the top (after the intro lines) so a newcomer lands on the new doc first, e.g. a line directing first-time readers to `_workflow/how-it-works.md`. No other edits.

### 3. `README.md` — link + stale fixes (Croatian, to match the file)

- Add a short **"Kako sve radi"** line linking to `_workflow/how-it-works.md`.
- Genericize the hardcoded `C:\Users\Mislav\projects_r\CroAIcon` path (appears in *Brzi start* and *Otvaranje u Positronu*) to a neutral `cd CroAIcon` / "otvori folder repozitorija".
- Reframe the **AI nacrt** section: keep `ai_draft.py` as an optional helper, but state plainly that live posts are built via `*_build.py` → `*_charts.py` → hand-authored `index.qmd`, and point to `how-it-works.md` for the full flow.

## Files touched

- `_workflow/how-it-works.md` (new)
- `AGENTS.md` (one pointer line)
- `README.md` (link + path genericization + AI-nacrt reframe)

No `_quarto.yml` change needed: `_workflow/` is outside the explicit render list and the
underscore prefix double-excludes it; `README.md` is not in the render list either.

## Verification

1. Confirm every file path named in `how-it-works.md` exists (all were verified during planning: `house_style.R`, `styles.scss`, `house-style-guide.md`, `sync-skills.sh`, the `*_build.py`/`*_charts.py` scripts, etc.).
2. Check the relative links resolve from each file's location (`AGENTS.md` → `_workflow/how-it-works.md`; `README.md` → `_workflow/how-it-works.md`).
3. `quarto render` (optional, if quick) and confirm `_site/` contains no `how-it-works.html` and no `README.html` — i.e. the new doc stays out of the published site.
4. Eyeball the README diff to confirm no remaining hardcoded user path.
