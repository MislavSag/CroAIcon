# Integration notes

This workflow layer drops onto an existing Quarto, R, and Python site. It adds files and a couple of folders. It does not touch your posts, data, scripts, or site config, except for the three manual merges at the end.

## What the overlay added

- `AGENTS.md`, `CLAUDE.md`, `MEMORY.md` at the root. The shared brain, the Claude adapter, the corrections log.
- `_workflow/`. The style guide, review checklist, idea playbook, quality gates, ideas backlog, and a data provenance template. The underscore keeps Quarto from rendering them.
- `.claude/agents/`, `.claude/skills/`, `.claude/rules/plan-first.md`, and `.claude/settings.example.json`.
- `.agents/skills/`, the Codex copy of the skills.
- `scripts/sync-skills.sh`.
- `posts/_template.qmd`. The underscore keeps it out of the rendered site.
- `quality_reports/`. Where review reports, plans, and logs are written.

## How it maps to your folders

| Your folder | Role in the workflow |
|-------------|----------------------|
| `posts/` | Published Quarto posts. |
| `drafts/` | Approved analytical drafts, the input a post is written from. |
| `outputs/` | Tables and figures the scripts write and the posts read. The anchored numbers live here. |
| `R/`, `python/` | The two analysis languages. Both write to `outputs/`. |
| `editorial/` | Your editorial space. The workflow leaves it to you. |
| `research/` | Exploration and sandbox work. |
| `prompts/` | Your own prompt snippets. |
| `assets/`, `Design/` | Site and design assets. |

## Three manual merges

The overlay does not overwrite files you already have. Do these three by hand.

### 1. Settings

Merge `.claude/settings.example.json` into your `.claude/settings.json`. If you do not have one, rename the example.

### 2. gitignore

Append these lines to your `.gitignore`.

```
# Workflow layer, keep local only files out
.claude/settings.local.json
.claude/state/personal-memory.md
AGENTS.override.md
```

Also confirm your `.gitignore` already keeps `.env`, `_site/`, and `.quarto/` out. Use `env.example` as the shared template, never the real `.env`.

### 3. Quarto render

Root markdown files render into the published site by default, so `AGENTS.md` would become a page. Add a render scope under the `project:` key in `_quarto.yml`.

```
project:
  render:
    - "**/*.qmd"
    - "!AGENTS.md"
    - "!CLAUDE.md"
    - "!MEMORY.md"
```

If any of your pages are `.md` rather than `.qmd`, add `"**/*.md"` above the three negations. After a render, confirm `_site` has no `AGENTS.html`.
