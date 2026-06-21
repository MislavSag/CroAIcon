# Build the long-run Croatian GDP-per-capita series.
# Run: Rscript scripts/update_gdp.R
# All raw data stays out of git; only outputs/figures/*.png and the provenance
# json are produced (and the committed Tica CSV is the only data input in repo).

source(file.path("R", "00_config.R"))
source(file.path("R", "prepare_data.R")) # write_warehouse_table()
source(file.path("R", "charts.R"))
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

plot_data <- long[!is.na(long$index), , drop = FALSE]

# Hero chart: the whole arc.
if (nrow(plot_data)) {
  save_gdp_index_chart(
    plot_data,
    path = path_project("outputs", "figures", "gdp_long_index.png"),
    title = "Hrvatski BDP po stanovniku, 1870. do 2025.",
    subtitle = "Spojeni indeks, 2015. = 100  ·  pet padova, pet povrataka",
    caption = "Izvor: Eurostat, Maddison 2023, Tica (2004) / Good 1994, izračun AI.econ  ·  kružići = desetljetne procjene do 1910.  ·  sive trake = ratovi i krize",
    bands = list(
      list(from = 1914, to = 1919, label = "I. svj. rat"),
      list(from = 1940, to = 1946, label = "II. svj. rat"),
      list(from = 1991, to = 1995, label = "Domovinski rat"),
      list(from = 2009, to = 2014, label = "Fin. kriza"),
      list(from = 2019.5, to = 2020.5, label = "COVID")
    )
  )
}

# Growth by era (bars): the long-term growth-rate payload. Plot the five spans;
# also write the summary rates (pre-war pace, whole run) quoted in prose.
growth <- build_gdp_growth(long)
growth_summary <- build_gdp_growth_summary(long)
write_table_data(rbind(growth, growth_summary), path_project("outputs", "tables", "gdp_growth_eras.csv"))
save_gdp_growth_bars(
  growth,
  path = path_project("outputs", "figures", "gdp_growth_eras.png"),
  title = "Najbrži rast pod socijalizmom, dva razdoblja pada",
  subtitle = "Prosječni godišnji realni rast BDP-a po stanovniku, po razdoblju",
  caption = "Izvor: spojeni niz (Eurostat, Maddison, Tica), izračun AI.econ  ·  zeleno rast, crveno pad"
)

# Per-era zoom charts.
zoom <- function(y0, y1, file, title, subtitle, bands = list()) {
  if (!nrow(plot_data)) return(invisible(NULL))
  save_gdp_zoom_chart(
    plot_data, y0, y1,
    path = path_project("outputs", "figures", file),
    title = title, subtitle = subtitle,
    caption = "Spojeni indeks, 2015. = 100. Izvor kao na glavnom grafu.",
    bands = bands
  )
}
zoom(1870, 1952, "gdp_zoom_prewar.png",
     "Prije 1952.: nisko, ravno, isprekidano",
     "Indeks BDP-a po stanovniku  ·  desetljetne točke do 1910., ratne rupe",
     bands = list(
       list(from = 1914, to = 1919, label = "I. svj. rat"),
       list(from = 1940, to = 1946, label = "II. svj. rat")
     ))
zoom(1952, 1986, "gdp_zoom_socialism.png",
     "Socijalizam: najstrmiji uspon, pa zastoj 1980-ih",
     "Indeks BDP-a po stanovniku, 1952. do 1986.",
     bands = list(list(from = 1980, to = 1986, label = "zastoj 1980-ih")))
zoom(1986, 2000, "gdp_zoom_crisis1.png",
     "Prva kriza: duboki pad, pa spori oporavak",
     "Indeks BDP-a po stanovniku, 1986. do 2000.",
     bands = list(list(from = 1991, to = 1995, label = "Domovinski rat")))
zoom(2008, 2025, "gdp_zoom_crisis2.png",
     "Druga kriza pa COVID: plitko, dugo, pa uzlet",
     "Indeks BDP-a po stanovniku, 2008. do 2025.",
     bands = list(
       list(from = 2009, to = 2014, label = "Financijska kriza"),
       list(from = 2019.5, to = 2020.5, label = "COVID")
     ))

# Raw multi-source panel: each series in its own unit/base year. Shows how the
# independent sources corroborate the same shape (esp. the 1990s contraction).
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
    save_gdp_panels_chart(
      long_raw,
      path = path_project("outputs", "figures", "gdp_raw_panels.png"),
      title = "Isti oblik, više izvora",
      subtitle = "Svaki sirovi niz u vlastitoj jedinici i baznoj godini  ·  pad 1990-ih vidljiv u svima",
      caption = "Izvor: Eurostat, Maddison 2023, PWT 10.01, Svjetska banka, izračun AI.econ  ·  siva traka = 1991.–1995."
    )
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

# Sync the post's committed figure copies (outputs/figures is git-ignored, so the
# post folder holds the published copies). Keeps them fresh on every rerun.
post_dir <- path_project("posts", "2026-06-hrvatski-rast-dugi-niz")
if (dir.exists(post_dir)) {
  fig_copies <- list(
    c("gdp_long_index.png", "gdp_1_long_index.png"),
    c("gdp_growth_eras.png", "gdp_2_growth_eras.png"),
    c("gdp_zoom_prewar.png", "gdp_3_zoom_prewar.png"),
    c("gdp_zoom_socialism.png", "gdp_4_zoom_socialism.png"),
    c("gdp_zoom_crisis1.png", "gdp_5_zoom_crisis1.png"),
    c("gdp_zoom_crisis2.png", "gdp_6_zoom_crisis2.png"),
    c("gdp_raw_panels.png", "gdp_7_raw_panels.png")
  )
  for (fc in fig_copies) {
    src <- path_project("outputs", "figures", fc[[1]])
    if (file.exists(src)) file.copy(src, file.path(post_dir, fc[[2]]), overwrite = TRUE)
  }
}

message("GDP build complete: ", min(long$year), "-", max(long$year),
        " (", nrow(long), " years).")
