# Zombie duration — results (correct columns), basis for the post

_Run 2026-07-10 on the verified physical columns (`_workflow/gfi-variable-map.md`). Panel: FINA
`db_afs`, non-financial firms, 2002–2024, 2.49M firm-years / 292,633 firms with a balance sheet.
Scripts: `scripts/zombie_pull_v2.R`, `scripts/zombie_analysis_v3.R`. Outputs: `outputs/tables/zombie_v3_*.csv`._

**Headline definition:** negative equity — a firm owes more than it owns (`b063 < 0`). Balance-sheet
based, no interest data needed. Cross-checked against the HNB imputed-rate definition.

---

## The five findings

### 1. One in four Croatian firms owes more than it owns
Negative-equity share of firms with a balance sheet: **19% (2004) → peak 32% (2012) → 26% (2024)**.
Among firms with actual revenue it is ~23–28%. This is the *high* end of the contested 4–22% zombie
debate — but it is a hard balance-sheet fact, not a definitional choice. A quarter of the corporate
sector is technically insolvent.

### 2. And it stays that way for years — this is the real story
Once a firm goes negative-equity it tends to **stay** negative-equity:
- **Annual persistence P(zombie → zombie) = 82%.** (Healthy → healthy = 91%.)
- **Median negative-equity spell = 4 years** (Kaplan–Meier); mean ~3.5 observed, with a long tail —
  spells of 8–12+ years are common (~10% of spells run ≥8 years).
- Only ~11% recover and ~7% die in any given year — so firms **linger** in insolvency.

This is the "undead duration" the post is about, and it needed the multi-year panel to see. (Note:
the flow-based interest-coverage measure showed the opposite — churn — because interest data is
unreliable; that is why the balance-sheet measure is the right lens.)

### 3. When a zombie finally leaves, it is a slow coin-flip toward recovery
Of firms that enter negative equity: **38% eventually recover, 23% die (deregistered), 39% still
stuck** at the panel's end. So it is not "nobody ever recovers" — but exit is slow and a large share
never resolves. Formal bankruptcy remains near-zero; death is via quiet deregistration.

### 4. The zombie coast — insolvency is concentrated on the Adriatic
Negative-equity share by county, 2023 (map-ready):

| Rank | County | Neg-equity % | | Lowest | County | % |
|---|---|---|---|---|---|---|
| 1 | Istarska | 32.9 | | | Brodsko-posavska | 16.8 |
| 2 | Šibensko-kninska | 32.7 | | | Vukovarsko-srijemska | 20.3 |
| 3 | Zadarska | 31.9 | | | Međimurska | 20.3 |
| 4 | Splitsko-dalmatinska | 30.3 | | | Varaždinska | 21.7 |
| 5 | Dubrovačko-neretvanska | 29.8 | | | Zagrebačka | 21.7 |
| 6 | Primorsko-goranska | 29.6 | | | Grad Zagreb | 25.8 |

The **six most insolvent counties are all coastal tourism counties**; the least insolvent are inland
and eastern. The "rich" tourist coast carries the most book-insolvent firms.

### 5. It is a tourism + real-estate story — and it predates COVID
By sector (negative-equity %, latest): **Real estate (L) ~41%, Tourism (I) ~38%**, then admin (N),
other services (S), mining (B) ~33–37%; manufacturing (C) ~20%, IT (J) ~16% are lowest.

Tourism (I) negative-equity share by year: 29% (2002) → **44% (2012)** → 39% (2019) → **46% (2020
COVID spike)** → 38% (2024). **Tourism was already 36–44% insolvent for the entire decade before
COVID.** COVID added a spike but did not create the problem — a clean contrarian test against the
"tourism zombification is a pandemic side-effect" narrative.

### (bonus) The jobs at stake
Firms in negative equity employ **~7–13% of all workers** (peaked ~13% in 2011, ~7% now) — not just
dormant shells; a real slice of employment sits inside book-insolvent firms.

---

## Robustness — locked (script `zombie_analysis_v4.R`, outputs `zombie_v4_*.csv`)

**Strip across three definitions (same panel):**

| Definition | Share 2023 | P(Z→Z) | Median spell (KM) | recovered / died |
|---|---|---|---|---|
| Negative equity (headline) | 26.6% | 81.6% | **4 yr** | 38% / 23% |
| Negative equity **+ loss-making** (hard core) | 18.8% | 63.8% | 2 yr | 59% / 16% |
| HNB imputed-rate | 10.0% | 65.9% | 2 yr | 63% / 11% |

The phenomenon is large and persistent under all three; the level moves, the persistence holds.

**Owner-loan guard — the critique is answered.** The worry was that negative equity could be
firms harmlessly financed by owner/parent loans. Test: of all negative-equity firms, **71–82% are
also loss-making** every year (currently ~73%). So the raw share is mostly genuine distress, not an
accounting artifact. The loss-making "hard core" is still ~19% of all firms. Report the headline as
negative equity, with the hard-core number beside it.

**Not a panel-length artifact.** Persistence is identical for firms that turned insolvent in
2005–2012 (P(Z→Z)=89.1%) vs 2013–2020 (87.5%) — disjoint cohorts agree, so the "they stay for
years" finding is a property of the process, not of our window length.

## Honest caveats (must be flagged in the post)
- **Negative equity ≠ certain distress.** Some firms run negative book equity while financed by
  owner/parent loans and are operationally fine (the "owner-loan" critique). This inflates the raw
  share. The HNB definition (which additionally requires operating losses) is the guard against it,
  and it still shows ~15% + high persistence.
- **"Recovery" can be recapitalisation/revaluation**, not a real turnaround.
- **Death = register deletion within ~3 years of last filing.** Court-register API (`sudreg`) would
  sharpen exact bankruptcy dates; not required for these findings.
- Blocked-accounts (blokada) duration — the Lider frame — is still not in the data (paid/FINA).

## Suggested post framing
Lead on the duration/verdict, not the stock. Candidate hook:
> *Svaka četvrta hrvatska firma duguje više nego što vrijedi — i takva ostane u prosjeku četiri
> godine. U Hrvatskoj se ne bankrotira; polako se tone.*

Spine: (1) a quarter of firms are book-insolvent → (2) and they stay that way ~4 years, 82% year to
year → (3) the zombie coast map → (4) tourism + real estate, insolvent before COVID → (5)
institutional close: almost nobody goes bankrupt; they just linger. One robustness strip (negative
equity vs HNB definition). Link the code.
