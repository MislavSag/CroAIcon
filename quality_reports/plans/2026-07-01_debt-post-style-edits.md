# Plan. Debt post style edits + bake style principle

Date: 2026-07-01. Author pass: Luka. Post: `posts/2026-06-zaduzenost-hrvatskih-firmi/index.qmd` ("50 nijansi zaduženosti").

## Why
Author flagged sensational/anthropomorphic verbs on abstract financial concepts (*vrišti*, *boli*, *jede*, *puca*), dramatic words over plain ones (*masovan*, *novi projekt*), and unclear titles/captions. Fix the post, then bake the rule into the house style so it holds for all future posts.

## Post edits
1. Opener para (l.13). *masovan* -> *velik*; *jesti prostor za novi projekt* -> *uzimati prostor za nove investicije* (author's exact wording).
2. Header (l.33). *Nekretnine su najteži omjer, ali stanje duga je šire* -> *Nekretnine su najzaduženije u odnosu na prihod, ali dug je raspoređen po mnogim sektorima*.
3. Sector-stock sentence before fig (l.39). Rewrite to name the ratio-vs-stock distinction plainly; drop metaphoric *sjedi*.
4. Sector-stock sentence after fig (l.43). Drop *vrišti* and metaphoric *sjedi*; state takeaway literally.
5. Header (l.45). *Koncentriran...* -> *Dug je koncentriran...* (self-standing claim). [audit find]
6. Caption (l.57). *lagirane zaduženosti* -> *zaduženosti na početku godine* (drop jargon). [audit find]
7. Header (l.65). *Dug najviše boli kad nema marže* -> *Dug najviše koči ulaganje kad je marža slaba*.
8. Overhang paras (l.69-71). Rewrite awkward *Aktualni literaturni kut* opener and *prvi red na budućem novcu*; drop *slika puca*; spell out *plus 2,2%*. Keep all numbers and the term *debt-overhang*.
9. Conclusion (l.73). *obveza već jede prostor* -> *obveza već uzima prostor* (same banned metaphor). [author's principle, applied for consistency]

Numbers preserved exactly: 19/15/13/11/10%, 325/75/68%, +2,2%, -0,7%, -0,2%, bands 50-100% and >100%. Date/author unchanged.

## Style-guide edit
Add section **"Calm words for abstract things"** to `_workflow/house-style-guide.md` right after "Verbs that move", plus a checklist line. Reconciles with "Verbs that move": motion for concrete actors and big real moves; calm literal language for abstractions (dug, omjer, marža, slika) whatever the magnitude.

## MEMORY edit
Append one `[LEARN:style]` line to `MEMORY.md` corrections log.

## Verify
Quarto not installed on this machine -> cannot render. Verify by re-reading the edited `.qmd` and grepping for banned verbs (vrišti, boli, jede/jesti, puca). Author to `quarto render` on a machine with Quarto.

## Done
- [x] Post edited
- [x] Style guide updated
- [x] MEMORY updated
- [x] Banned-verb grep clean (vrišti, boli, jede/jesti, puca, masovan, sjedi — 0 matches)
- [ ] `quarto render` — deferred, Quarto not installed on this machine
