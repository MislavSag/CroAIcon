# Plan. Restructure the debt post to house structure

Target file: `posts/2026-06-zaduzenost-hrvatskih-firmi/index.qmd` (Mislav Sagovac)
Model to match: `posts/2026-06-firme-i-zaposlenost-po-sektorima/index.qmd`

## Context

The debt post came in from `origin/main` (commits "Add debt structure post" → "Fix debt post AOP mapping"). Its body is solid and QA-blessed (score 95), but it opens with two paragraphs of codebook / MySQL / AOP-mapping plumbing instead of an opener that orients the reader and lands a number. That methodology is the "weird stuff at the beginning." The QA report itself notes the provenance detail is *material* (the post exists to correct the broken `db_afs.bNNN` mapping logged in `MEMORY.md`), so the right move is to **relocate** it into *Napomene*, not delete it, and rebuild the front of the post to the same shape as the firms/employment post.

Intended outcome. A reader meets the finding in the first two lines, the four chart sections read as one argument, and every codebook caveat survives in the notes box.

## Constraints

- **Preserve every number exactly.** All figures trace to `outputs/tables/debt_*.csv` (per QA). This is a prose/structure edit, no re-analysis, no script changes, no chart rebuilds.
- **Keep all four charts and captions** (`debt_1_dynamics.png` … `debt_4_sector_size.png`).
- **Do not lose the codebook caveat.** The "why the physical codebook, not `codes_gfi`" rationale moves into *Napomene*, where it half-lives already.
- **Leave authorship and `draft:` untouched** — it is Mislav's already-published post. (The "keep draft:true" memory note is about our own new posts, not his.)

## Changes, section by section

**Front matter**
- `title`: keep `"Dug nije masovan, ali je koncentriran"` (already a claim).
- `subtitle`: strip the codebook jargon ("Na ispravnom GFI šifrarniku…"); restate as a literal finding with the contrast and the standout — typical firm 6,6%, aggregate 32%, real estate carries the heaviest ratio.
- `description`: set empty (house rule: empty when it only echoes title/subtitle).

**Opener** (replaces current lines 11–13, the codebook preamble)
- Orient + hortative bridge + hero contrast, mirroring the model's *Odgovorimo … dvije brojke, dvije različite priče*:
  question (how indebted are Croatian firms?) → *Odgovorimo* → **medijan 6,6% (2024.)** vs **agregat 32%** → name the promise: the gap is the story, debt is concentrated not widespread.
- No codebook / MySQL / AOP text in the opener.

**Body** — keep Mislav's four sections and their charts, tighten to house style (arrows, bold change, lead/land on a number, light narrative bridge between sections):
1. *Agregat i medijan pričaju različitu priču* — `debt_1`. 37% (2008.) → 32% (2024.), vrh 50% (2016.); medijan 8,0% → 6,6%; gornji kvartil ~42%, gornji decil > godišnji prihod. Land: aggregate is a picture of concentration, not the average firm.
2. *Dug je više dugoročan nego kratkoročan* — `debt_2`. Kratkoročno ~32% (2024.), ~isto kao 2008., vrh ~37% (2016.). Don't overstate rollover risk.
3. *Neprofitabilne firme nose najteži teret* — `debt_3`. Median by net-margin quintile: weakest 60% → sredina ~7% → najviši 0%; ali agregat najvišeg kvintila 48% (few big profitable firms carry the debt). Pecking-order.
4. *Nekretnine iskaču iz sektorske slike* — `debt_4`. Most-leveraged framing: nekretnine **325%**, smještaj/ugostiteljstvo **75%**, građevinarstvo **68%**, ostali **39–45%**. The sharpest finding; a map of vulnerability, not a verdict.

**Payoff** (tighten current closing line): land the *so what* — Croatian firms aren't broadly over-indebted; debt concentrates by size, profitability, and sector, and that's where refinancing pressure bites first if conditions tighten.

**Napomene** — keep Mislav's existing notes (source, sample `b110>0` / NKD A–S excl K / 80k–142k firms, debt = `b086+b087` long + `b096+b097` short, revenue `b110`, net result `b152-b153`, "što nije korišteno", literatura, scripts). Ensure the one-line "why the physical codebook `codes_gfi_db_afs_physical`, not `codes_gfi`" rationale that left the opener is fully present here (it largely is, in the šifrarnik note — strengthen if thin).

## Verification

- `quarto render posts/2026-06-zaduzenost-hrvatskih-firmi` builds clean and the four charts resolve. (No Python rerun needed — no scripts or numbers change.)
- Eyeball against the house checklist: headers alone tell the story; every paragraph leads/lands on a number; no dashes; opener connects up to subtitle and down to the first number; no codebook plumbing above *Napomene*; notes box lean but keeps the material codebook caveat.
- Confirm no number drifted from the original by diffing the figures against the current file.

## Notes for the author

- I am not adding `[KUT]` markers. The one genuine human-judgment item — whether the new physical codebook mapping can be trusted — is Mislav's call, already QA-blessed, and stays as prose in *Napomene*. Flag back if you want it surfaced more prominently in the body.
- On approval I will also save this plan under the dated convention `quality_reports/plans/2026-06-24_zaduzenost-restructure.md`.
