source(file.path("R", "00_config.R"))
source(file.path("R", "prepare_data.R"))
source(file.path("R", "charts.R"))
source(file.path("R", "tables.R"))

dir_create(path_project("data", "processed"))
dir_create(path_project("outputs", "facts"))
dir_create(path_project("outputs", "figures"))
dir_create(path_project("outputs", "tables"))

demo <- build_demo_dataset()
facts <- build_example_facts(demo)

write_table_data(demo, path_project("data", "processed", "example_macro.csv"))
write_json(facts, path_project("outputs", "facts", "example_facts.json"))
write_markdown_table(demo, path_project("outputs", "tables", "example_macro.md"))
save_line_chart(
  demo,
  x = "period",
  y = "index",
  path = path_project("outputs", "figures", "example_macro_index.png"),
  title = "Primjer indeksa",
  subtitle = "Sintetički podaci za provjeru projekta"
)

tryCatch(
  {
    write_warehouse_table("example_macro", demo)
    message("DuckDB warehouse updated: data/warehouse/croaicon.duckdb")
  },
  error = function(err) {
    message("DuckDB warehouse skipped: ", conditionMessage(err))
  }
)

tryCatch(
  source(path_project("scripts", "update_gdp.R")),
  error = function(err) message("GDP update skipped: ", conditionMessage(err))
)

message("Data update completed.")

