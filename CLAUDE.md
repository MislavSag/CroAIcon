@AGENTS.md
@MEMORY.md

# Claude Code notes

Everything above is imported from `AGENTS.md`, the shared brain that Codex also reads, and from `MEMORY.md`, the corrections log. The notes below apply only to Claude Code.

- The project facts, the writing bar, the data rules, and the quality rubric all live in `AGENTS.md` and `_workflow/`. Do not restate them here.
- Enter plan mode before any task that touches more than one file. Plans save to `quality_reports/plans/`.
- The agents in `.claude/agents/` are called by the skills, not by you. `style-critic`, `editor`, and `number-checker` run inside `/qa-post`. `idea-generator` and `idea-critic` run inside `/brainstorm`.
- For a quality pass run `/qa-post`. For ideas run `/brainstorm`. For framing run `/find-angle`. After any correction run `/learn`.
- Merge `.claude/settings.example.json` into `.claude/settings.json` so the permissions cover R, Python, Quarto, and git.
