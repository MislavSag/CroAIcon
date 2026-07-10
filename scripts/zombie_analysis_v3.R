# ZOMBIE DURATION ANALYSIS v3 - correct physical columns, plan's recommended definitions.
# Headline def: NEGATIVE EQUITY (b063<0). Second: HNB imputed-rate (EBIT<6% of fin.debt 2yrs + loss).
# Death from register deletion date. See _workflow/gfi-variable-map.md.
suppressWarnings(suppressMessages({library(data.table); has_surv <- requireNamespace("survival", quietly=TRUE)}))
dir.create("outputs/tables", showWarnings=FALSE, recursive=TRUE)
afs <- readRDS("data/raw/zombie_extract_v2.rds")
reg <- readRDS("data/raw/zombie_register.rds")

## clean + merge
afs <- afs[!is.na(oib) & oib!=""]
setorder(afs, oib, year, -revenue); afs <- unique(afs, by=c("oib","year"))
reg1 <- unique(reg, by="oib")
afs[reg1, `:=`(founding_year=i.founding_year, status=i.status, brisan_year=i.brisan_year), on="oib"]
afs <- afs[grepl("^[A-U]$", nace) & nace!="K"]                 # non-financial
afs[, age := year - founding_year]
afs[, ebit := revenue - opex]
afs[, net := profit - loss]
afs[, fin_debt := rowSums(cbind(lt_fd1,lt_fd2,st_fd1,st_fd2), na.rm=TRUE)]
afs[, has_bs := !is.na(assets) & assets > 0]
afs[, last_year := max(year), by=oib]

## ============ DEFINITION 1: NEGATIVE EQUITY ============
afs[, z_ne := has_bs & !is.na(equity) & equity < 0]

## ============ DEFINITION 2: HNB imputed-rate ============
setorder(afs, oib, year)
afs[, weak_raw := fin_debt > 0 & ebit < 0.06*fin_debt]
afs[, `:=`(weak_l1=shift(weak_raw), py=shift(year)), by=oib]
afs[, weak2 := weak_raw & weak_l1==TRUE & (year-py==1)]
afs[, z_hnb := weak2==TRUE & !is.na(net) & net<0 & !is.na(age) & age>3 &
               (is.na(brisan_year) | year < brisan_year)]
afs[is.na(z_hnb), z_hnb := FALSE]

## ---------- transition matrix helper (3-state H/Z/Exit); D already filtered to universe ----------
trans <- function(D, zcol, wyears){
  X <- copy(D); X[, state := fifelse(get(zcol),"Z","H")]
  X[, last_u := max(year), by=oib]
  lk <- X[, .(oib, year, state)]; X[, ynext := year+1L]
  X[lk, next_state := i.state, on=.(oib, ynext=year)]
  X[is.na(next_state) & year>=2023, next_state := "cens"]
  X[is.na(next_state) & year==last_u & !is.na(brisan_year) & brisan_year<=year+3L, next_state := "Exit"]
  X[is.na(next_state) & year==last_u, next_state := "cens"]
  X[is.na(next_state) & year< last_u, next_state := "gap"]
  P <- X[year %in% wyears & state %in% c("H","Z") & next_state %in% c("H","Z","Exit")]
  round(prop.table(table(P$state, P$next_state),1)*100,1)
}

M_ne  <- trans(afs[has_bs==TRUE], "z_ne",  2004:2021)
M_hnb <- trans(afs[has_bs==TRUE], "z_hnb", 2004:2021)

## ---------- negative-equity SPELLS + KM ----------
BS <- afs[has_bs==TRUE]; setorder(BS, oib, year)
BS[, last_bs := max(year), by=oib]
lkz <- BS[, .(oib, year, zf=z_ne)]; BS[, yprev := year-1L]
BS[lkz, zprev := i.zf, on=.(oib, yprev=year)]
BS[, entry := z_ne & (is.na(zprev)|zprev==FALSE)]
BS[, sid := cumsum(fifelse(is.na(entry),FALSE,entry))]
zt <- BS[z_ne==TRUE]
sp <- zt[, .(oib=oib[1], start=min(year), end=max(year), len=.N,
             last_bs=last_bs[1], brisan_year=brisan_year[1]), by=sid]
sp[, `:=`(sm1=start-1L, ep1=end+1L)]
sp[lkz, prev_z := i.zf, on=.(oib, sm1=year)]
sp[lkz, next_z := i.zf, on=.(oib, ep1=year)]
sp[, incident := !is.na(prev_z) & prev_z==FALSE]
sp[, recovered := !is.na(next_z) & next_z==FALSE]
sp[, died := is.na(next_z) & end==last_bs & !is.na(brisan_year) & brisan_year<=end+3L]
sp[, censored := !(recovered|died)]
sp[, event := as.integer(recovered|died)]
inc <- sp[incident==TRUE]
km <- NA; if (has_surv && nrow(inc)>0) km <- summary(survival::survfit(survival::Surv(len,event)~1,data=inc))$table["median"]

## ---------- stock shares by year ----------
stock <- afs[year>=2004, .(
  n_bs = sum(has_bs),
  ne_share  = round(100*sum(z_ne)/sum(has_bs),1),
  ne_active = round(100*sum(z_ne & revenue>0)/sum(has_bs & revenue>0),1),
  hnb_share = round(100*sum(z_hnb)/sum(has_bs & fin_debt>0),1),
  emp_ne_share = round(100*sum(emp[z_ne],na.rm=TRUE)/sum(emp[has_bs],na.rm=TRUE),1)
), by=year][order(year)]

## ---------- sector (tourism test) ----------
sec <- afs[has_bs==TRUE & year %in% c(2008,2012,2016,2019,2022,2024),
  .(ne=round(100*mean(z_ne),1)), by=.(year, nace)]
sec_w <- dcast(sec, nace~year, value.var="ne")
tour <- afs[has_bs==TRUE & nace=="I", .(ne_share=round(100*mean(z_ne),1), n=.N), by=year][order(year)]

## ---------- county (latest) ----------
cty <- afs[has_bs==TRUE & year==2023, .(
  n=.N, ne=round(100*mean(z_ne),1),
  emp_ne=round(100*sum(emp[z_ne],na.rm=TRUE)/sum(emp,na.rm=TRUE),1)), by=county][order(-ne)]

## ============ PRINT ============
cat("############## ZOMBIE DURATION - CORRECT COLUMNS (v3) ##############\n")
cat(sprintf("panel 2002-2024, non-financial, %s firm-years / %s firms; with balance sheet: %s\n\n",
    format(nrow(afs),big.mark=","), format(uniqueN(afs$oib),big.mark=","), format(sum(afs$has_bs),big.mark=",")))

cat("== 1. NEGATIVE-EQUITY transition matrix, row %% (origins 2004-2021) ==\n"); print(M_ne)
cat(sprintf("   -> persistence P(Z->Z)=%.1f%%  recover P(Z->H)=%.1f%%  exit/die P(Z->Exit)=%.1f%%   [healthy P(H->H)=%.1f%%]\n",
    M_ne["Z","Z"], M_ne["Z","H"], M_ne["Z","Exit"], M_ne["H","H"]))

cat("\n== 2. HNB imputed-rate transition matrix, row %% ==\n"); print(M_hnb)
cat(sprintf("   -> persistence P(Z->Z)=%.1f%%\n", M_hnb["Z","Z"]))

cat("\n== 3. Negative-equity SPELLS (incident) ==\n")
cat(sprintf("n=%s | median observed length=%s yr | mean=%.2f | KM median=%s | recovered=%.0f%% died=%.0f%% censored=%.0f%%\n",
    format(nrow(inc),big.mark=","), median(inc$len), mean(inc$len),
    ifelse(is.na(km),"unreached(>panel)",sprintf("%.1f",km)),
    100*mean(inc$recovered),100*mean(inc$died),100*mean(inc$censored)))
print(inc[, .(pct=round(100*.N/nrow(inc),1)), by=len][order(len)][1:12])

cat("\n== 4. Stock shares by year ==\n"); print(stock)
cat("\n== 5. Tourism (I) negative-equity share by year ==\n"); print(tour)
cat("\n== 6. Negative equity by sector x year (%) ==\n"); print(sec_w)
cat("\n== 7. County (2023): negative-equity share + zombie-employment share ==\n"); print(cty)

fwrite(stock,"outputs/tables/zombie_v3_stock.csv")
fwrite(tour,"outputs/tables/zombie_v3_tourism.csv")
fwrite(sec_w,"outputs/tables/zombie_v3_sector.csv")
fwrite(cty,"outputs/tables/zombie_v3_county.csv")
fwrite(as.data.table(M_ne, keep.rownames="from"),"outputs/tables/zombie_v3_transition_negeq.csv")
fwrite(inc[, .(sid,oib,start,end,len,recovered,died,censored)],"outputs/tables/zombie_v3_spells.csv")
cat("\nsaved outputs/tables/zombie_v3_*.csv\n")
