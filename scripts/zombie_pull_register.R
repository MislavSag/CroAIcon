# Pull the register (status/death/county/capital) and run quick availability checks for the
# other perspectives: (a) is negative equity computable among ACTIVE firms? (b) how prevalent
# and persistent are dormant shells (registered, zero activity)?
suppressWarnings(suppressMessages({library(DBI); library(RMySQL); library(data.table)}))
read_env <- function(path){ln<-readLines(path,warn=FALSE);ln<-ln[nzchar(trimws(ln))&!startsWith(trimws(ln),"#")&grepl("=",ln)]
  kv<-strsplit(ln,"=",fixed=TRUE);setNames(trimws(vapply(kv,function(x)paste(x[-1],collapse="="),"")),trimws(vapply(kv,`[`,"",1)))}
e <- read_env("c:/Users/lukas/Dropbox/AI.econ/CroAIcon/.env")
con <- dbConnect(RMySQL::MySQL(), host=e[["GFI_DB_HOST"]], port=as.integer(e[["GFI_DB_PORT"]]),
                 user=e[["GFI_DB_USER"]], password=e[["GFI_DB_PASSWORD"]], dbname=e[["GFI_DB_NAME"]])
on.exit(dbDisconnect(con)); dbSendQuery(con,"SET NAMES utf8")

## --- (a) negative equity among ACTIVE firms (db_afs, verified codebook: b065 assets, b067 equity) ---
cat("== db_afs: balance-sheet availability among firms WITH operating revenue ==\n")
q <- "SELECT reportyear,
        COUNT(*) n_active,
        ROUND(AVG(b065>0),3) assets_pos,
        ROUND(AVG(b067<0),4)  equity_neg,
        ROUND(AVG(b067=0),3)  equity_zero
      FROM db_afs WHERE reportyear IN (2015,2018,2022) AND b125>0
      GROUP BY reportyear"
print(dbGetQuery(con,q))

## --- (b) dormancy prevalence in db_afs (zero revenue AND zero expense) ---
cat("\n== db_afs: dormant-shell prevalence (op_rev=0 & op_exp=0) by year ==\n")
q2 <- "SELECT reportyear, COUNT(*) n,
         ROUND(AVG(b125=0 AND b131=0),3) dormant_share,
         ROUND(AVG(b125=0),3) norev_share
       FROM db_afs WHERE reportyear IN (2008,2012,2016,2020,2023) GROUP BY reportyear"
print(dbGetQuery(con,q2))

## --- pull register ---
cat("\npulling register ...\n")
reg <- setDT(dbGetQuery(con, "
  SELECT oib, status, is_active, datum_brisanja, zupanija, nkd2007,
         godina_osnivanja AS founding_year, temeljni_kapital
  FROM subjekti_current"))
reg[, oib := as.character(oib)]
reg[, brisan_year := suppressWarnings(as.integer(substr(as.character(datum_brisanja),1,4)))]
cat(sprintf("register rows: %s | with deletion date: %s | active(1): %s\n",
    format(nrow(reg),big.mark=","), format(sum(!is.na(reg$brisan_year)),big.mark=","),
    format(sum(reg$is_active==1,na.rm=TRUE),big.mark=",")))
cat("\nstatus distribution:\n"); print(reg[, .N, by=status][order(-N)])

saveRDS(reg, "data/raw/zombie_register.rds")
cat("\nsaved data/raw/zombie_register.rds\n")
