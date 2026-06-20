if (!exists("path_project")) {
  source(file.path("R", "00_config.R"))
}

# Penn World Table 10.01 (Feenstra, Inklaar & Timmer). CRAN package `pwt10`
# bundles the data in the R library, so nothing is downloaded or stored in repo.
# Croatia (HRV) coverage: 1950-2019. rgdpo/rgdpe are in millions of 2017 US$;
# pop is in millions, so rgdpo/pop is real GDP per capita in 2017 US$.
load_pwt_hrv <- function() {
  require_package("pwt10")

  env <- new.env()
  utils::data("pwt10.01", package = "pwt10", envir = env)
  d <- as.data.frame(env$pwt10.01)
  d <- d[d$isocode == "HRV" & !is.na(d$rgdpo), , drop = FALSE]

  data.frame(
    year = as.integer(d$year),
    gdppc_pwt = as.numeric(d$rgdpo) / as.numeric(d$pop),
    stringsAsFactors = FALSE
  )
}
