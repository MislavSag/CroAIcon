---
name: learn
description: Capture a correction or a discovery so it is never relearned. A one line fix becomes a [LEARN] tag in MEMORY.md. A reusable multi-step procedure becomes a new skill. Use right after you correct the agent or solve something non-obvious.
argument-hint: "[the correction or discovery in a sentence]"
---
# Learn from this

This is how the system improves itself. A lesson that lands here changes future sessions, because both tools read `MEMORY.md` before they work.

## Steps

1. **Judge it.** Was this non-obvious, and would a future session benefit. If no, stop. Not everything is worth saving.
2. **Pick the form.**
   - A one line fix or fact → a `[LEARN:category]` tag in `MEMORY.md`, written as wrong → right, with the file or moment that taught it.
   - A repeatable multi step procedure → a new skill in `.claude/skills/<name>/SKILL.md`, with a clear description and steps.
3. **Check for duplicates.** Search `MEMORY.md` and the existing skills first. Update what is there rather than adding a near copy.
4. **Write it.** Add the tag or the skill. For a new skill, rerun `scripts/sync-skills.sh` so Codex picks it up too.
5. **Confirm.** Tell the author what was captured and where, in one line.
