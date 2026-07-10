# TIGHTENING pass. (1) Owner-loan guard: negative equity vs negative-equity-AND-loss-making core.
# (2) Robustness strip across definitions. (3) Disjoint-cohort test (persistence not a window artifact).
# (4) Sharper death: register deletion OR stecaj/likvidacija status.
suppressWarnings(suppressMessages({library(data.table); has_surv <- requireNamespace("survival", quietly=TRUE)}))
dir.create("outputs/tables", showWarnings=FALSE, recursive=TRUE)
afs <- readRDS("data/raw/zombie_extract_v2.rds")
reg <- readRDS("data/raw/zombie_register.rds")

afs <- afs[!is.na(oib) & oib!=""]
setorder(afs, oib, year, -revenue); afs <- unique(afs, by=c("oib","year"))
reg1 <- unique(reg, by="oib")
afs[reg1, `:=`(founding_year=i.founding_year, status=i.status, brisan_year=i.brisan_year), on="oib"]
afs <- afs[grepl("^[A-U]$", nace) & nace!="K"]
afs[, `:=`(age=year-founding_year, ebit=revenue-opex, net=profit-loss,
           fin_debt=rowSums(cbind(lt_fd1,lt_fd2,st_fd1,st_fd2), na.rm=TRUE),
           has_bs = !is.na(assets) & assets>0)]
afs[, dead_firm := !is.na(brisan_year) | status %in% c("stečaj","likvidacija")]

# ---- definitions ----
afs[, z_ne   := has_bs & !is.na(equity) & equity<0]                 # negative equity (headline)
afs[, z_core := z_ne & !is.na(net) & net<0]                         # + loss-making = owner-loan-guarded
setorder(afs, oib, year)
afs[, weak_raw := fin_debt>0 & ebit < 0.06*fin_debt]
afs[, `:=`(weak_l1=shift(weak_raw), py=shift(year)), by=oib]
afs[, z_hnb := (weak_raw & weak_l1==TRUE & (year-py==1)) & !is.na(net) & net<0 &
               !is.na(age) & age>3 & (is.na(brisan_year)|year<brisan_year)]
afs[is.na(z_hnb), z_hnb:=FALSE]

BS <- afs[has_bs==TRUE]; setorder(BS, oib, year)

# ---- generic analyzer: transition matrix + KM spell for a zombie flag ----
analyze <- function(D, zcol, wyears=2004:2021){
  X <- copy(D); X[, z := as.logical(get(zcol))]; X[is.na(z), z:=FALSE]
  X[, state := fifelse(z,"Z","H")]; X[, last_u := max(year), by=oib]
  lk <- X[, .(oib,year,state)]; X[, ynext := year+1L]
  X[lk, next_state := i.state, on=.(oib, ynext=year)]
  X[is.na(next_state) & year>=2023, next_state:="cens"]
  X[is.na(next_state) & year==last_u & !is.na(brisan_year) & brisan_year<=year+3L, next_state:="Exit"]
  X[is.na(next_state) & year==last_u & is.na(brisan_year) & status %in% c("stečaj","likvidacija"), next_state:="Exit"]
  X[is.na(next_state) & year==last_u, next_state:="cens"]
  X[is.na(next_state) & year< last_u, next_state:="gap"]
  P <- X[year %in% wyears & state %in% c("H","Z") & next_state %in% c("H","Z","Exit")]
  M <- prop.table(table(P$state,P$next_state),1)*100
  # spells
  lkz <- X[, .(oib,year,zf=z)]; X[, yprev := year-1L]
  X[lkz, zprev := i.zf, on=.(oib, yprev=year)]
  X[, entry := z & (is.na(zprev)|zprev==FALSE)]
  X[, sid := cumsum(fifelse(is.na(entry),FALSE,entry))]
  zt <- X[z==TRUE]
  sp <- zt[, .(oib=oib[1], start=min(year), end=max(year), len=.N, lu=last_u[1], by_=brisan_year[1]), by=sid]
  sp[, ep1 := end+1L]; sp[lkz, nz := i.zf, on=.(oib, ep1=year)]
  sp[, sm1 := start-1L]; sp[lkz, pz := i.zf, on=.(oib, sm1=year)]
  sp[, incident := !is.na(pz) & pz==FALSE]
  sp[, recovered := !is.na(nz) & nz==FALSE]
  sp[, died := is.na(nz) & end==lu & !is.na(by_) & by_<=end+3L]
  sp[, event := as.integer(recovered|died)]
  inc <- sp[incident==TRUE]
  km <- NA; if (has_surv && nrow(inc)>0) km <- summary(survival::survfit(survival::Surv(len,event)~1,data=inc))$table["median"]
  latest <- X[year==2023, round(100*mean(z),1)]
  list(pZZ=round(M["Z","Z"],1), pZH=round(M["Z","H"],1), pZE=round(M["Z","Exit"],1),
       pHH=round(M["H","H"],1), km=km, n_inc=nrow(inc),
       rec=round(100*mean(inc$recovered),0), die=round(100*mean(inc$died),0),
       share2023=latest)
}

r_ne   <- analyze(BS, "z_ne")
r_core <- analyze(BS, "z_core")
r_hnb  <- analyze(BS, "z_hnb")

# ---- owner-loan guard: share of neg-equity firms that are ALSO loss-making, by year ----
guard <- afs[has_bs==TRUE & year>=2006, .(
  ne=round(100*mean(z_ne),1),
  core=round(100*mean(z_core),1),
  core_of_ne=round(100*sum(z_core)/sum(z_ne),0)), by=year][order(year)]

# ---- disjoint-cohort persistence test (negative equity) ----
cohort_pZZ <- function(D, zcol, yrs){
  X <- copy(D); X[, z:=as.logical(get(zcol))]; X[is.na(z),z:=FALSE]; X[, state:=fifelse(z,"Z","H")]
  lk<-X[,.(oib,year,state)]; X[,ynext:=year+1L]; X[lk,ns:=i.state,on=.(oib,ynext=year)]
  P<-X[year %in% yrs & state=="Z" & ns %in% c("H","Z")]; round(100*mean(P$ns=="Z"),1)
}
coh <- data.table(cohort=c("2005-2012 origins","2013-2020 origins"),
  pZZ_negeq=c(cohort_pZZ(BS,"z_ne",2005:2012), cohort_pZZ(BS,"z_ne",2013:2020)))

# ---- print ----
cat("############## TIGHTENED RESULTS (v4) ##############\n")
cat("\n== Robustness strip: three definitions, same panel ==\n")
mkrow <- function(name, r) data.table(definition=name, share_2023=r$share2023, `P_ZZ`=r$pZZ,
  `P_HH`=r$pHH, KM_median_yr=r$km, recovered_pct=r$rec, died_pct=r$die, n_spells=r$n_inc)
strip <- rbindlist(list(mkrow("Negative equity (headline)", r_ne),
                        mkrow("Neg equity + loss (hard core)", r_core),
                        mkrow("HNB imputed-rate", r_hnb)))
print(strip)

cat("\n== Owner-loan guard: how much of negative equity is ALSO loss-making? ==\n")
print(guard)

cat("\n== Disjoint-cohort persistence (should agree => not a panel-length artifact) ==\n")
print(coh)

fwrite(strip,"outputs/tables/zombie_v4_robustness_strip.csv")
fwrite(guard,"outputs/tables/zombie_v4_ownerloan_guard.csv")
fwrite(coh,"outputs/tables/zombie_v4_cohort_test.csv")
cat("\nsaved outputs/tables/zombie_v4_*.csv\n")
