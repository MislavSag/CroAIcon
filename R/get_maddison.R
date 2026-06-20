if (!exists("path_project")) {
  source(file.path("R", "00_config.R"))
}

# Maddison Project Database 2023 (Bolt & van Zanden 2024, J. Econ. Surveys).
# DOI 10.34894/INZBF2. Dataverse datafile id 421302 -> mpd2023_web.xlsx.
# NOTE: download with GET (download.file). A HEAD request 403s on the signed URL.
maddison_url <- "https://dataverse.nl/api/access/datafile/421302"

cache_maddison <- function(
  output = path_project("data", "raw", "maddison", "mpd2023.xlsx"),
  url = maddison_url,
  force = FALSE
) {
  dir_create(dirname(output))
  if (force || !file.exists(output)) {
    utils::download.file(url, output, mode = "wb", quiet = TRUE)
  }
  invisible(output)
}

# Croatia (HRV) real GDP per capita in 2011 international (PPP) dollars.
# Verified coverage: the gdppc column is non-null only 1952-2022. There is NO
# pre-WWII Maddison level for Croatia, so Maddison is the socialist-era + modern
# bridge, never the pre-1952 source.
#
# Alternative offline path: the CRAN package `MaddisonData` (v1.1.0) bundles the
# same 2023 release inside the R library (nothing downloaded, nothing in repo).
# It is left as an opt-in below; the xlsx path is the verified default.
load_maddison_hrv <- function(path = cache_maddison()) {
  require_package("readxl")

  raw <- as.data.frame(readxl::read_excel(path, sheet = "Full data"))
  raw <- raw[raw$countrycode == "HRV" & !is.na(raw$gdppc), , drop = FALSE]

  data.frame(
    year = as.integer(raw$year),
    gdppc_maddison = as.numeric(raw$gdppc),
    pop_maddison = as.numeric(raw$pop),
    stringsAsFactors = FALSE
  )
}
