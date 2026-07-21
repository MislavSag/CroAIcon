# MEMORY.md. Shared learnings

Corrections and facts that must not be relearned. Both tools read this before they write or review. Append, do not rewrite history. Keep it under a few hundred lines and prune stale lines when it gets noisy.

Format for a correction. [LEARN:category] what was wrong → what is right, with the file or moment that taught it.

## Facts that do not change

- The stack is R for analysis, Quarto for posts, git for everything.
- The GFI base is FINA annual reports, table `db_afs`, one row per firm and year.
- Trusted baseline columns are `employeecounteop` and `nacerev21`. Financial columns require the `codes_gfi_db_afs_physical` codebook plus an analysis-specific audit before use.

## Data quirks

- [LEARN:data] A rising firm count in `db_afs` partly reflects wider coverage of the base, not real growth → say coverage, not growth, unless you can separate the two.
- [LEARN:data] Employee counts are end of period headcounts and more robust than firm counts → lead with employment when the two disagree.
- [LEARN:data] `codes_gfi` does not match the physical `db_afs.bNNN` financial-column layout -> use MySQL table `codes_gfi_db_afs_physical`, imported from `financije_sifrarnik.xlsx`, for GFI balance/P&L column labels.
- [LEARN:data] The VIEW `vw_db_afs_metric_catalog` is ALSO poisoned — `SHOW CREATE VIEW` shows it is built on `codes_gfi` (`from codes_gfi cg`), so it inherits the wrong bNNN map. Never resolve `db_afs` column meaning from it. Verified column map + the empirical proof (physical `b110`=revenue 88% cov €105bn vs catalog `b125` 7% €0.8bn; `b061`/`b063` assets/equity ~100% vs `b065`/`b067` ~6%; negative equity is `b063<0`≈28-32%, NOT `b067` which is floored at 0) live in `_workflow/gfi-variable-map.md` — the single source of truth. Cheap check: a real headline line is populated for most firms and sums to a sane macro total; a wrong column covers ~5-8% and sums to nonsense. Taught by a session that used `b125`/`b065`/`b067` off the catalog view and got a fake "financials only cover 8k firms / no negative equity" result.
- [LEARN:data] Godišnje izvješće o državnim potporama za 2024. mijenja metodologiju. Prvi put odvojeno prikazuje poljoprivredu i ribarstvo i izuzima izravna plaćanja ZPP-a (842,1 mil. eura) iz definicije potpore → naslovni iznos za 2024. (1,4 mlrd.) NIJE usporediv s naslovnim iznosom izvješća za 2023. (3.035,6 mil.). Isto izvješće 2023. iskazuje ponovno na blizu 2,1 mlrd. i pad mjeri na 30,4%. Naivna usporedba naslovnih iznosa daje lažnih minus 54%. Izvješće za 2024. nije na `mfin.gov.hr`, nego samo na sabor.hr i u materijalima 135. sjednice Vlade.
- [LEARN:data] GFI/FINA health employment (zdravstvo, NKD područje Q) does not match DZS health figures → DZS counts all health personnel plus dental care and pharmaceutical wholesalers (veledrogerije), a wider scope than the GFI base. Read the health sector and its +164% gain cautiously. Flagged by Zoran Aralica on the sektori post.

## Corrections log

- [LEARN:style] (seed example) A long dash slipped into a method box → the house uses periods, arrows, and parentheses, never long dashes.
- [LEARN:style] Post notes (`## Napomene`) carried raw GFI column codes (`b110`, `b086 + b087`, NKD section letters) and codebook internals (`codes_gfi_db_afs_physical`, table and šifrarnik names) in the prose, and literature as bare `Author (year) za topic` → keep Napomene plain. Say what each variable means and how it is calculated, not its column code. Keep codebook and table names out of the post (they govern the analysis, not the reader, see the `codes_gfi_db_afs_physical` data quirk above). Give literature as proper references with working links (DOI or direct PDF). Script paths in backticks stay. Taught editing `posts/2026-06-zaduzenost-hrvatskih-firmi/index.qmd`.
- [LEARN:style] Sensational, anthropomorphic verbs landed on abstract financial concepts (*omjer vrišti*, *dug jede prostor*, *dug boli* in a header, *slika puca*) and dramatic words replaced plain ones (*masovan*, *novi projekt*) → keep motion verbs for concrete actors (sektori, firme, radnici) and give abstract concepts (dug, omjeri, marža, slika) calm, literal language even when the number is big; prefer the exact word (*velik*, *uzima prostor za nove investicije*, header *koči ulaganje* not *boli*). See the *Calm words for abstract things* section in `_workflow/house-style-guide.md`. Taught editing `posts/2026-06-zaduzenost-hrvatskih-firmi/index.qmd`.
- [add corrections here as they happen, newest at the bottom]

## Workflow learnings

- [add reusable fixes here. If one is a multi step procedure, capture it as a skill instead of a line]
