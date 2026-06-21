if (!exists("path_project")) {
  source(file.path("R", "00_config.R"))
}

# Tica (2004), "The Estimation of 1910-1989 Per Capita GDP in Croatia",
# Zagreb Int. Review of Economics & Business 7(1):103-133. Open PDF:
# https://hrcak.srce.hr/35610
#
# This is the ONLY long-run source for Croatia before 1952, and it exists only
# as a PDF appendix -- it cannot be fetched. The transcribed values live in a
# small committed CSV (the one data exception in this repo). Until the appendix
# is transcribed, the file holds empty values and the long index simply starts
# at 1952 (Maddison) instead of 1910.
tica_path <- function() {
  path_project("data", "reference", "tica_2004_gdppc.csv")
}

# Pre-1910 DECADAL benchmark estimates (1870, 1880, 1890, 1900) from Tica's GVSM
# series, which adopts the Good (1994) benchmarks. Same unit (1990 GK $) as the
# annual Tica series, so they chain on the same scale. These are benchmarks, not
# annual data -- render them as such.
load_tica_benchmarks <- function(path = tica_xlsx_path()) {
  require_package("readxl")
  g <- as.data.frame(readxl::read_excel(path, sheet = "GVSM_annual_series"))
  g <- g[g$year < 1910 & !is.na(g$gdppc_1990gk), , drop = FALSE]
  data.frame(
    year = as.integer(g$year),
    gdppc_tica = as.numeric(g$gdppc_1990gk),
    stringsAsFactors = FALSE
  )
}

load_tica <- function(path = tica_path()) {
  if (!file.exists(path)) {
    stop(sprintf("Tica reference file missing: %s", path), call. = FALSE)
  }

  d <- read_table_data(path)
  d <- d[!is.na(d$gdppc_tica), , drop = FALSE]

  data.frame(
    year = as.integer(d$year),
    gdppc_tica = as.numeric(d$gdppc_tica),
    stringsAsFactors = FALSE
  )
}

# The ten alternative pre-1952 estimates from Tica (2004), tables 8/11/12
# (extrapolated and original Vinski / Stajic / Cobeljic / Maddison, SA and RA
# growth), all in 1990 GK dollars and so directly comparable, plus the chosen
# GVSM series. Returns long form (year, estimate, value, chosen) for 1910-1958.
# Used to show the early history rests on a fan of estimates, not one guess.
tica_xlsx_path <- function() {
  path_project("data", "reference", "Tica_2004_Croatia_GDP_data.xlsx")
}

load_tica_estimates <- function(path = tica_xlsx_path()) {
  require_package("readxl")
  rd <- function(sheet) as.data.frame(readxl::read_excel(path, sheet = sheet))

  gvsm <- rd("GVSM_annual_series")
  parts <- list(
    data.frame(year = gvsm$year, GVSM = gvsm$gdppc_1990gk),
    rd("T8_SA_est_1910_1952"),
    rd("T11_RA_est_1910_1958"),
    rd("T12_orig_gr_est_1910_1958")
  )
  m <- Reduce(function(a, b) merge(a, b, by = "year", all = TRUE), parts)
  m <- m[m$year >= 1910 & m$year <= 1958, , drop = FALSE]

  cols <- setdiff(names(m), "year")
  out <- do.call(rbind, lapply(cols, function(col) {
    sub <- m[!is.na(m[[col]]), c("year", col)]
    if (!nrow(sub)) return(NULL)
    data.frame(
      year = as.integer(sub$year),
      estimate = col,
      value = as.numeric(sub[[col]]),
      chosen = identical(col, "GVSM"),
      stringsAsFactors = FALSE
    )
  }))
  out
}
