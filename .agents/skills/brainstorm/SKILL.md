---
name: brainstorm
description: Generate a ranked batch of CroAIcon post ideas from the data we trust. Scores each against the idea playbook, drops anything already in the backlog, and appends the survivors. Use when you want new post ideas or are exploring what the data could tell.
argument-hint: "[optional theme or dataset to focus on]"
---
# Brainstorm post ideas

You run a divergent pass then a convergent pass, so the output is many ideas filtered to the few worth building.

## Steps

1. **Read the ground.** Read `_workflow/idea-playbook.md` for the bar, `_workflow/ideas-backlog.md` for what exists, `MEMORY.md` for data quirks, and `_workflow/data-provenance.md` for which columns are trusted.
2. **Diverge.** Generate at least a dozen candidate ideas grounded in the trusted columns. On the Claude side, run the `idea-generator` agent. Push for range, not safety. Cross sectors, time, regions, firm size, reversals, and surprises.
3. **Converge.** Score every candidate against the five tests. On the Claude side, run the `idea-critic` agent in a fresh context so it has no stake in the ideas. Kill anything the data cannot answer, anything already in the backlog, and anything that is a flat line rather than a finding.
4. **Shape the survivors.** For each, write the logged form from the playbook. Hook, finding with magnitude, data needed, angle, effort, verdict.
5. **Append.** Add the buildable survivors to the Buildable section of `_workflow/ideas-backlog.md`. Park the near misses with a one line reason.
6. **Report.** Present the ranked shortlist to the author, best first, each with its one line angle.

Quality over volume. Five strong ideas beat fifteen weak ones.
