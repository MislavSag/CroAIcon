# Style critique. Svi naši usponi i padovi (dugi niz BDP-a)

Read-only pass against `_workflow/review-checklist.md`. Scope owned here: Voice
and writing (whole section), plus the notes-box half of Editorial and method.
Numbers verification, narrative arc, and charts belong to other agents and are
not re-litigated below except where a number surfaces as a voice/notes-box
honesty problem (a contradiction between two stated claims in the post itself).

Reviewed the file as it stands now, working tree against `git diff` off
`41443cd`. Note: `quality_reports/2026-06-hrvatski-rast-dugi-niz_qa.md` (today,
score 93) claims all findings from an earlier four-critic pass were fixed.
Two of the findings below (both Critical) show that claim was premature, at
least for these two spots, both inside material touched by today's rework.
Extra weight given to the new era section ("Rast u dva naleta, prvi jači"),
the 1980 debt-crisis paragraph, and the expanded Napomene, per instructions.

Punctuation sweep across the whole post: zero colons, zero em/en dashes, zero
quote marks in prose. One semicolon (flagged below). Clean otherwise.

## Critical

### 1. Napomene states one drawdown threshold, the body states another
**Location.** Lines 118-119 (body) vs. line 226 (Napomene, "Padovi i prag").
**Problem.** The body says the uncounted jitters (1927, 1956, 1980s stagnation,
1999) sit "ispod praga iz *Napomena*" at "minus 5%", but Napomene's own bullet
gives the actual counting threshold as "oko 7%" (matching
`fall_pct <= -7` in `scripts/gdp_drawdowns.R`). The body names a number and
attributes it to the notes box, and the notes box says a different number.
A reader who checks the box, exactly the reader this post says it rewards,
hits a contradiction.
**Rewrite.**
> Ispod ovih sedam ostaju trzaji, 1927., 1956., zastoj 1980-ih, 1999. Nijedan
> ne prijeđe minus 5%, dobro ispod praga od oko 7% iz *Napomena*, pa ih ne
> brojimo.

### 2. Letargija label and duration still carry the pre-correction window
**Location.** Line 104 (label and arrow in the same line), line 106 ("šest godina").
**Problem.** The bold lead "**Letargija 2008. do 2014.**" and the later "drže
liniju u mjestu šest godina" still reflect the old, superseded 2008-2014
window. The arrow immediately after the label, on the very same line, already
gives the corrected trough as 2012 ("indeks 96 (2012.)"), matching
`outputs/tables/gdp_drawdowns.csv` (trough_year 2012). The label also breaks
the peak-to-trough pattern the other two pad labels set (Depresija 1929. do
1932., Blokada 1949. do 1952., both peak-year-do-trough-year). "Šest godina"
matches neither the 4-year peak-to-trough span (2008-2012) nor the 9-year
peak-to-recovery span (2008-2017, already given two clauses later) — it is a
leftover of the old 2014 trough that the numbers were corrected around it but
the label and duration were not. The QA report claims this exact number was
fixed; the label shows it was only half-fixed.
**Rewrite.**
> **Letargija 2008. do 2012.** **Indeks 105 (2008.) → indeks 96 (2012.)** (oko
> **minus 9%**), plitko. Ali dugo. Financijska kriza pa duga domaća recesija
> drže liniju u mjestu, a vrh iz 2008. linija prijeđe tek 2017.

## Major

### 3. The 1980 debt-crisis mechanism runs three events into one sentence
**Location.** Lines 96-99 ("Jeftini strani krediti..." through "...2016.).").
**Problem.** This is the single most load-bearing new sentence in the post,
the actual mechanism the two 2016 papers earn their place for, and it chains
three separate historical beats (credit dries up, IMF deal signed,
stabilization begins) with commas into one long sentence. Every other
explanation in the post runs one idea per sentence; this is the one place
that reads like report prose instead of the house's punchy declaratives.
**Rewrite.**
> Jeftini strani krediti koji su uspon financirali nestaju u svjetskoj
> dužničkoj krizi 1979. i 1980. Zemlja potpisuje prvi uvjetovani aranžman s
> MMF-om. Kreće stabilizacija s devalvacijom (Bićanić, Deskar-Škrbić i Zrnc,
> 2016.).

## Minor

### 4. One semicolon, the only one in the post
**Location.** Line 245.
**Problem.** "(Aslund, 2001.; Bićanić, Deskar-Škrbić i Zrnc, 2016.)" is the
only semicolon in 277 lines otherwise built entirely on periods and commas.
The post already has a clean precedent for stacking two citations without one,
"Gnjatović (2017.) te Gnjatović i Aleksić (2011.)" a few lines above.
**Rewrite.**
> (Åslund, 2001. te Bićanić, Deskar-Škrbić i Zrnc, 2016.)

### 5. Aslund is missing its diacritic
**Location.** Lines 245 and 272 (Izvori).
**Problem.** The economist is Anders Åslund. Both the in-text citation and the
Izvori entry drop the Å, in a notes box that otherwise names every source
carefully (Miljković's unlinkable issue is even flagged rather than glossed
over).
**Rewrite.**
> [Åslund (2001.)](https://carnegieendowment.org/research/2001/03/the-myth-of-output-collapse-after-communism)
> za precijenjeni pad tranzicije.

## Not flagged, checked and clean

Present tense and active voice hold throughout. No hedging, no throat
clearing, no vague attribution (every claim in the new prose names Bićanić,
Bićanić-Deskar-Škrbić-Zrnc, or Bićanić-Tuđa directly rather than "one later
review"). No adjective stands in for a number without one following close
by. Abstract concepts (linija, sidro, društveni proizvod, tempo) keep calm,
literal verbs; the one dramatic-sounding verb "nestaju" (krediti nestaju) is
applied to a concrete flow of foreign lending drying up, not to an abstraction,
and reads as plain economic language rather than personification. All [KUT]
markers are resolved, none remain. Every section header states a finding.
Coined terms (*sidro*, *škare cijena*, *društveni proizvod*) are italicized,
self-explained in the body, and detailed once in Napomene. The body's
pointers to the box ("više u *Napomenama*", "zašto, u *Napomenama*") are
consistently subtle rather than restating the caveat in full.
