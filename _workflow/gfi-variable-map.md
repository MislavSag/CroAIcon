# GFI variable map — the ONE true column dictionary for `db_afs`

**This is the single source of truth for what each `db_afs.bNNN` column means.** Every session,
on every machine, resolve financial columns here first. Do not trust column labels from anywhere
else. Last verified against the live DB: 2026-07-10.

---

## The one rule

`db_afs` stores financial statement lines in physical columns `b001`–`b380`. **There are two
dictionaries in the database and they disagree completely.** Only one is right.

| Dictionary | What it is | Use it? |
|---|---|---|
| **`codes_gfi_db_afs_physical`** | Physical layout, imported from `financije_sifrarnik.xlsx` (sheet `cb_afs`). Matches how the data was actually loaded. | ✅ **ALWAYS** |
| `codes_gfi` | A generic/logical FINA AOP list. Assumes column `bNNN` = AOP `NNN`. **Wrong for this table.** | ❌ NEVER |
| `vw_db_afs_metric_catalog` | A VIEW. `SHOW CREATE VIEW` proves it is built **on `codes_gfi`** (`from codes_gfi cg`, `column_name = concat('b', lpad(AOP,3,'0'))`). Inherits the wrong map. | ❌ NEVER for column meaning |

**Why they differ:** `codes_gfi` assumes the physical column number equals the official AOP
position number. It does not. The real revenue line sits in physical column `b110`; `codes_gfi`
mislabels `b110` as "obveze prema društvima…" and calls `b125` revenue. Two different numbering
schemes; only the physical one matches the bytes in `db_afs`.

**How to catch a wrong column in 10 seconds** — coverage + a macro anchor:
- A real headline line (revenue, assets, equity) is populated for **most** firms and sums to a
  sane macro total. A wrong column is populated for ~5–8% of firms and sums to nonsense.
- Proof (2019, non-financial, 135,896 firms):

  | Quantity | Physical (correct) | Catalog (wrong) |
  |---|---|---|
  | Revenue | `b110`: 88% populated, **€105 bn** | `b125`: 7%, €0.8 bn |
  | Total assets | `b061`: 100% | `b065`: 5.5% |
  | Equity | `b063`: 99.9% | `b067`: 7.8% |
  | Negative equity share | `b063<0`: **28–32% of firms** | `b067<0`: 0% (floored) |

---

## Verified column map (physical, from `codes_gfi_db_afs_physical`)

### Balance sheet (Imovinska bilanca)
| Column | Meaning | Coverage |
|---|---|---|
| `b002` | B) Dugotrajna imovina — fixed / long-term assets | ~88% |
| `b034` | C) Kratkotrajna imovina — current assets | high |
| `b058` | Cash (novac u banci i blagajni) | high |
| `b060` | *) Gubitak iznad visine kapitala — loss above capital | — |
| **`b061`** | **E) UKUPNO AKTIVA — total assets** | 100% |
| **`b063`** | **A) KAPITAL I REZERVE — book equity** (can be < 0) | 99.9% |
| `b080` | B) Rezerviranja — provisions | — |
| `b084` | C) Dugoročne obveze — long-term liabilities (total) | high |
| `b086`+`b087` | Long-term financial debt (loans + bank debt) | audited |
| `b094` | D) Kratkoročne obveze — short-term liabilities (total) | high |
| `b096`+`b097` | Short-term financial debt (loans + bank debt) | audited |
| **`b108`** | **F) UKUPNO PASIVA — total equity + liabilities** (= b061) | 100% |

### Profit & loss (Račun dobiti i gubitka)
| Column | Meaning |
|---|---|
| **`b110`** | **I. POSLOVNI PRIHODI — operating revenue** (88% cov, the trusted revenue) |
| `b113` | II. Poslovni rashodi — operating expenses → **EBIT proxy = b110 − b113** |
| `b130` | III. Financijski prihodi — financial income |
| `b136` | IV. Financijski rashodi — financial expenses (interest is a *sub-line* here → unreliable, see below) |
| `b147` / `b150` | IX. Ukupni prihodi / X. Ukupni rashodi — total revenue / expenses |
| `b151` | XI. Dobit ili gubitak prije oporezivanja — pre-tax profit/loss |
| `b152` − `b153` | Dobit razdoblja − Gubitak razdoblja → **net result** |

### Non-financial dimensions (trusted, all years, do not need the codebook)
`subjecttaxnoid` (OIB), `reportyear`, `nacerev21` (NKD section A–U), `countyid` (1–21),
`subjectsizeeurev2` (size 0–4), `ownershiptypeid` / `foreigncontrol`, `employeecounteop`
(employees, ~71% cov — the trusted headcount), `price_deflator`.

### Do NOT use (wrong-map columns that look plausible but are not what their catalog label says)
`b125` (not revenue), `b065` (not assets), `b067` (not equity — floored at 0). Any label pulled from
`codes_gfi` / `vw_db_afs_metric_catalog`.

---

## How retrieval works (the pipeline, start to finish)

1. **Source.** FINA files annual statements → loaded into MySQL table **`db_afs`** (1993–2024, one
   row per firm-year, ~3M rows). Financial values live in physical columns `b001`–`b380`.
2. **Which column is which.** The physical layout is defined by `financije_sifrarnik.xlsx` (sheet
   `cb_afs`), imported into **`codes_gfi_db_afs_physical`** by `python/import_gfi_db_afs_codebook.py`.
   That table maps `db_column` → human label. **This is the map. Nothing else.**
3. **Pulling data (the way the published posts do it — see `python/debt_structure_build.py`):**
   select the *physical* columns straight from `db_afs`
   (`SELECT b110, b061, b063, b152, b153 … FROM db_afs WHERE reportyear=? AND b110>0 AND nacerev21 …`),
   then rename in code (`revenue = b110`, `assets = b061`, `equity = b063`). The physical codebook
   is queried only to attach labels, never to decide which column to read.
4. **Audit before trust.** Every financial ratio is gated: coverage ≥ threshold, balance identity
   `b061 ≈ b108`, macro-anchor plausibility. If a gate fails, the build blocks rather than publish.
5. **Connection.** Creds in `CroAIcon/.env` (gitignored). From R: `DBI` + `RMySQL`
   (`Rscript` at `C:/Program Files/R/R-4.4.1/bin/Rscript.exe`). From Python: `pymysql`
   (note: Python is NOT installed on the `lukas`/Dropbox machine — use R there).

## Full-balance-sheet history
`db_afs` (1993–2024) is P&L-complete and has the balance sheet too (`b061`,`b063`,`b108` ~100%).
`gfi_all` (1993–2019) is the older full-statement table with a **different** physical layout — do
not reuse `db_afs` column numbers on it; decode separately if ever needed.
