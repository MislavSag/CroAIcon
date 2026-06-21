---
name: chart
description: Pick the right chart for a finding, build it in house style, and hand it to review. Reasons from dataviz first principles and the house chart system, then calls an existing save_*_chart or scaffolds a new one. Use when you have a result and need to show it, or are unsure which chart fits.
argument-hint: "[a finding, a data file under outputs/, or a post path]"
---
# Chart helper

You turn a finding into the right figure. You advise on the chart type, you build it in house style, and you can hand the result to the `chart-critic` for review. You never invent generic ggplot. You reason from `_workflow/chart-playbook.md` and route into the house chart system in `R/house_style.R`, `R/charts.R`, and the Python chart scripts.

## Steps

1. **Read the ground.** `_workflow/chart-playbook.md` for the decision rules and the house look, `MEMORY.md` for data quirks, and the finding, data file, or post in play. If a data file is named, read its columns and shape first.
2. **Diagnose.** Name the one point the chart must make and the shape of the data, one series over time, many categories, two variables, or a spread of estimates. One chart, one point. If there are two points, say so and split.
3. **Advise.** Recommend the chart type with the encoding reason from Cleveland's hierarchy, why this channel carries the finding. Name one runner-up and why it loses, most often *not dual-axis, it implies a correlation the data does not claim*. Flag any trap the data invites.
4. **Build.** Numbers come from `outputs/` only, never hardcoded. If an existing `save_*_chart` fits, call it. Else scaffold a new builder in `R/charts.R` or the Python mirror that uses `house_pal` and `theme_house`, a finding-stating title, a source caption, and arrows in any annotation. One builder, one chart type.
5. **Render.** Run the script, write the preview PNG to the post folder or `outputs/`, and report the path. Verify it rendered. Never claim a chart from memory.
6. **Offer review.** Offer a `chart-critic` pass on the figure, and run it if asked.

Any [KUT] in the framing stays human. Surface it, never bake an interpretation into the chart silently.

The palette and theme live in one place each and are mirrored across R, Python, and the SCSS by hand. If you touch a palette value, say so, the others must move with it.

Quality over polish. The right chart plain beats the wrong chart pretty.
