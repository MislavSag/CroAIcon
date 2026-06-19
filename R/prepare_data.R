if (!exists("path_project")) {
  source(file.path("R", "00_config.R"))
}

build_demo_dataset <- function() {
  data.frame(
    period = 2020:2025,
    index = c(100.0, 103.2, 108.5, 112.1, 116.4, 121.0),
    source = "synthetic",
    stringsAsFactors = FALSE
  )
}

build_example_facts <- function(data = build_demo_dataset()) {
  latest <- data[nrow(data), , drop = FALSE]
  first <- data[1, , drop = FALSE]
  total_change <- latest$index / first$index - 1

  list(
    title = "CroAIcon demo facts",
    generated_at = format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z"),
    source = "Synthetic example data for project verification only.",
    observation_count = nrow(data),
    first_period = first$period,
    latest_period = latest$period,
    first_index = first$index,
    latest_index = latest$index,
    total_change_pct = round(100 * total_change, 2),
    table = data
  )
}

write_warehouse_table <- function(
  name,
  data,
  db_path = path_project("data", "warehouse", "croaicon.duckdb"),
  overwrite = TRUE
) {
  require_package("DBI")
  require_package("duckdb")
  dir_create(dirname(db_path))

  con <- DBI::dbConnect(duckdb::duckdb(), dbdir = db_path)
  on.exit(DBI::dbDisconnect(con, shutdown = TRUE), add = TRUE)

  DBI::dbWriteTable(con, name, data, overwrite = overwrite)
  invisible(db_path)
}
