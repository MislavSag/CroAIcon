# Zombie spell duration study — variable retrieval plan

**Date:** 2026-07-10
**Status:** research complete, pre-DB-session. No code written yet.
**Companion:** `research/zombie-duration-variable-plan.html` (rendered, navigable version of this doc).
**Reframe:** Stop measuring the *stock* of zombies (contested, 4–22%). Measure the *duration* — how long a Croatian zombie stays undead, how rarely it recovers, how rarely it is allowed to die. Headline target: *prosječni hrvatski zombi je živ mrtvac već X godina* + an annual transition matrix (healthy / zombie / exit).

---

## 0. Three blockers to resolve in the next DB session

The existing pipeline (`python/zombie_topic1_build.py`) is built on **catalog-vintage** column labels that conflict with the **physical-vintage** labels used in the two audited, published posts. Resolve before any zombie flag is computed.

1. **Revenue column.** `b125` (catalog: operating income, used in zombie/zagreb builds) vs `b110` (physical: operating revenue, audited in the debt + margins posts). Both cannot be revenue. Dump `codes_gfi_db_afs_physical` for both by `report_type`; cross-check national sums vs the ~150–200 bn EUR corporate-revenue macro anchor.
2. **Interest expense is unverified.** The published debt post declined to report ICR ("kamatni rashodi još nisu pouzdano izmjereni"). HNB Financijska stabilnost 22, Box 4 calls firm-level FINA interest data *"nepouzdani"* and imputes a 6% benchmark instead. The OECD/ICR zombie series rests on unaudited `b166+b168`. **Decision:** pivot the headline to interest-free definitions (negative equity + HNB imputed-rate); keep OECD/ICR as robustness only.
3. **`foreigncontrol` scale.** Research notes say 0–1 (threshold ≥ 0.5); `zombie_topic1_build.py:71` uses `> 50`. One is wrong. `SELECT MIN,MAX,AVG(foreigncontrol) FROM db_afs WHERE foreigncontrol IS NOT NULL AND reportyear=2023`. The ownership output is suspect until fixed.

---

## 1. DB session checklist (run before coding the duration build)

- [ ] **Revenue mapping** — dump `codes_gfi_db_afs_physical` for `b110` and `b125` by `report_type`; cross-check national sums vs 150–200 bn EUR anchor.
- [ ] **Interest `b166+b168`** — national coverage % 2008–2024; compare to annex `b277`; decide audit vs pivot to imputed rate.
- [ ] **Net profit** — confirm `COALESCE(NULLIF(b184,0),NULLIF(b197,0),0) - COALESCE(NULLIF(b185,0),NULLIF(b198,0),0)` coverage; cross-check vs physical `b152-b153`.
- [ ] **Equity** — probe physical `b063` vs catalog `b067`: `SELECT reportyear, SUM(b063<0)/COUNT(*) FROM db_afs WHERE b061>0 GROUP BY reportyear`. Expect `b067` near-zero by form design.
- [ ] **Financial debt** — confirm physical `b086+b087` (LT) and `b096+b097` (ST); component-fit gate ≥95% of rows where `b084>0`.
- [ ] **EBITDA / depreciation** — find physical depreciation column (catalog `b141`); coverage % 2010–2024. If <50%, restrict Storz to full-form filers.
- [ ] **`foreigncontrol` scale** — confirm 0–1; rebuild ownership output.
- [ ] **`subjekti_26012026` schema** — `SHOW COLUMNS`; check for `datum_brisanja`/`status`/`pravni_oblik`, else exit dates come from the court register API.
- [ ] **`countyid` → županija** — confirm `ref_county` (21 rows) exists; Zagreb = 21; build NUTS-3 crosswalk.
- [ ] **`price_deflator`** — `SELECT reportyear, AVG(price_deflator) ... GROUP BY reportyear`. Confirm exists, not-NULL through 2023, NULL for 2024.
- [ ] **`vw_db_afs_financial_subject_year`** — `SHOW CREATE VIEW` to inspect the blessed net-result construction.

---

## 2. Variable catalog by block

Legend: ✅ confirmed/audited · 🟡 unverified/coverage risk · 🔴 blocked/conflict.

### Core identifiers (db_afs + subjekti_26012026)

| Column | Meaning | Status | Notes |
|---|---|---|---|
| `subjecttaxnoid` | OIB, firm id | ✅ | STRING (leading zeros). Uniqueness on (id, year) not guaranteed — build uses `drop_duplicates`; audit duplicate volume. |
| `reportyear` | Fiscal year | ✅ | 2002–2024. 2023–24 preliminary. `price_deflator` real series ends 2023. |
| `godina_osnivanja` | Founding year (join `oib=subjecttaxnoid`) | ✅ ~92% match | Jan-2026 snapshot → survivorship bias pre-~2010; avoid age claims before 2012. Founding ≠ economic birth. ~8% unmatched dropped from OECD/HNB. |

### Operating performance (resolve vintage first)

| Column | Meaning | Status | Notes |
|---|---|---|---|
| `b125` / `b110` | Operating revenue | 🔴 conflict | See Blocker 1. |
| `b131` | Operating expenses (EBIT = rev − b131) | 🔴 unaudited | ~90% NULL in full-P&L subset → margins ~88% flat. Build silently drops NULL-EBIT firms. |
| `b166 + b168` | Interest expense (ICR denominator) | 🔴 never audited | HNB says unreliable. `fillna(0)` + `interest>0` requirement → NULL-interest firms never zombies by construction. |
| `b184/b185/b197/b198` | Net profit / loss | ✅ used (zagreb) | Use the COALESCE/NULLIF construction. `b183` is dead (~1% nonzero) — never use. |
| `b141` | Depreciation (for EBITDA) | 🟡 never queried | Coverage unknown; likely sparse for micro forms. Probe before Storz. |

### Balance sheet

| Column | Meaning | Status | Notes |
|---|---|---|---|
| `b063` / `b067` | Book equity | 🔴 use b063 | Catalog `b067<0` ≈ 0% every year (form floors at 0). Physical `b063` is audited. |
| `b061` / `b065` | Total assets | ✅ b061 | Catalog `b065` only ~8% populated, rising share → fake trend. Always `b061`. |
| `b002` | Fixed assets (Δ = net investment) | ✅ audited | Coverage ~87–89%. Δb002 is net change not gross capex; self-join on year−1. |

### Financial debt — physical vintage only

Audited & published: `b086+b087` (LT financial debt), `b096+b097` (ST), inside totals `b084`/`b094` (component-fit ≥95%).
**Blocked** (catalog, unaudited, do not use): `b100`, `b101`, `b112`, `b113`.

```
financial_debt   = (b086 + b087) + (b096 + b097)
imputed_interest = 0.06 * financial_debt   # HNB benchmark; consider time-varying median
```

### Slice dimensions

| Column | Meaning | Status | Notes |
|---|---|---|---|
| `nacerev21` | NKD section A–U | ✅ trusted | Filter `^[A-U]$`; exclude K, D, E. Tourism=I, Construction=F, Real estate=L. |
| `countyid` | County 1–21 | ✅ in db_afs | 100% populated; Zagreb=21; join `ref_county` (verify). |
| `foreigncontrol` | Foreign ownership share | 🔴 scale unresolved | See Blocker 3. |
| `subjectsizeeurev2` | Size class 0–4 | 🟡 assumed coding | No codebook evidence; confirm. |
| `employeecounteop` | Employees (EoP headcount) | ✅ trusted | Zombie-employment weight; internal GFI denominator for county shares. |
| `price_deflator` | Per-row deflator | 🟡 unverified column | Never selected by any script; confirm existence. Ratios/shares don't need it. |

---

## 3. Four zombie definitions — variable requirements

### ① OECD / ICR — Adalet McGowan, Andrews & Millot (2017), *Economic Policy* 33(96)
`ICR = EBIT / interest_paid < 1` for 3 consecutive years AND age ≥ 10.
Columns: `b125`/phys, `b131`, `b166`, `b168`, id, year, `godina_osnivanja`.
Spell start = **first** year of the 3-year window (date back 2y). Recovery = any year ICR ≥ 1.
**Robustness only** — interest denominator unaudited/disputed.

### ② Negative equity — Bonfim et al. (2021); Croatian: Beriša (2023, CNB YES seminar) — **RECOMMENDED HEADLINE**
`book_equity < 0` in prior period → physical `b063_{t-1} < 0`. No age, no interest, no market data.
Computable across all form vintages 2002–2024. Captures balance-sheet insolvency. In Croatia equity stays negative for years without exit — exactly the spell mechanics being studied.
Robustness variant: require `b063<0` in both t and t−1.

### ③ HNB imputed-rate / "Huljak-nod" — HNB Financijska stabilnost 22, Okvir 4 (May 2021) — **RECOMMENDED for duration headline**
- Step 1 (weak): `EBIT < 0.06 × financial_debt` for 2 consecutive years.
- Step 2 (zombie): weak AND `net_profit < 0` AND `age > 3` AND NOT in exit proceedings.
Built specifically to sidestep unreliable FINA interest. "Exit proceedings" filter needs the court-register merge. CNB result end-2019: ~6% zombies, ~22% weak, concentrated in **transport, agriculture, manufacturing — not tourism** (this baseline powers the COVID counterfactual).
**Attribution:** FS 22 Box 4 is unsigned. Cite as *HNB Financijska stabilnost 22, Okvir 4* — NOT "Huljak (2021)". Huljak's authorship is plausible (mentor of Beriša 2023) but unverified.

### ④ Storz et al. / ESRB WP 143 — Havemeister & Horn (2023), adopting Storz (ECB WP 2104, 2017)
All three for 2 consecutive years: (i) ROA < 0; (ii) Δfixed assets < 0; (iii) `EBITDA / financial_debt < 5%`. No age filter.
```
ROA=net_result/b061 ; net_inv=b002_t−b002_{t-1} ; EBITDA=EBIT+b141 ; fin_debt=(b086+b087)+(b096+b097)
```
No interest needed. Lowest zombie share by design (most distressed subpopulation). **Depreciation coverage risk** (`b141`) — may need to restrict to full-form filers.

---

## 4. Exit & death measurement

**Core rule:** disappearance from GFI is NOT death — Croatian filing compliance is imperfect; non-filing is a zombie state. Register status + deletion dates are canonical.

### Sudski registar open data API — FREE, verified live July 2026
`sudreg-data.gov.hr` — full machine-readable court register, daily snapshot, covers **deleted firms with deletion dates** (`subjekti?only_active=0`). Exit dates 2002–2024 reconstructable from one snapshot. OAuth2 client credentials (free registration), paginated REST/JSON, Otvorena dozvola license, EU High-Value Dataset.

Key fields: `mbs` (stable join key), `oib`, `status` (1=active, 0=deleted), `datum_brisanja`, `postupak.datum_stecaja`, exit-mode šifra (stečaj/likvidacija/brisanje), `sjediste.sifra_zupanije`.

Caveats: public tier is current-state (no row-level history); old bankruptcies have empty `datum_stecaja` → supplement with **e-Oglasna** stečaj announcements (OIB-keyed, XLSX export, from ~Sept 2015) and Narodne novine for pre-2014. Many pre-2009 deletions have no OIB → **key the exit merge on MBS**, map to OIB where present, or old deaths are lost.

### Three-state model
`Healthy ⇄ Zombie → Exit` (Zombie→Exit and Healthy→Exit absorbing/competing risks).
Banerjee & Hofmann (BIS WP 882): ~25% of zombies eventually exit via death, ~60% formally recover — but recovered zombies underperform and relapse, so distinguish "recovered (at-risk)" from "never-zombie" if n allows.

### Account blockade (Nama / ~12,500 blocked narrative) — firm-level NOT open
Firm-level blockade duration not retrievable at panel scale from open data. FINA Očevidnik is per-firm transactional only (1.66 EUR/SMS; monitoring is prospective). **Fininfo.hr** sells firm-level blockade *history* to subscribers (closest ready-made source; licensing by negotiation). FINA monthly PDFs give macro totals only (verified July 2026: 13,076 blocked, EUR 955.5m; ~41.4% blocked >1yr) — good for framing, useless for firm identification.

---

## 5. Geographic & auxiliary sources

### County NUTS-3 boundaries — giscoR (free, R-ready)
```r
library(giscoR); library(sf); library(dplyr); library(ggplot2)
hr <- gisco_get_nuts(year=2024, nuts_level=3, resolution="03", epsg=4326, country="HR")  # 21 rows
# countyid -> NUTS_ID crosswalk (CONFIRM countyid = DZS codes 1-21 in DB session)
xw <- tibble::tribble(~countyid, ~NUTS_ID,
  1,"HR065", 2,"HR064", 3,"HR028", 4,"HR027", 5,"HR062", 6,"HR063", 7,"HR021",
  8,"HR031", 9,"HR032",10,"HR022",11,"HR023",12,"HR024",13,"HR033",14,"HR025",
 15,"HR034",16,"HR026",17,"HR035",18,"HR036",19,"HR037",20,"HR061",21,"HR050")  # Zagreb=21=HR050
map_df <- hr |> left_join(xw,"NUTS_ID") |> left_join(county_zombie_stats,"countyid")
ggplot(map_df) + geom_sf(aes(fill=zombie_emp_share), color="white", linewidth=.2) +
  scale_fill_viridis_c(option="magma", direction=-1) + theme_void()
```

### DZS county employment — robustness denominator only
xlsx: `podaci.dzs.hr/media/xpkfrkth/zaposlenost-i-place-pregled-po-zupanijama.xlsx` (+ `.../syjnewxe/zaposleni-pregled-po-zupanijama.xlsx`). Series back to 1994.
**Caveat:** DZS covers ALL legal entities + obrt + agricultural insurees — much broader than the GFI poduzetnici base, so DZS-based shares understate zombie-employment. **Use internal GFI `employeecounteop` sum by county as the headline denominator**, DZS as robustness. Series break from 2025 (JOPPD vs RAD-1G, "nisu usporedivi").

### State ownership flags — ~100–150 firms, manual crosswalk (runner-up angle)
CERP portfolio xlsx (`cerp.hr/portfelj-cerp-a/dionice-i-poslovni-udjeli/114`, monthly, ~8 majority + ~80 minority with OIB + % stake) + NN 147/2021 special-interest SOEs (~36). OIB-joinable in an afternoon; expandable to ~500 via MFIN subsidiary reports. NOT feasible at panel scale — public sudreg API exposes no founder/member records.

---

## 6. Spell mechanics & survival setup

**Persistence trap:** a 3-year entry rule creates a mechanical 3-year minimum spell and a 2-year entry lag. Date spell start at the FIRST qualifying year; treat persistence as a measurement property, not the hazard. Storz/HNB 2-year rules → 2-year minimum, 1-year lag.

### Censoring rules
| Observation | Treatment |
|---|---|
| Still zombie in 2024 | Right-censor at 2024 |
| Disappears from GFI, no register death | Right-censor at last GFI year (non-filing ≠ death) |
| Confirmed deleted (`datum_brisanja`) | Event = exit; year = stečaj opening if available, else deletion |
| Already zombie in 2002 (left-truncation) | Age covariate, or restrict to spells starting ≥2004 |
| Merger / acquisition | Censor at merger, or separate competing risk |

### R implementation
```r
library(survival); library(survminer); library(mstate)
# Kaplan-Meier spell duration
km <- survfit(Surv(spell_length, event_recovery) ~ definition, data = zombie_spells)
ggsurvplot(km, risk.table=TRUE, conf.int=TRUE, break.time.by=1)
# Multi-state healthy/zombie/exit
tmat <- transMat(list(c(2,3), c(1,3), c()), names=c("Healthy","Zombie","Exit"))
msdata <- msprep(time=c(NA,"t_zombie","t_exit"), status=c(NA,"zombie_event","exit_event"),
                 data=firm_panel, id="subjecttaxnoid", trans=tmat)
fit_ms <- msfit(coxph(Surv(Tstart,Tstop,status)~strata(trans), data=msdata, method="breslow"), trans=tmat)
pt <- probtrans(fit_ms, predt=0)   # annual transition probability matrix
```

**Headline stat:** median KM spell length across all definitions (report the range as the robustness bar). Second finding: the annual transition matrix (Zombie→Zombie persistence prob). Banerjee & Hofmann (2018) found "stay zombie" rose 60%→85% (1980s→2016) for listed firms; Croatia's number on a mostly-unlisted, enforcement-weak system is what this post will own.

---

## 7. Recommended path

1. Resolve the 3 blockers in a DB session (§0–1).
2. Build the panel on **physical** columns; headline = **negative equity (②)** + **HNB imputed-rate (③)**; OECD/ICR (①) and Storz (④) as robustness across-definition bar.
3. Merge court-register exit dates on **MBS** (free API).
4. KM median spell + 3-state transition matrix + county choropleth (GFI-internal employment denominator).
5. COVID counterfactual: was tourism (NKD I) already drifting zombieward pre-2020? HNB 2019 baseline says tourism was NOT the concentration — a clean contrarian test.

**Sources verified July 2026.** Coverage %s quoted from prior ad-hoc DB sessions (research notes) — re-verify in the reproducible build. Blockade firm-level data is paid/proxied, not open.
