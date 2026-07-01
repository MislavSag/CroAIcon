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
- [LEARN:data] GFI/FINA health employment (zdravstvo, NKD područje Q) does not match DZS health figures → DZS counts all health personnel plus dental care and pharmaceutical wholesalers (veledrogerije), a wider scope than the GFI base. Read the health sector and its +164% gain cautiously. Flagged by Zoran Aralica on the sektori post.

## Corrections log

- [LEARN:style] (seed example) A long dash slipped into a method box → the house uses periods, arrows, and parentheses, never long dashes.
- [LEARN:style] Post notes (`## Napomene`) carried raw GFI column codes (`b110`, `b086 + b087`, NKD section letters) and codebook internals (`codes_gfi_db_afs_physical`, table and šifrarnik names) in the prose, and literature as bare `Author (year) za topic` → keep Napomene plain. Say what each variable means and how it is calculated, not its column code. Keep codebook and table names out of the post (they govern the analysis, not the reader, see the `codes_gfi_db_afs_physical` data quirk above). Give literature as proper references with working links (DOI or direct PDF). Script paths in backticks stay. Taught editing `posts/2026-06-zaduzenost-hrvatskih-firmi/index.qmd`.
- [LEARN:style] Sensational, anthropomorphic verbs landed on abstract financial concepts (*omjer vrišti*, *dug jede prostor*, *dug boli* in a header, *slika puca*) and dramatic words replaced plain ones (*masovan*, *novi projekt*) → keep motion verbs for concrete actors (sektori, firme, radnici) and give abstract concepts (dug, omjeri, marža, slika) calm, literal language even when the number is big; prefer the exact word (*velik*, *uzima prostor za nove investicije*, header *koči ulaganje* not *boli*). See the *Calm words for abstract things* section in `_workflow/house-style-guide.md`. Taught editing `posts/2026-06-zaduzenost-hrvatskih-firmi/index.qmd`.
- [add corrections here as they happen, newest at the bottom]

## Workflow learnings

- [add reusable fixes here. If one is a multi step procedure, capture it as a skill instead of a line]
