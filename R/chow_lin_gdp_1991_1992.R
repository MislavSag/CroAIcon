# Chow-Lin temporal disaggregation of annual GDP to monthly, 1991-1992, using
# observed monthly industrial production (HNB Tablica 2) as the indicator.
#
# Purpose: a common-sense check on the early-1990s GDP reconstruction. The annual
# series for 1991-1995 is reconstructed (Maddison growth rates), not observed
# national accounts (see R/prepare_gdp.R, break_period). Industrial production is
# a hard, observed monthly indicator. Spreading annual GDP along its profile lets
# us look at WHEN the economy fell inside the year and ask whether the implied
# path and magnitude sit consistently with the reconstructed annual numbers.
#
# One job: read inputs, disaggregate, write the table/facts/figure that the
# writeup (research/chowlin_gdp_check_1991_1992.md) reads. No numbers hardcoded
# downstream.

if (!exists("path_project")) {
  source(file.path("R", "00_config.R"))
}
source(path_project("R", "house_style.R"))

suppressPackageStartupMessages({
  require_package("ggplot2")
  library(ggplot2)
})

# --- Inputs -------------------------------------------------------------------

ipi_raw <- read_table_data(
  path_project("data", "reference", "hnb_industrijska_proizvodnja_1991_1992.csv")
)

# Monthly industrial-production LEVEL index, 1990 = 100. idx1990_orig is the
# percent deviation of the level from the 1990 average, so level = 100 + it.
ipi <- data.frame(
  year = ipi_raw$year,
  month = ipi_raw$month,
  ipi_1990_100 = 100 + ipi_raw$idx1990_orig
)
ipi <- ipi[order(ipi$year, ipi$month), , drop = FALSE]
ipi$date <- as.Date(sprintf("%d-%02d-01", ipi$year, ipi$month))

# Annual GDP per capita to disaggregate: the reconstructed backbone (Maddison,
# 2011 international $). 1990 is kept only as the indexing base / out-of-sample
# check; the disaggregation targets the two years the indicator covers.
gdp_raw <- read_table_data(path_project("data", "processed", "gdp_raw.csv"))
annual_col <- "gdppc_maddison_int2011"
g <- function(y) gdp_raw[[annual_col]][gdp_raw$year == y]
G1990 <- g(1990); G1991 <- g(1991); G1992 <- g(1992)
stopifnot(length(c(G1990, G1991, G1992)) == 3, all(is.finite(c(G1990, G1991, G1992))))

# --- Chow-Lin disaggregation --------------------------------------------------
# Chow-Lin (1971): annual GDP = a + b*IPI + u, high-frequency u ~ AR(1); GLS for
# (a, b), then the BLUE distribution back to monthly subject to the annual totals
# (conversion = sum: GDP is a flow, the 12 months sum to the year).
#
# Here the indicator covers only 1991-1992 -> two annual benchmarks, two
# parameters. The model is exactly identified: the two annual residuals are zero,
# the AR(1) term drops out, and the estimator reduces to the indicator linearly
# rescaled to hit the two annual totals. That is the Chow-Lin solution in this
# case, not a shortcut. We compute it in closed form and (below) confirm it
# against tempdisagg::td().

S1 <- sum(ipi$ipi_1990_100[ipi$year == 1991])   # annual sum of the monthly indicator
S2 <- sum(ipi$ipi_1990_100[ipi$year == 1992])
b  <- (G1991 - G1992) / (S1 - S2)
a  <- (G1991 - b * S1) / 12                       # intercept per month

ipi$gdp_pc_monthly <- a + b * ipi$ipi_1990_100    # monthly GDP pc (flow, sums to annual)

# Index monthly GDP to 1990 = 100 using the 1990 monthly average (annual / 12).
base_1990_monthly <- G1990 / 12
ipi$gdp_idx_1990_100 <- ipi$gdp_pc_monthly / base_1990_monthly * 100

# --- Verify the annual totals reproduce ---------------------------------------
sum_1991 <- sum(ipi$gdp_pc_monthly[ipi$year == 1991])
sum_1992 <- sum(ipi$gdp_pc_monthly[ipi$year == 1992])
stopifnot(
  abs(sum_1991 - G1991) < 1e-6,
  abs(sum_1992 - G1992) < 1e-6
)
message(sprintf("Annual totals reproduced: 1991 %.1f (=%.1f), 1992 %.1f (=%.1f)",
                sum_1991, G1991, sum_1992, G1992))

# --- Cross-check against tempdisagg::td() (if available) ----------------------
td_max_abs_diff <- NA_real_
if (requireNamespace("tempdisagg", quietly = TRUE)) {
  td_diff <- tryCatch({
    gdp_lf <- stats::ts(c(G1991, G1992), start = 1991, frequency = 1)
    ipi_hf <- stats::ts(ipi$ipi_1990_100, start = c(1991, 1), frequency = 12)
    m <- tempdisagg::td(gdp_lf ~ ipi_hf, conversion = "sum",
                        method = "chow-lin-maxlog")
    max(abs(as.numeric(stats::predict(m)) - ipi$gdp_pc_monthly))
  }, error = function(e) {
    message("tempdisagg cross-check skipped: ", conditionMessage(e))
    NA_real_
  })
  td_max_abs_diff <- td_diff
  if (is.finite(td_max_abs_diff)) {
    message(sprintf("tempdisagg cross-check: max abs diff = %.3e (should be ~0)",
                    td_max_abs_diff))
  }
}

# --- Common-sense-check numbers -----------------------------------------------
ipi_avg <- function(y) mean(ipi$ipi_1990_100[ipi$year == y])
ipi_1991_avg <- ipi_avg(1991); ipi_1992_avg <- ipi_avg(1992)

# Out-of-sample: does the IPI->GDP line fitted on 1991-1992 recover 1990?
pred_1990_monthly <- a + b * 100                  # IPI = 100 is the 1990 average
pred_1990_annual  <- pred_1990_monthly * 12
pred_1990_err_pct <- 100 * (pred_1990_annual / G1990 - 1)

# Falls 1990 -> 1992 (annual), and the GDP "beta" to industry over that span.
ipi_fall_pct <- 100 * (ipi_1992_avg / 100 - 1)
gdp_fall_pct <- 100 * (G1992 / G1990 - 1)
gdp_beta_to_industry <- gdp_fall_pct / ipi_fall_pct

# Troughs (deepest month on each 1990=100 index).
gdp_trough <- ipi[which.min(ipi$gdp_idx_1990_100), ]
ipi_trough <- ipi[which.min(ipi$ipi_1990_100), ]

# --- Outputs ------------------------------------------------------------------
out_tbl <- ipi[, c("year", "month", "date", "ipi_1990_100",
                   "gdp_pc_monthly", "gdp_idx_1990_100")]
out_tbl$ipi_1990_100   <- round(out_tbl$ipi_1990_100, 1)
out_tbl$gdp_pc_monthly <- round(out_tbl$gdp_pc_monthly, 1)
out_tbl$gdp_idx_1990_100 <- round(out_tbl$gdp_idx_1990_100, 1)
write_table_data(out_tbl,
                 path_project("outputs", "tables", "gdp_monthly_chowlin_1991_1992.csv"))

facts <- list(
  method = "Chow-Lin temporal disaggregation (annual -> monthly), indicator = HNB monthly industrial production (1990=100)",
  target = "annual GDP per capita, Maddison 2011 international $ (reconstructed backbone)",
  n_annual_benchmarks = 2L,
  note = "Two benchmarks, two parameters -> exactly identified; AR(1) drops out, estimate = indicator linearly rescaled to the annual totals.",
  fit_intercept_a_monthly = round(a, 2),
  fit_slope_b = round(b, 4),
  annual_totals = list(
    gdp_1991 = round(G1991, 1), reproduced_1991 = round(sum_1991, 1),
    gdp_1992 = round(G1992, 1), reproduced_1992 = round(sum_1992, 1)
  ),
  out_of_sample_1990 = list(
    actual_annual = round(G1990, 1),
    predicted_annual = round(pred_1990_annual, 1),
    error_pct = round(pred_1990_err_pct, 2)
  ),
  industry_vs_gdp = list(
    ipi_avg_1991 = round(ipi_1991_avg, 1), ipi_avg_1992 = round(ipi_1992_avg, 1),
    ipi_fall_1990_1992_pct = round(ipi_fall_pct, 1),
    gdp_fall_1990_1992_pct = round(gdp_fall_pct, 1),
    gdp_beta_to_industry = round(gdp_beta_to_industry, 2)
  ),
  gdp_trough = list(year = gdp_trough$year, month = gdp_trough$month,
                    idx_1990_100 = round(gdp_trough$gdp_idx_1990_100, 1)),
  ipi_trough = list(year = ipi_trough$year, month = ipi_trough$month,
                    idx_1990_100 = round(ipi_trough$ipi_1990_100, 1)),
  tempdisagg_max_abs_diff = if (is.finite(td_max_abs_diff)) signif(td_max_abs_diff, 3) else NA
)
write_json(facts, path_project("outputs", "facts", "chowlin_check_1991_1992.json"))

# --- Figure: monthly GDP path over observed industrial production -------------
plot_df <- rbind(
  data.frame(date = ipi$date, value = ipi$ipi_1990_100,
             series = "Industrijska proizvodnja (promatrano)"),
  data.frame(date = ipi$date, value = ipi$gdp_idx_1990_100,
             series = "BDP, mjesecno (Chow-Lin)")
)
annual_pts <- data.frame(
  date = as.Date(c("1991-07-01", "1992-07-01")),
  value = c(G1991 / G1990 * 100, G1992 / G1990 * 100)
)

p <- ggplot(plot_df, aes(date, value, color = series)) +
  geom_hline(yintercept = 100, color = house_pal$muted, linewidth = 0.3, linetype = "dashed") +
  geom_line(linewidth = 0.9) +
  geom_point(data = annual_pts, aes(date, value), inherit.aes = FALSE,
             color = house_pal$ink, size = 2.2) +
  geom_text(data = annual_pts, aes(date, value,
            label = sprintf("godisnji BDP %.0f", value)), inherit.aes = FALSE,
            color = house_pal$ink, vjust = -1.1, size = 3, family = "mono") +
  scale_color_manual(values = c(
    "Industrijska proizvodnja (promatrano)" = house_pal$fall,
    "BDP, mjesecno (Chow-Lin)" = house_pal$accent)) +
  scale_y_continuous(limits = c(50, 105)) +
  labs(
    title = "BDP je pao blaze nego industrija, ali u istom ritmu",
    subtitle = "Indeks, 1990 = 100. Mjesecni BDP dobiven Chow-Lin razdvajanjem godisnjeg BDP-a\nuz mjesecnu industrijsku proizvodnju (HNB) kao indikator. Tocke = godisnji BDP.",
    caption = "Izvori: industrija HNB (DZS), godisnji BDP Maddison 2023. Razdvajanje 1991-1992, dva godisnja sidra.",
    color = NULL
  ) +
  theme_house() +
  theme(legend.position = "top", legend.text = element_text(size = 9))

ggsave(path_project("outputs", "figures", "gdp_vs_ipi_monthly_1991_1992.png"),
       p, width = 9, height = 5.4, dpi = 200, bg = house_pal$paper)

message("Done. Wrote table, facts JSON, and figure under outputs/.")
