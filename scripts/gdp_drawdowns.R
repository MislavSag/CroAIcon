# Census of every peak-to-trough drawdown in the spliced GDP-per-capita index,
# computed from outputs/tables/gdp_long.csv so the post's crisis numbers trace
# here. War gaps split the annual series into runs; an episode never spans a
# gap, so the two war holes stay holes rather than fake drawdowns.
#   Run: Rscript scripts/gdp_drawdowns.R    # -> outputs/tables/gdp_drawdowns.csv

source(file.path("R", "00_config.R"))

long <- utils::read.csv(path_project("outputs", "tables", "gdp_long.csv"))
ann <- long[long$granularity == "annual", c("year", "index")]
ann <- ann[order(ann$year), ]

run_id <- cumsum(c(1, diff(ann$year) > 1))
episodes <- list()

for (id in unique(run_id)) {
  seg <- ann[run_id == id, ]
  peak_i <- 1
  i <- 2
  while (i <= nrow(seg)) {
    if (seg$index[i] >= seg$index[peak_i]) {
      peak_i <- i
      i <- i + 1
      next
    }
    rec_i <- NA_integer_
    j <- i
    while (j <= nrow(seg)) {
      if (seg$index[j] >= seg$index[peak_i]) {
        rec_i <- j
        break
      }
      j <- j + 1
    }
    below <- seg[i:(if (is.na(rec_i)) nrow(seg) else rec_i - 1), ]
    tr_i <- which.min(below$index)
    episodes[[length(episodes) + 1]] <- data.frame(
      peak_year = seg$year[peak_i],
      peak_index = round(seg$index[peak_i], 2),
      trough_year = below$year[tr_i],
      trough_index = round(below$index[tr_i], 2),
      fall_pct = round(100 * (below$index[tr_i] / seg$index[peak_i] - 1), 1),
      recovery_year = if (is.na(rec_i)) NA_integer_ else seg$year[rec_i],
      recovery_years = if (is.na(rec_i)) NA_integer_ else seg$year[rec_i] - seg$year[peak_i]
    )
    if (is.na(rec_i)) break
    peak_i <- rec_i
    i <- rec_i + 1
  }
}

draw <- do.call(rbind, episodes)
draw$major <- draw$fall_pct <= -7  # the bar at which the post counts a pad
write_table_data(draw, path_project("outputs", "tables", "gdp_drawdowns.csv"))
message("gdp_drawdowns: ", nrow(draw), " episodes -> outputs/tables/gdp_drawdowns.csv")
