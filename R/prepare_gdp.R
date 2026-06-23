if (!exists("path_project")) {
  source(file.path("R", "00_config.R"))
}

# Source the per-source loaders.
local({
  modules <- c("get_eurostat.R", "get_maddison.R", "get_pwt.R", "get_tica.R", "get_worldbank.R")
  for (m in modules) {
    fp <- path_project("R", m)
    if (file.exists(fp)) source(fp)
  }
})

# --- Splicing -----------------------------------------------------------------
# Chain an older per-capita series onto an anchor at a common overlap year,
# PRESERVING the older series' growth rates (no raw-level substitution). This is
# the ratio/chain-link splice: rescale the older series by anchor/older at the
# overlap year, then keep only the older years strictly before the overlap.
#
# Why not COALESCE(modern, tica, maddison)? The three series use different
# yardsticks (Maddison 2011 int'l $, Eurostat chain-linked EUR, Tica its own
# base), so stacking raw levels injects fake jumps at every junction. We work
# entirely in per-capita terms so growth rates are commensurable.
chain_back <- function(anchor, older, overlap_year) {
  a <- anchor$value[anchor$year == overlap_year]
  o <- older$value[older$year == overlap_year]
  if (length(a) != 1 || length(o) != 1 || is.na(a) || is.na(o) || o == 0) {
    stop(sprintf("No usable overlap at %s for chaining.", overlap_year), call. = FALSE)
  }

  scale <- a / o
  pre <- older[older$year < overlap_year & !is.na(older$value), , drop = FALSE]
  if (!nrow(pre)) {
    return(anchor)
  }

  rbind(
    data.frame(year = pre$year, value = pre$value * scale, stringsAsFactors = FALSE),
    anchor
  )
}

# Build the spliced long per-capita series:
#   1995-present : Eurostat (anchor, published levels)
#   1952-1994    : Maddison growth rates (bridges socialist era + 1990s war)
#   1910-1951    : Tica growth rates (its unique contribution), if transcribed
build_gdp_long <- function(base_year = 2015) {
  modern <- load_gdp_modern_hrv()
  mad <- load_maddison_hrv()

  modern_v <- data.frame(year = modern$year, value = modern$gdppc_modern, stringsAsFactors = FALSE)
  mad_v <- data.frame(year = mad$year, value = mad$gdppc_maddison, stringsAsFactors = FALSE)

  overlap_mad <- min(intersect(modern_v$year, mad_v$year))
  long <- chain_back(modern_v, mad_v, overlap_mad)
  long$segment <- ifelse(long$year >= min(modern_v$year), "modern", "maddison")

  # Extend with Tica before Maddison starts, only if the appendix is transcribed.
  # Annual 1910-1951 plus the pre-1910 decadal benchmarks (1870-1900), all in the
  # same 1990 GK unit so they chain on one scale at the 1952 overlap.
  tica <- tryCatch(load_tica(), error = function(e) NULL)
  if (!is.null(tica) && nrow(tica)) {
    bench <- tryCatch(load_tica_benchmarks(), error = function(e) NULL)
    tica_all <- tica[, c("year", "gdppc_tica")]
    if (!is.null(bench) && nrow(bench)) {
      tica_all <- rbind(bench[, c("year", "gdppc_tica")], tica_all)
    }
    tica_v <- data.frame(year = tica_all$year, value = tica_all$gdppc_tica, stringsAsFactors = FALSE)

    overlap_tica <- min(intersect(long$year, tica_v$year))
    chained <- chain_back(long[, c("year", "value")], tica_v, overlap_tica)
    added <- chained[chained$year < overlap_tica, , drop = FALSE]
    if (nrow(added)) {
      added$segment <- "tica"
      long <- rbind(added, long)
    }
  } else {
    message("Tica not transcribed yet -- long index starts at ", min(long$year), ".")
  }

  long <- long[order(long$year), , drop = FALSE]
  # Granularity: pre-1910 are decadal benchmarks, 1910+ are annual.
  long$granularity <- ifelse(long$year < 1910, "benchmark", "annual")

  base_val <- long$value[long$year == base_year]
  long$index <- if (length(base_val) == 1 && !is.na(base_val)) {
    long$value / base_val * 100
  } else {
    NA_real_
  }

  # 1991-1995: war/transition. Maddison covers these years but they are
  # reconstructed, not observed national accounts -> flag, do not hide.
  long$break_period <- long$year >= 1991 & long$year <= 1995
  rownames(long) <- NULL
  long
}

# Wide table of every raw source, aligned by year, for the "raw view" panel.
# Each column keeps its native unit/base year in the name -- never merge levels.
build_gdp_raw <- function() {
  grab <- function(expr, year_col, val_name) {
    tryCatch(
      {
        d <- expr
        out <- data.frame(year = d$year, stringsAsFactors = FALSE)
        out[[val_name]] <- d[[year_col]]
        out
      },
      error = function(e) NULL
    )
  }

  parts <- list(
    grab(load_gdp_modern_hrv(), "gdppc_modern", "gdppc_modern_eur_clv"),
    grab(load_maddison_hrv(), "gdppc_maddison", "gdppc_maddison_int2011"),
    grab(load_pwt_hrv(), "gdppc_pwt", "gdppc_pwt_usd2017"),
    grab(load_worldbank_hrv(), "gdppc_wb", "gdppc_wb_usd2015"),
    grab(load_tica(), "gdppc_tica", "gdppc_tica")
  )
  parts <- Filter(Negate(is.null), parts)
  if (!length(parts)) {
    return(data.frame())
  }

  out <- Reduce(function(a, b) merge(a, b, by = "year", all = TRUE), parts)
  out[order(out$year), , drop = FALSE]
}

# Uncertainty inputs for the honesty layer of the hero/zoom charts. The point is
# to DRAW the soft ground into the graphic, not bury it in the notes.
#
# Returns a list with:
#   ribbon  : year, lo, hi -- the spread of Tica's (2004) fan of pre-1952
#             estimates (10+ alternative reconstructions, tables 8/11/12 + GVSM),
#             mapped into the spliced index's units. This is the "sources
#             diverge" band for the interwar/early stretch.
#   depth   : per cross-source fall 1990 -> trough (Maddison, PWT, World Bank),
#             plus the trough placed on the spliced index. They agree on the
#             DIRECTION and rough timing; the tight cluster is shared bias, not
#             independent confirmation of the DEPTH.
#   anchors : the spliced index at the candidate peaks (1986, 1989, 1990) and the
#             fall from each to the 1993 trough -- the depth depends on where you
#             start counting, which is the single number to trust least.
build_gdp_uncertainty <- function(long = build_gdp_long()) {
  idx <- function(y) {
    v <- long$index[long$year == y]
    if (length(v) == 1) v else NA_real_
  }

  # --- pre-1952 fan -> ribbon in index units --------------------------------
  ribbon <- tryCatch(
    {
      est <- load_tica_estimates()
      gvsm <- est[est$estimate == "GVSM", c("year", "value")]
      mk <- merge(long[, c("year", "index")], gvsm, by = "year")
      k <- stats::median(mk$index / mk$value, na.rm = TRUE)
      agg <- stats::aggregate(value ~ year, est, function(v) c(lo = min(v), hi = max(v), n = length(v)))
      r <- data.frame(year = agg$year, lo = agg$value[, "lo"] * k, hi = agg$value[, "hi"] * k, n = agg$value[, "n"])
      r[r$n > 1 & r$year <= 1951, c("year", "lo", "hi")]
    },
    error = function(e) {
      message("Uncertainty ribbon skipped (Tica fan unavailable): ", conditionMessage(e))
      NULL
    }
  )

  # --- 1990s cross-source depth (fall from 1990 to trough) ------------------
  idx1990 <- idx(1990)
  depth <- tryCatch(
    {
      raw <- build_gdp_raw()
      cols <- c(
        Maddison = "gdppc_maddison_int2011",
        PWT = "gdppc_pwt_usd2017",
        `Svjetska banka` = "gdppc_wb_usd2015"
      )
      rows <- lapply(seq_along(cols), function(i) {
        col <- cols[[i]]
        if (!col %in% names(raw)) return(NULL)
        s <- raw[raw$year %in% 1989:1996, c("year", col)]
        names(s) <- c("year", "v")
        s <- s[!is.na(s$v), ]
        base <- s$v[s$year == 1990]
        if (length(base) != 1) return(NULL)
        tr <- min(s$v)
        ty <- s$year[which.min(s$v)]
        data.frame(
          source = names(cols)[i],
          fall_pct = round(100 * (tr / base - 1), 1),
          trough_year = ty,
          trough_index = round(idx1990 * tr / base, 1),
          stringsAsFactors = FALSE
        )
      })
      do.call(rbind, Filter(Negate(is.null), rows))
    },
    error = function(e) {
      message("Cross-source depth skipped: ", conditionMessage(e))
      NULL
    }
  )

  # --- anchor sensitivity: depth depends on the peak year -------------------
  trough_idx <- idx(1993)
  anchors <- do.call(rbind, lapply(c(1986, 1989, 1990), function(y) {
    v <- idx(y)
    if (is.na(v) || is.na(trough_idx)) return(NULL)
    data.frame(peak_year = y, peak_index = round(v, 1),
               fall_pct = round(100 * (trough_idx / v - 1), 1), stringsAsFactors = FALSE)
  }))

  list(ribbon = ribbon, depth = depth, anchors = anchors,
       trough_index = trough_idx, trough_year = 1993)
}

# Average annual real growth (CAGR) of the spliced per-capita index, by era.
# One source of truth for the growth-bar chart and the prose numbers. Eras use
# the annual data only (1952+), where rates are most reliable.
.gdp_cagr_rows <- function(long, defn) {
  idx <- function(y) long$index[long$year == y]
  rows <- lapply(defn, function(e) {
    y0 <- as.integer(e[[2]])
    y1 <- as.integer(e[[3]])
    v0 <- idx(y0)
    v1 <- idx(y1)
    if (!length(v0) || !length(v1)) return(NULL)
    cagr <- 100 * ((v1 / v0)^(1 / (y1 - y0)) - 1)
    data.frame(
      era = e[[1]], year0 = y0, year1 = y1,
      cagr = round(cagr, 1), total = round(100 * (v1 / v0 - 1)),
      positive = cagr >= 0, stringsAsFactors = FALSE
    )
  })
  do.call(rbind, Filter(Negate(is.null), rows))
}

# The five plotted eras (boom/crisis spans), for the growth-bar chart.
build_gdp_growth <- function(long = build_gdp_long()) {
  .gdp_cagr_rows(long, list(
    c("Socijalizam", 1952, 1986),
    c("Prva kriza", 1986, 1993),
    c("Oporavak", 1993, 2008),
    c("Druga kriza", 2008, 2014),
    c("Novije", 2014, 2025)
  ))
}

# Summary rates quoted in prose but not plotted (pre-war pace, whole annual run).
build_gdp_growth_summary <- function(long = build_gdp_long()) {
  .gdp_cagr_rows(long, list(
    c("Habsbursko 1870-1900", 1870, 1900),
    c("Medjuratno 1920-1939", 1920, 1939),
    c("Cijeli niz 1952-2025", 1952, 2025)
  ))
}
