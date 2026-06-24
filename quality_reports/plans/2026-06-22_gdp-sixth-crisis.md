# Plan. Add the Cominform crisis as a sixth fall to the GDP long-series post

**DONE 2026-06-22.** All six edits applied, post renders clean, count consistent throughout (six falls / six returns). Closing-list framing chosen.

Date 2026-06-22. Post `posts/2026-06-hrvatski-rast-dugi-niz/index.qmd`.

## Why

The series shows a real downturn 1949 to 1952, the Tito-Stalin split and Cominform
blockade. It is confirmed inside a single source (Tica), not a seam artifact, so it
is a genuine sixth fall. The post currently counts five and skips this one. The
author confirmed it is real and wants it counted as six throughout, with a sentence
where it belongs.

## Anchored numbers (from `outputs/tables/`)

- Spliced index (`gdp_long.csv`). Peak **indeks 19 (1949.)** to trough **indeks 16
  (1952.)**, about **minus 18%**.
- Raw Tica (`gdp_raw.csv`). 2009 (1949.) to 1655 (1952.), also about minus 18%.
- The dip lives entirely in the Tica years, before Maddison begins in 1952. Pre-1952
  is the less-certain part of the series, so hedge as the post hedges its other early
  numbers.

## Edits

1. **Opener / framing (lines 24 to 26).** The "najupečatljiviji je povratak" passage
   says "Pet padova, pet povrataka." Change to six. Keep "dvije krize se izdvajaju"
   as is, those two are still the standouts.
2. **New sentence, socialism section (around line 66 to 70).** The section opens at
   indeks 16 (1952.) as a launch pad. Add one sentence that the line actually fell
   *into* 1952. Place it before the takeoff so 1952 reads as a trough, not a baseline.
   Tie to the Cominform blockade. Anchor to peak 19 (1949.) to trough 16 (1952.),
   minus 18%. Hedge (Tica years, less certain).
3. **Section header (line 114).** "## Pet puta dolje, pet puta natrag" to six.
4. **Closing passage (lines 116 to 118).** The list "Rat 1914. Rat 1940. Slom
   1990-ih. Mljevenje 2008. do 2014. Pandemija 2020." has five items. Add the
   Cominform fall (1949 to 1952). Update "Pet puta dolje, pet puta natrag" to six.
5. **Sweep.** Grep the file for any other "pet" / "five" / count of crises to catch
   stragglers.

## House-style notes

- Bold the carrying numbers, arrow form for the transition, per the published post.
- This is a real finding, not a [KUT] interpretation, so it gets written in plainly.
  The *meaning* of having a sixth fall (does it change the "law of return" read) is
  already covered by the existing [KUT] at the close. Do not add a new [KUT].
- Numbers trace to `gdp_long.csv` and `gdp_raw.csv`. No new script output needed.

## Verify

- Re-grep for "pet" to confirm no "five" survives.
- Confirm the six falls are now: 1914 war, 1940 war, 1949 to 1952 Cominform, 1990s
  collapse, 2008 to 2014 grind, 2020 COVID. (Note: the early count had not named the
  two world wars as "falls" explicitly in the five; the closing list does. Make the
  closing list and the framing agree on which six.)
- Render the post.
