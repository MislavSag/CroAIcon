# Plan. The AI layer's second aspect — narrative consistency

**Status. Done (2026-06-21).** All seven files edited and cross-checked. No skill files
touched, so `sync-skills.sh` was not run; Codex picks up the doc changes directly.

## Context

The AI layer today guarantees one thing: **form consistency**. Two authors on two tools
produce posts that look and read identically, because voice, look, charts, numbers, and
ideas each have an owner in the repo (`house-style-guide.md`, `styles.scss`,
`chart-playbook.md`, `number-checker`, `idea-playbook.md`). That is the whole thesis of
`how-it-works.md`: "the posts come out identical."

What the layer does **not** guarantee is that a single post holds together as a piece of
writing. Nothing surfaces narrative coherence as its own aspect. The closest thing is one
buried line in the `editor` agent ("The arc. Do the sections build to the central
finding"), and there is a real gap at the end: the house closes every post on the
`## Napomene` reference box, and **no document describes an interesting payoff close**.

This plan adds the layer's **second aspect: narrative consistency** — a post opens with a
hook, builds its one argument through charts, numbers, and prose that stay consistent with
the story, and lands a payoff before the notes box. Per the chosen approach it is built
**lean**: extend the existing `editor` (the "meaning" owner) rather than add a new
agent/doc, and put the enforceable bar in the shared `_workflow/` docs so Codex picks it
up by reading them directly.

## The three beats (one definition, used verbatim across every file)

1. **Hook.** The open grabs and orients — opener, bridge, two-beat headline already cover
   this; the arc check just confirms the hook lands and is not flat.
2. **Build.** Every section, chart, and number advances the *one* central finding and stays
   consistent with it. The evidence escalates toward the central `[KUT]`. Nothing wanders,
   nothing contradicts the story, no section fails to move it forward.
3. **Payoff.** The post lands a closing insight — a sharp "so what" that resolves the
   central `[KUT]` or opens one forward line. A punch, not a summary, not a hedge. It is
   the last thing the reader holds **in the body**, distinct from the `## Napomene` box,
   which stays the reference footer after it.

Internal review docs use the English labels Hook / Build / Payoff (matching the existing
"The lede" / "The arc" style). The house-style guide and template stay in the Croatian
voice.

## Files to change

**1. `.claude/agents/editor.md` (Claude-only wrapper; the meaning owner).**
Reframe so the editor explicitly owns the arc as the layer's second aspect. Keep "The
lede" and "The honesty"; replace the single "The arc" line with the three beats:
- **The hook** — does the open land, or is it flat. (Ties to the existing lede check.)
- **The build** — do the sections, charts, and numbers build on the one finding and stay
  consistent, or does a section wander / contradict the story.
- **The payoff** — does the post close on an interesting insight, or end flat on the data
  / straight into the notes box with nothing earned.
Add a one-line framing that the editor owns "whether the post holds together," not grammar.

**2. `_workflow/review-checklist.md` (read directly by Codex → both tools).**
- Add a new `## Narrative arc` section after `## Editorial and method`, with three bullets
  matching the three beats above.
- Extend the `## Severity` block: **Major** — the argument wanders (a section does not
  build on the central finding), or the post ends with no payoff. **Minor** — a flat hook
  or a perfunctory payoff that only restates the finding.

**3. `_workflow/quality-gates.md` (read directly by Codex → both tools).**
Add two rows to the deduction table (kept lean; the hook is already covered by the
existing "A headline that hides the finding | 10"):
- `The argument wanders — a section does not build on the central finding` → **10**
- `No payoff — the post ends on the data, not a closing insight` → **8**

**4. `_workflow/house-style-guide.md` (read directly by Codex → both tools).**
- Add a `## The close — land a payoff` subsection immediately **before** `## The notes
  box`: the body's last move is a payoff that resolves the central `[KUT]` or lands one
  forward line — a punch, one or two sentences, never a summary or a hedge, distinct from
  the notes box.
- Reconcile the opening of `## The notes box` ("Close every post with the notes box") so it
  reads as the reference footer that follows the payoff, not the post's last idea.
- Add one line under `## Headers that carry the story` on build consistency: every section
  advances the one finding; stacked headers should read as one escalating argument.
- Add a `Payoff close` item to the `## Before you publish` checklist.

**5. `posts/_template.qmd` (read directly by both tools).**
Insert a bracketed payoff placeholder between `[KUT — glavna interpretacija]` and
`## Napomene`, e.g.:
`[Payoff. The closing punch. Resolve the central [KUT] into a sharp "so what" or land one
forward line. Not a summary. The last thing the reader holds before the notes.]`

**6. `_workflow/how-it-works.md` (the map; the file that prompted this).**
- In the intro, tie the two aspects together: the layer does two jobs — makes posts uniform
  in form **and** makes each one hold together as an argument.
- Add a short section (e.g. `## The second aspect — a post that holds together`) after
  `## How a post is styled — three layers`, naming Hook → Build → Payoff and pointing to
  where the bar lives (the `Narrative arc` checklist section, the house-style close
  guidance, the `editor` agent).
- Add a `Narrative arc / payoff close` row to the `## Where things live` table →
  `_workflow/review-checklist.md`, `_workflow/house-style-guide.md`.

**7. `AGENTS.md` (the shared brain; read by both tools).**
Add one bullet to "Writing a post, the short rules": the post is one argument — a hook, a
build where every section, chart, and number advances the one finding and stays consistent
with it, and a payoff close that lands a "so what" before the notes box. Lightly reconcile
the existing "Close every post with the notes box" bullet so the body closes on the payoff
and the notes box is the reference footer.

## Intentionally **not** changed

- **No new agent, no new `_workflow/` doc** — the lean choice; narrative shares the
  "meaning" owner (`editor`) and rides the existing checklist/gates.
- **No skill files** — so `scripts/sync-skills.sh` does **not** need to run. `qa-post`
  already runs the `editor` on Claude and the checklist top-to-bottom on Codex, so it
  carries the new dimension with no edit.
- **No `/commit` wiring** — that skill does not exist yet (aspirational in
  `quality-gates.md`); out of scope.

## Verification

These are docs, one agent prompt, and a template — no code to run. Verify by consistency:

1. **One definition everywhere.** Re-read all seven files and confirm Hook / Build /
   Payoff are described the same way, with no contradictions.
2. **Close rule reconciled.** Confirm `house-style-guide.md`, `AGENTS.md`, and the template
   all agree: the body lands a payoff, the `## Napomene` box is the reference footer after
   it. No file still implies the notes box is the post's last idea.
3. **Gate/checklist alignment.** Confirm every new checklist Severity line has a matching
   deduction row in `quality-gates.md`, and the point values are sane against neighbours.
4. **Dry run the rubric.** Walk the new `Narrative arc` checks against the
   `posts/_template.qmd` skeleton (the only post-shaped artifact today) to confirm they are
   answerable as written. Optional: `quarto render posts/_template.qmd` only to confirm the
   added placeholder does not break the build (it is `draft: true`).
