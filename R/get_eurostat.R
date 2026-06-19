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
