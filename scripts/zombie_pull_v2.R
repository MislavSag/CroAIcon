# CLEAN pull on the VERIFIED physical columns (see _workflow/gfi-variable-map.md).
# b110 revenue, b113 op expenses, b061 assets, b063 equity, b108 pasiva,
# b152 profit / b153 loss (net = b152-b153), b002 fixed assets,
# b086+b087 LT financial debt, b096+b097 ST financial debt.
suppressWarnings(suppressMessages({library(DBI); library(RMySQL); library(data.table)}))
read_env <- function(path){ln<-readLines(path,warn=FALSE);ln<-ln[nzchar(trimws(ln))&!startsWith(trimws(ln),"#")&grepl("=",ln)]
  kv<-strsplit(ln,"=",fixed=TRUE);setNames(trimws(vapply(kv,function(x)paste(x[-1],collapse="="),"")),trimws(vapply(kv,`[`,"",1)))}
e <- read_env("c:/Users/lukas/Dropbox/AI.econ/CroAIcon/.env")
con <- dbConnect(RMySQL::MySQL(), host=e[["GFI_DB_HOST"]], port=as.integer(e[["GFI_DB_PORT"]]),
                 user=e[["GFI_DB_USER"]], password=e[["GFI_DB_PASSWORD"]], dbname=e[["GFI_DB_NAME"]])
on.exit(dbDisconnect(con)); dbSendQuery(con,"SET NAMES utf8")

message("pulling db_afs on verified columns, 2002-2024 ...")
afs <- setDT(dbGetQuery(con, "
  SELECT subjecttaxnoid AS oib, reportyear AS year, nacerev21 AS nace,
         countyid AS county, subjectsizeeurev2 AS size_cls,
         employeecounteop AS emp, foreigncontrol AS foreign_ctrl,
         b110 AS revenue, b113 AS opex, b061 AS assets, b063 AS equity, b108 AS pasiva,
         b152 AS profit, b153 AS loss, b002 AS fixed_assets,
         b086 AS lt_fd1, b087 AS lt_fd2, b096 AS st_fd1, b097 AS st_fd2
  FROM db_afs WHERE reportyear >= 2002"))
message(sprintf("  rows: %s", format(nrow(afs), big.mark=",")))

numc <- setdiff(names(afs), c("oib","nace"))
afs[, (numc) := lapply(.SD, as.numeric), .SDcols = numc]
afs[, oib := as.character(oib)]

# quick self-check vs the verified anchor (2019 non-fin revenue ~ €105bn, neg-equity ~28-32%)
chk <- afs[year==2019 & nace!="K" & grepl("^[A-U]$", nace),
           .(rev_bn=round(sum(revenue,na.rm=TRUE)/1e9,1),
             rev_cov=round(mean(revenue>0,na.rm=TRUE),3),
             negeq=round(mean(equity<0 & assets>0, na.rm=TRUE),3))]
print(chk)

saveRDS(afs, "data/raw/zombie_extract_v2.rds")
message("saved data/raw/zombie_extract_v2.rds")
