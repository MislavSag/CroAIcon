# Build the long-run Croatian GDP-per-capita series and write the data tables the
# chart layer reads. Charts are rendered separately by python/gdp_charts.py
# (matplotlib, house style), mirroring the sectors build/charts split so the GDP
# post matches the look of the live posts.
#   Run: Rscript scripts/update_gdp.R        # data tables -> outputs/tables/
#   then: python python/gdp_charts.py        # charts -> drafts/.../gdp_*.png

source(file.path("R", "00_config.R"))
source(file.path("R", "prepare_data.R")) # write_warehouse_table()
source(file.path("R", "prepare_gdp.R"))

# Keep the eurostat package cache inside the git-ignored data tree.
dir_create(path_project("data", "raw", "eurostat"))
options(eurostat_cache_dir = path_project("data", "raw", "eurostat"))

long <- build_gdp_long(base_year = 2015)
raw <- build_gdp_raw()

write_table_data(long, path_project("data", "processed", "gdp_long.csv"))
if (nrow(raw)) {
  write_table_data(raw, path_project("data", "processed", "gdp_raw.csv"))
}

# Also publish the series under outputs/ so post numbers trace there (house rule).
write_table_data(long, path_project("outputs", "tables", "gdp_long.csv"))
if (nrow(raw)) {
  write_table_data(raw, path_project("outputs", "tables", "gdp_raw.csv"))
}

tryCatch(
  {
    write_warehouse_table("gdp_long", long)
    if (nrow(raw)) write_warehouse_table("gdp_raw", raw)
    message("Warehouse updated: gdp_long", if (nrow(raw)) ", gdp_raw" else "")
  },
  error = function(err) message("Warehouse skipped: ", conditionMessage(err))
)

# Growth by era: the five plotted spans (boom/crisis) for the bar chart, plus the
# summary rates (pre-war pace, whole run) quoted in prose.
growth <- build_gdp_growth(long)
growth_summary <- build_gdp_growth_summary(long)
write_table_data(rbind(growth, growth_summary), path_project("outputs", "tables", "gdp_growth_eras.csv"))
write_table_data(growth, path_project("outputs", "tables", "gdp_growth_bars.csv"))

# Uncertainty inputs, drawn into the charts rather than buried in the notes:
#   ribbon  = spread of the pre-1952 fan of estimates (sources diverge),
#   anchors = depth from each candidate peak 1986/1989/1990 (depends on the vrh),
#   depth   = the 1990s cross-source fall from 1990 (shared bias, not confirmation).
unc <- build_gdp_uncertainty(long)
if (!is.null(unc$ribbon)) write_table_data(unc$ribbon, path_project("outputs", "tables", "gdp_ribbon.csv"))
if (!is.null(unc$anchors)) write_table_data(unc$anchors, path_project("outputs", "tables", "gdp_anchors.csv"))
if (!is.null(unc$depth)) write_table_data(unc$depth, path_project("outputs", "tables", "gdp_depth.csv"))

# Raw multi-source panel data in long, labelled form, for the cross-check chart.
# Each series keeps its native unit/base year (never merge levels across sources).
if (nrow(raw)) {
  labels <- c(
    gdppc_modern_eur_clv = "Eurostat (EUR, 1995+)",
    gdppc_maddison_int2011 = "Maddison (2011 int$, 1952+)",
    gdppc_pwt_usd2017 = "PWT 10.01 (2017 US$, 1950+)",
    gdppc_wb_usd2015 = "World Bank (2015 US$, 1990+)",
    gdppc_tica = "Tica (indeks, 1910-1989)"
  )
  value_cols <- setdiff(names(raw), "year")
  long_raw <- do.call(rbind, lapply(value_cols, function(col) {
    sub <- raw[!is.na(raw[[col]]), c("year", col)]
    if (!nrow(sub)) return(NULL)
    data.frame(
      year = sub$year,
      source = if (!is.na(labels[col])) labels[[col]] else col,
      value = sub[[col]],
      stringsAsFactors = FALSE
    )
  }))
  if (!is.null(long_raw) && nrow(long_raw)) {
    write_table_data(long_raw, path_project("outputs", "tables", "gdp_raw_long.csv"))
  }
}

provenance <- list(
  title = "Long-run Croatian GDP per capita -- source provenance",
  generated_at = format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z"),
  base_year = 2015,
  segments = c(
    "tica 1910-1951 (transcribed; per-capita growth)",
    "maddison 1952-1994 (2011 int'l $; per-capita growth)",
    "eurostat 1995-present (chain-linked EUR per capita; anchor levels)"
  ),
  break_flagged = "1991-1995 war/transition (reconstructed, not observed)",
  rows_long = nrow(long),
  rows_raw = nrow(raw),
  year_min = min(long$year),
  year_max = max(long$year),
  registry = "data/reference/gdp_sources.json"
)
write_json(provenance, path_project("outputs", "facts", "gdp_provenance.json"))

message("GDP data build complete: ", min(long$year), "-", max(long$year),
        " (", nrow(long), " years). Now render charts: python python/gdp_charts.py")
