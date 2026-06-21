if (!exists("path_project")) {
  source(file.path("R", "00_config.R"))
}

fetch_eurostat_dataset <- function(dataset, filters = list(), time_format = "num", cache = TRUE) {
  require_package("eurostat")

  eurostat::get_eurostat(
    id = dataset,
    filters = filters,
    time_format = time_format,
    cache = cache
  )
}

cache_eurostat_dataset <- function(
  dataset,
  filters = list(),
  output = path_project("data", "raw", "eurostat", paste0(dataset, ".rds")),
  time_format = "num",
  cache = TRUE
) {
  data <- fetch_eurostat_dataset(
    dataset = dataset,
    filters = filters,
    time_format = time_format,
    cache = cache
  )

  write_table_data(as.data.frame(data), output)
  invisible(output)
}

# Modern official real GDP per capita for Croatia (ESA 2010), 1995-present.
# Dataset nama_10_pc, GDP at market prices (B1GQ), chain-linked volume per
# capita in euro. The chain-link reference year migrates over time (2010 -> 2015
# -> 2020), so pick whichever CLV*_EUR_HAB unit is actually populated for HR,
# preferring the most recent reference year. This is the splice ANCHOR.
load_gdp_modern_hrv <- function() {
  raw <- as.data.frame(fetch_eurostat_dataset(
    "nama_10_pc",
    filters = list(geo = "HR", na_item = "B1GQ")
  ))

  prefer <- c("CLV20_EUR_HAB", "CLV15_EUR_HAB", "CLV10_EUR_HAB")
  available <- unique(as.character(raw$unit))
  unit_pick <- prefer[prefer %in% available][1]
  if (is.na(unit_pick)) {
    stop(
      sprintf(
        "No chain-linked per-capita euro unit in nama_10_pc for HR. Available: %s",
        paste(available, collapse = ", ")
      ),
      call. = FALSE
    )
  }

  d <- raw[as.character(raw$unit) == unit_pick & !is.na(raw$values), , drop = FALSE]

  year_raw <- if (!is.null(d[["time"]])) d[["time"]] else d[["TIME_PERIOD"]]
  year <- suppressWarnings(as.integer(substr(as.character(year_raw), 1, 4)))

  out <- data.frame(
    year = year,
    gdppc_modern = as.numeric(d$values),
    unit = unit_pick,
    stringsAsFactors = FALSE
  )
  out[order(out$year), , drop = FALSE]
}
