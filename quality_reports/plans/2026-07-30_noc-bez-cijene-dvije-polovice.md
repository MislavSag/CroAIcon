# Plan. Noć bez cijene, restructure the accommodation-model section

Date 30. srpnja 2026. Post `posts/2026-07-noc-bez-cijene/index.qmd`.
Status: awaiting approval.

## Why

The section at lines 102–118 presents three revenue-per-night figures as one series:

> Hotel po noćenju proknjiži **127,2 eura**. Kamp **12,2 eura**. Soba ili apartman **4,4 eura**.

The third is not a price and not comparable to the first two. It is GFI **firm** revenue
(203,2 M EUR, 1.691 firms) divided by DZS **category** nights (46,64 M), a denominator that is
96,8% household-run. The paragraph then spends five sentences retracting it. A skimming reader
keeps the bolded number and never reaches the retraction.

Evidence that the retraction does not work: this section misled its own author twice in one
session, once into believing the 55.2 nights were a firm segment, and once into believing
platform-booked nights sat outside the post's denominator. The author had the data open. A reader
gets one pass.

Root cause is a label collision. `55.2` names two different populations and the post uses one word
for both:

| | What it counts | 2024 |
|---|---|---|
| DZS 55.2 | nights and beds in facilities classified to the group, overwhelmingly household | 46,64 M nights, 732.274 beds |
| GFI 55.2 | firms that self-declared `nacerev23 = 5520` | 1.691 firms, 203,2 M EUR, 2.266 employees |

There is also a defect the current text understates. Firm NKD is self-declared at registration;
DZS object type is assigned per facility. Nothing guarantees the two sets overlap at all. A company
running categorised apartments may sit in `5510` while its nights book to 55.1 under
*Turistički apartmani*. So numerator and denominator are not merely different sizes, they have no
verified correspondence. `4,4` should therefore not be printed as a quantity anywhere.

## The replacement structure

Split the country in two rather than into three price points. `BS_TU14` carries an unused
object-type layer nested inside each NKD group, which lets the household layer be named directly
instead of inferred.

| | Nights 2024 | Share | Measurable? |
|---|---|---|---|
| Hotels (25.560.432) + camps (21.446.680) | **47.007.112** | **50,2%** | Yes. 74,7 EUR per night |
| *Sobe, apartmani, studio-apartmani, kuće za odmor* | **45.167.304** | **48,2%** | No |
| Residual (hosteli, domovi, lječilišta, ostalo) | 1.509.398 | 1,6% | Immaterial |

Croatia's nights split almost exactly in half: half where money and nights describe the same
people, half where they do not. That is the post's title argued rather than asserted.

Supporting evidence for the second half, all already on disk:

- 697.267 beds against 1.691 firms and 2.266 employees. 412 beds per firm, 308 per employee.
- 37.687.805 platform-booked nights, **83,4%** of the household line. DZS's own table is titled
  *...u skupini 55.2*, so this is DZS placing Airbnb and Booking inside the category.
- 64,8 nights per bed against 158,4 for hotels.

## Changes

### 1. `python/tourism_value_build.py`

Extend `read_accommodation_types()` (or add a sibling) to read the **child** rows of `BS_TU14`,
which are marked by a three-space prefix on `Vrste smještaja`. Match on the stripped label.

New facts:

- `household_nights`, `household_beds`, `household_nights_share_pct`
- `commercial_nights`, `commercial_nights_share_pct` (hotels + camps)
- `residual_nights_share_pct`
- `platform_share_of_household_pct` (replaces `platform_share_of_apartments_pct`, which currently
  divides by the whole category and so understates at 80,8% instead of 83,4%)
- `household_beds_per_firm`, `household_beds_per_employee`

New gates:

- `household_layer_identified` — the household line is ≥ 95% of group 55.2 nights (actual 96,8%)
- `platform_nights_are_household` — platform nights ≥ 75% of the household line (actual 83,4%)
- `country_splits_in_half` — the three shares sum to 100 ± 0,1

Drop nothing from the facts file. `model_552_eur_per_night` stays computed so Napomene can cite the
bracket, but no longer renders in the body.

Note two suppressed cells: *Turistički apartmani* and *Guest house* nights are `z`. Beds are
published (9.811 and 81). Handle as NaN, never as zero, per the existing `MISSING_CODES` rule.

### 2. `python/tourism_value_charts.py`

Rewrite the Figure 2 builder (line 173, `tourism_2_po_vrsti_smjestaja.png`). Current chart sorts
three bars by `eur_per_night` and so gives 4,4 equal visual standing.

**Recommended.** Two priced bars plus an explicit void row:

```
Hotel      ████████████████████████  127,2 EUR    27,3% noćenja
Kamp       ██                         12,2 EUR    22,9% noćenja
Kućanstva  ·······················    nema mjere  48,2% noćenja
```

The void row is the point of the chart, not an omission from it. Title states the finding:
*Polovicu noćenja Hrvatska može naplatiti i izmjeriti. Drugu polovicu ne.*

Alternative if the void row reads as a data error: a 100% stacked single bar of national nights
split measurable / household / residual, with the 74,7 EUR annotated on the measurable segment.
Cleaner but loses the hotel-camp contrast, which would then live only in prose.

Figure 10 (`nights_per_bed`) is unaffected and keeps carrying the utilisation evidence.

### 3. `posts/2026-07-noc-bez-cijene/index.qmd`

Rewrite lines 102–118. Shape:

1. Bridge back from the 40 EUR headline.
2. State the split. Half the nights sit where firms and nights are the same people.
3. Give the two real prices, 127,2 and 12,2, and the 74,7 for the measurable half.
4. Turn to the other half as a **measurement boundary**, not a cheap price. Beds, firms,
   employees, platform nights. Never print 4,4.
5. Land the existing payoff, that 40 EUR is a capture rate rather than a low price.

Line 112's *Na apartmane otpada 49,8% ... a na firme 5,5% prihoda* keeps its arithmetic but the
subject changes from *apartmani* to *kućanstva*, and the share moves to the 48,2% household line so
both sides of the sentence describe the same population.

Line 118's platform paragraph merges upward into step 4 rather than arriving as a later reveal.

Napomene, lines 198 and 201: add the two-populations distinction explicitly, and record the
bracket as the reason the household segment carries no figure — attribute the 203,2 M EUR to the
whole category and it reads 4,4 EUR per night, attribute it to the non-household residual and it
reads about 138, above hotels. Both absurd, the truth unrecoverable, so no number is printed.
Per `MEMORY.md`, keep `b110`, `nacerev23` and table names out of the prose.

### 4. `MEMORY.md`

Append a `[LEARN:data]` line: `55.2` names a DZS nights/beds category (household-dominated) and a
GFI firm set (`nacerev23 = 5520`), and the two do not correspond. Never divide one by the other.
Taught by this section misleading its own author twice.

## Verification

1. `python python/tourism_value_build.py` — all gates pass, including the three new ones.
2. `python python/tourism_value_charts.py` — Figure 2 regenerates.
3. Inspect the new PNG before accepting it.
4. `QUARTO_PYTHON=.venv/Scripts/python.exe quarto render posts/2026-07-noc-bez-cijene`
   (per `MEMORY.md`, the render fails without it).
5. Confirm `4,4` appears nowhere in the rendered body. Grep the HTML, not the source.
6. Re-read the rendered section cold and check it cannot be misread the way it was today.

## Out of scope

- The pipeline's arithmetic. Every existing number verified correct this session; nothing is being
  recomputed, only relabelled and re-presented.
- The cross-sector spillover analysis (revenue per night by NKD division, county-year panel with
  fixed effects). Separate post, discussed but not planned here.
- Post stays `draft: true`. No commit, per standing instruction.
