# Chart playbook

The bar a figure clears, and the rule for picking it. Shared by both tools. Claude wraps the build in the `/chart` skill and the review in the `chart-critic` agent. Codex runs the same bar by reading this file. The house chart code lives in `R/house_style.R` and `R/charts.R`, mirrored in the Python chart scripts. This file says which chart to reach for and why. The code says how to draw it.

## The one rule above the rest

One chart, one point. The title states the finding, not the variable. If a chart makes two claims, it is two charts.

## Pick the encoding first, the chart second

People read some visual channels more accurately than others (Cleveland's hierarchy). Put the number that carries the finding on the most accurate channel it can sit on.

1. Position on a common scale, a shared axis. Most accurate. Line, scatter, dot plot, bar from a common baseline.
2. Position on non-aligned scales. Small multiples, facets.
3. Length. Bars.
4. Angle and slope. A slope chart for a two-point change.
5. Area. Bubble, treemap. Use sparingly.
6. Color hue and saturation. Categories and heat. Least accurate for magnitude, never the sole carrier of the finding.

Rule of thumb. If the reader has to compare magnitudes, give them a common position axis. Drop to area or color only when position is spent.

## Message to chart, the decision table

| The point you are making | Reach for | House builder |
|--------------------------|-----------|---------------|
| Change over time, one series | Line | `save_line_chart`, or `save_gdp_index_chart` for an index |
| Compare the path of 2+ series in different units | Index each to 100 at a common base year, one line each | scaffold. Never dual-axis |
| One series across sources that share no unit or base | Small multiples, free-y facets, one panel per source | `save_facet_chart`, `save_gdp_panels_chart` |
| Rank categories, winners and losers | Sorted horizontal bars, `rise` and `fall` color | scaffold |
| A two-point change across many categories | Slope chart | scaffold |
| A reconstruction resting on a spread of estimates | Fan, muted variants and one bold chosen line | `save_gdp_fan_chart` |
| Relationship between two variables | Scatter, the focal point in `accent` | scaffold |
| Composition that sums to a meaningful whole | Stacked area, else small multiples | scaffold |
| Distribution | Histogram or a strip of dots | scaffold |
| A single number in context | Often no chart. State it in the prose | none |

When a row says scaffold, write a new builder in `R/charts.R` or the Python mirror that uses `house_pal` and `theme_house`. Do not hand-roll a one-off theme.

## The traps, banned unless argued

- **Dual y-axes.** Two scales on one frame imply a correlation the data does not claim. Index both to 100 and use one axis.
- **Merged levels from incomparable sources.** Facet with free y instead, one panel per source.
- **Interpolating across a real gap.** A missing year breaks the line. Do not draw through it (the war years missing in Tica break the GDP line on purpose).
- **A pie past two slices, or any 3D.** Bars rank better.
- **A truncated bar baseline.** Bars start at zero. A line may start where the data is.
- **Color as the only magnitude channel.** Encode the finding on position. Reserve color for category or for rise and fall.
- **A rainbow palette.** The house has a palette. Stay in it.

## The house look, the law from the code

The palette and the theme live in one place each, `house_pal` and `theme_house` in `R/house_style.R`, mirrored in the Python chart scripts and matched to `assets/styles/styles.scss`. Never hardcode a hex in a chart. Pull the role.

- `accent`. The focal series, the one the finding is about.
- `rise` and `fall`. Gain and loss. Winners and losers.
- `muted`. Context series, the lines that are not the point.
- `surface`. Recession and structural-break bands behind the data.
- `hair`. The baseline and the y-grid. Faint.
- `ink`. Title and labels.
- For multi-series, cycle `house_series` in order.

Title left-aligned and bold, stating the finding. Subtitle muted, the unit or the span. Source caption at the foot, muted. Monospace family. No top or right spine, no ticks, hairline y-grid only. Arrows for change in any annotation (65.000 → 162.000), magnitude in parentheses, plus and minus spelled out, same as the prose.

The chart's caption in the post says plainly what the reader sees. *Indeks (2008. = 100). Broj firmi i ukupan broj zaposlenih.*

## Provenance

A chart is a number too. Its data traces to a file under `outputs/`, written by a build script. The chart script reads that file. It never hardcodes the series. If the build changed since the chart was drawn, the chart is stale. Rebuild it. Untrusted columns (revenue, profit, debt) stay off the canvas until cleaned and confirmed, same as in the prose.

## The figure bar, what the critic checks, by severity

A read-only pass. Group findings by severity. For each, give the figure, the problem in one line, and a concrete fix.

- **Critical.** The chart's data does not trace to `outputs/`. An untrusted column is plotted. The chart makes a different claim than the prose around it.
- **Major.** Wrong chart for the message (dual-axis where an index is meant, levels merged across sources, a pie ranking many slices). The title states a variable, not a finding. A real gap interpolated. A truncated bar baseline.
- **Minor.** Off-palette color or a hardcoded hex. Missing or vague source caption. A second point creeping into one chart. Over-precise tick labels.
