# Plan. Ugradnja Bićanić (2012) i Bićanić, Deskar-Škrbić i Zrnc (HUB) u post "Svi naši usponi i padovi"

**Status: done (2026-07-25).** All eight changes applied; Maddison provenance
verified from `mpd2023.xlsx` (Sources sheet + per-republic rate comparison);
charts re-rendered; post renders clean.

Approved by Luka in chat (2026-07-25): "make these changes and if necessary also to visualizations."

## Sources being incorporated

- Bićanić, I. (2012). Prikaz knjige: Stipetić, Dva stoljeća razvoja hrvatskog
  gospodarstva (1820.-2005.). PKIEP 133/2012. https://hrcak.srce.hr/file/143698
- Bićanić, I., Deskar-Škrbić, M., Zrnc, J. Činjenice koje treba objasniti:
  analiza sekularnog rasta Hrvatske od 1952. do 2015. HUB.
  https://www.hub.hr/sites/default/files/inline-files/rh_dugi_rok_cinjenice_koje_treba_objasniti_final.pdf

## Changes

1. **Era split at 1980** (data + chart + prose). Bai-Perron breaks in the HUB
   paper are 1980, 1994, 2009; the current era table folds the 1980s stall into
   a 1952-1986 "+5,0%" era, producing a false symmetry with the 1993-2008
   recovery. New eras in `R/prepare_gdp.R`: Uspon socijalizma 1952-1980, Zastoj
   1980-1990, Slom 1990-1993, Oporavak 1993-2008 (unchanged), Druga kriza,
   Novije. Rerun `scripts/update_gdp.R`, re-render `python/gdp_charts.py`.
   Prose follows the new csv numbers.
2. **Tito sentence**: stall dates to 1980 (debt crisis, hard budget constraint,
   IMF stand-by), Tito's death same year is the marker, not the mechanism.
3. **Provenance of the socialist stretch**: verify against MPD 2023 data
   whether pre-1990 Croatia rates are republic-specific (Milanović republic DP
   rates, per HUB Dodatak 1) rather than "jugoslavenske stope prenesene na
   Hrvatsku". Fix karta pouzdanosti + Napomene accordingly; real caveats are
   DP != GDP concept and the 1990 anchor.
4. **Nineties**: add named overstatement mechanisms (okupirana područja izvan
   službene statistike ~10% stanovništva / ~25% teritorija do 1995.,
   hiperinflacija do 1993., neregistrirana ratna pomoć; Aslund 2001) and the
   anchor ("sidro") sensitivity next to the peak-choice sensitivity; note that
   two serious reconstructions (Milanović vs Bićanić et al.) disagree on the
   early-90s depth.
5. **Blokada**: "samo jedan izvor" -> only *verifiable* source; other published
   series exist (Stipetić 2012, Vinski 1978) but are non-reproducible per
   Bićanić (2012); HUB deliberately starts in 1952.
6. **Break lines**: 1990 is not a statistical break; the statistical turn is
   1994 and coincides with the October 1993 stabilization, not the end of the
   war.
7. **Konvergencija**: pointer to the HUB paper as the comparative work the post
   declines to do.
8. **Napomene**: method note that era rates are endpoint averages (trend gives
   lower, HUB: 3,3% vs 2,6%); references for the two papers with working links.

## Out of scope

- No change to the payoff (diversity of falls, time-to-recover).
- No import of the HUB institutional narrative beyond the one-sentence 1980
  mechanism.
- Drawdown census, thresholds, and the seven-falls structure stay as they are.

## Done when

- `outputs/tables/gdp_growth_eras.csv` regenerated, charts re-rendered, post
  edited, `quarto render posts/2026-06-hrvatski-rast-dugi-niz` passes, numbers
  in prose match the new csv.
