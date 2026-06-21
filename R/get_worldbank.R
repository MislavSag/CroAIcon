if (!exists("path_project")) {
  source(file.path("R", "00_config.R"))
}

# World Bank WDI -- optional cross-check only (Eurostat is the modern anchor).
# Croatia (HR/HRV) NY.GDP.PCAP.KD = GDP per capita, constant 2015 US$.
# Levels start 1990; the growth series (NY.GDP.MKTP.KD.ZG) starts 1991.
# Prefer the `WDI` package over `wbstats` (more widely used / maintained, 2026).
load_worldbank_hrv <- function(start = 1990) {
  require_package("WDI")

  d <- WDI::WDI(
    country = "HR",
    indicator = c(gdppc = "NY.GDP.PCAP.KD"),
    start = start
  )
  d <- d[!is.na(d$gdppc), , drop = FALSE]

  data.frame(
    year = as.integer(d$year),
    gdppc_wb = as.numeric(d$gdppc),
    stringsAsFactors = FALSE
  )
}
