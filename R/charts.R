if (!exists("path_project")) {
  source(file.path("R", "00_config.R"))
}

if (!exists("theme_house")) {
  source(file.path("R", "house_style.R"))
}

`%||%` <- function(x, y) {
  if (is.null(x)) y else x
}

save_line_chart <- function(
  data,
  x,
  y,
  path,
  title = NULL,
  subtitle = NULL,
  width = 7,
  height = 4
) {
  dir_create(dirname(path))

  if (requireNamespace("ggplot2", quietly = TRUE)) {
    plot <- ggplot2::ggplot(data, ggplot2::aes(x = .data[[x]], y = .data[[y]])) +
      ggplot2::geom_line(color = "#0b6b6f", linewidth = 0.9) +
      ggplot2::geom_point(color = "#0b6b6f", size = 2) +
      ggplot2::labs(title = title, subtitle = subtitle, x = NULL, y = NULL) +
      ggplot2::theme_minimal(base_size = 12) +
      ggplot2::theme(
        plot.title = ggplot2::element_text(face = "bold"),
        panel.grid.minor = ggplot2::element_blank()
      )

    ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 160)
    return(invisible(path))
  }

  grDevices::png(path, width = width, height = height, units = "in", res = 160)
  on.exit(grDevices::dev.off(), add = TRUE)

  graphics::plot(
    data[[x]],
    data[[y]],
    type = "b",
    pch = 19,
    col = "#0b6b6f",
    xlab = x,
    ylab = y,
    main = title %||% ""
  )
  graphics::grid(col = "#d7dde2")

  invisible(path)
}

# Faceted multi-series chart: one panel per source, free y-scales so each raw
# series shows in its own unit/base year (never merge levels across sources).
# `data` is long: columns year, source, value. Requires ggplot2.
save_facet_chart <- function(
  data,
  path,
  title = NULL,
  subtitle = NULL,
  width = 8,
  height = 5
) {
  dir_create(dirname(path))

  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    message("save_facet_chart needs ggplot2; skipping ", basename(path))
    return(invisible(NULL))
  }

  plot <- ggplot2::ggplot(
    data,
    ggplot2::aes(x = .data[["year"]], y = .data[["value"]])
  ) +
    ggplot2::geom_line(color = "#0b6b6f", linewidth = 0.8) +
    ggplot2::facet_wrap(~source, scales = "free_y", ncol = 2) +
    ggplot2::labs(title = title, subtitle = subtitle, x = NULL, y = NULL) +
    ggplot2::theme_minimal(base_size = 11) +
    ggplot2::theme(
      plot.title = ggplot2::element_text(face = "bold"),
      panel.grid.minor = ggplot2::element_blank(),
      strip.text = ggplot2::element_text(face = "bold")
    )

  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 160)
  invisible(path)
}

# --- House-styled GDP charts (match python/sectors_charts.py aesthetic) -------

# Draw shaded event bands with optional text labels. Each band is either a
# numeric c(from, to) or a list(from=, to=, label=). Labels are staggered in two
# rows near the top so adjacent ones do not collide.
.add_bands <- function(plot, bands) {
  i <- 0
  for (b in bands) {
    i <- i + 1
    from <- if (!is.null(b[["from"]])) b[["from"]] else b[[1]]
    to <- if (!is.null(b[["to"]])) b[["to"]] else b[[2]]
    label <- if (!is.null(b[["label"]])) b[["label"]] else NULL

    plot <- plot + ggplot2::annotate(
      "rect", xmin = from, xmax = to, ymin = -Inf, ymax = Inf, fill = house_pal$surface
    )
    if (!is.null(label) && nzchar(label)) {
      vj <- if (i %% 2 == 1) 1.3 else 3.1
      plot <- plot + ggplot2::annotate(
        "text", x = (from + to) / 2, y = Inf, label = label,
        vjust = vj, size = 2.6, color = house_pal$muted, family = "mono"
      )
    }
  }
  plot
}

# Spliced long index, with the UNCERTAINTY drawn into the picture (so a reader
# who never reaches the notes still sees where the ground is soft):
#   * shaded ribbon where the early sources diverge (the Tica fan of pre-1952
#     estimates), passed in via `ribbon` (year, lo, hi in index units);
#   * hollow dashed circles for the pre-1910 decadal benchmarks;
#   * grey GAPS for the two war windows (no data), labelled as gaps;
#   * the pre-1952 single-source stretch drawn thinner, the reconstructed
#     1991-1995 window drawn as an amber dashed segment, both flagged in place.
# `long` has columns year, index, granularity.
save_gdp_index_chart <- function(
  long,
  path,
  title,
  subtitle,
  caption,
  ribbon = NULL,
  recon_window = c(1990, 1995),
  war_gaps = list(c(1914, 1919), c(1940, 1946)),
  base_index = 100,
  width = 8.6,
  height = 5.0
) {
  dir_create(dirname(path))
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    message("save_gdp_index_chart needs ggplot2; skipping ", basename(path))
    return(invisible(NULL))
  }

  if (is.null(long[["granularity"]])) long$granularity <- "annual"
  pal <- house_pal
  ymax <- max(long$index, na.rm = TRUE) * 1.06

  # Annual part: complete the year grid so unobserved gaps (war years missing in
  # Tica) BREAK the solid line instead of being interpolated across.
  ann <- long[long$granularity == "annual", c("year", "index"), drop = FALSE]
  grid <- data.frame(year = seq(min(ann$year), max(ann$year)))
  ann <- merge(grid, ann, by = "year", all.x = TRUE)

  # Split the annual line into a soft single-source pre-1952 stretch (thinner)
  # and the firmer 1952+ stretch, and break the firmer line across the
  # reconstructed window so no straight chord is drawn under the amber segment.
  soft_pre <- ann[ann$year <= 1951, , drop = FALSE]
  firm <- ann[ann$year >= 1952, , drop = FALSE]
  firm$index[firm$year >= recon_window[1] & firm$year <= recon_window[2]] <- NA
  recon <- long[long$year >= recon_window[1] & long$year <= recon_window[2], c("year", "index"), drop = FALSE]

  # Benchmark part: sparse decadal points, shown as points + a dashed connector
  # that reaches the first annual year, so they read as benchmarks not data.
  bench <- long[long$granularity == "benchmark", c("year", "index"), drop = FALSE]
  has_bench <- nrow(bench) > 0
  if (has_bench) {
    first_ann <- long[long$granularity == "annual", c("year", "index")]
    first_ann <- first_ann[which.min(first_ann$year), , drop = FALSE]
    dash <- rbind(bench, first_ann)
    dash <- dash[order(dash$year), , drop = FALSE]
  }

  plot <- ggplot2::ggplot()
  for (b in war_gaps) {
    plot <- plot + ggplot2::annotate(
      "rect", xmin = b[[1]], xmax = b[[2]], ymin = -Inf, ymax = Inf, fill = pal$surface
    )
  }

  # Uncertainty band where the early sources diverge.
  if (!is.null(ribbon) && nrow(ribbon)) {
    plot <- plot + ggplot2::geom_ribbon(
      data = ribbon,
      ggplot2::aes(x = .data[["year"]], ymin = .data[["lo"]], ymax = .data[["hi"]]),
      fill = pal$accent, alpha = 0.18
    )
  }

  plot <- plot +
    ggplot2::geom_hline(yintercept = base_index, color = pal$hair, linewidth = 0.5)

  if (has_bench) {
    plot <- plot +
      ggplot2::geom_line(
        data = dash, ggplot2::aes(x = .data[["year"]], y = .data[["index"]]),
        color = pal$accent, linewidth = 0.6, linetype = "22"
      ) +
      ggplot2::geom_point(
        data = bench, ggplot2::aes(x = .data[["year"]], y = .data[["index"]]),
        color = pal$accent, fill = pal$paper, shape = 21, size = 1.9, stroke = 0.9
      )
  }

  plot <- plot +
    ggplot2::geom_line(
      data = soft_pre, ggplot2::aes(x = .data[["year"]], y = .data[["index"]]),
      color = pal$accent, linewidth = 0.7
    ) +
    ggplot2::geom_line(
      data = firm, ggplot2::aes(x = .data[["year"]], y = .data[["index"]]),
      color = pal$accent, linewidth = 1.15
    ) +
    ggplot2::geom_line(
      data = recon, ggplot2::aes(x = .data[["year"]], y = .data[["index"]]),
      color = pal$amber, linewidth = 1.0, linetype = "42"
    )

  # In-place flags for each soft spot (positional, self-explaining).
  lab <- function(x, y, text, color, hjust = 0.5) {
    ggplot2::annotate("text", x = x, y = y, label = text, size = 2.3,
                      color = color, family = "mono", lineheight = 0.9, hjust = hjust)
  }
  plot <- plot +
    lab(1885, 0.13 * ymax, "desetljetne\nprocjene", pal$muted) +
    lab(1927, 0.27 * ymax, "raspon procjena\n(izvori se razilaze)", pal$accent) +
    ggplot2::annotate("segment", x = 1927, xend = 1927, y = 0.205 * ymax, yend = 0.115 * ymax,
                      color = pal$accent, linewidth = 0.3) +
    lab(mean(war_gaps[[1]]), 0.97 * ymax, "rat\n(rupa)", pal$muted) +
    lab(mean(war_gaps[[2]]), 0.97 * ymax, "rat\n(rupa)", pal$muted) +
    lab(1948.5, 0.22 * ymax, "samo\nTica", pal$amber, hjust = 1) +
    ggplot2::annotate("segment", x = 1950, xend = 1950, y = 0.155 * ymax, yend = 0.13 * ymax,
                      color = pal$amber, linewidth = 0.3) +
    lab(1996, 0.28 * ymax, "rekonstruirano\n1991.–1995.", pal$amber, hjust = 0)

  plot <- plot +
    ggplot2::labs(title = title, subtitle = subtitle, caption = caption) +
    ggplot2::scale_x_continuous(expand = ggplot2::expansion(mult = c(0.01, 0.03))) +
    ggplot2::scale_y_continuous(limits = c(0, ymax), breaks = c(0, 50, 100, 150)) +
    theme_house() +
    ggplot2::theme(plot.caption = ggplot2::element_text(size = 7.2))

  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 170)
  invisible(path)
}

# Raw multi-source panel, one facet per source, free y-scales, accent lines.
# `long_raw` has columns year, source, value.
save_gdp_panels_chart <- function(
  long_raw,
  path,
  title,
  subtitle,
  caption,
  width = 8.4,
  height = 5.2
) {
  dir_create(dirname(path))
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    message("save_gdp_panels_chart needs ggplot2; skipping ", basename(path))
    return(invisible(NULL))
  }

  plot <- ggplot2::ggplot(long_raw, ggplot2::aes(x = .data[["year"]], y = .data[["value"]])) +
    ggplot2::annotate("rect", xmin = 1991, xmax = 1995, ymin = -Inf, ymax = Inf, fill = house_pal$surface) +
    ggplot2::geom_line(color = house_pal$accent, linewidth = 0.9) +
    ggplot2::facet_wrap(~source, scales = "free", ncol = 2) +
    ggplot2::labs(title = title, subtitle = subtitle, caption = caption) +
    theme_house(base_size = 11)

  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 170)
  invisible(path)
}

# Windowed zoom of the spliced index. Same house treatment as the hero chart
# (annual line breaks at gaps; pre-1910 benchmarks as points + dashed connector),
# restricted to [year_min, year_max], with optional shaded crisis bands. `long`
# has columns year, index, granularity.
save_gdp_zoom_chart <- function(
  long,
  year_min,
  year_max,
  path,
  title,
  subtitle,
  caption,
  bands = list(),
  width = 7.4,
  height = 4.0
) {
  dir_create(dirname(path))
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    message("save_gdp_zoom_chart needs ggplot2; skipping ", basename(path))
    return(invisible(NULL))
  }
  if (is.null(long[["granularity"]])) long$granularity <- "annual"

  w <- long[long$year >= year_min & long$year <= year_max, , drop = FALSE]
  ann <- w[w$granularity == "annual", , drop = FALSE]
  bench <- w[w$granularity == "benchmark", c("year", "index"), drop = FALSE]
  has_bench <- nrow(bench) > 0

  # Complete the annual grid so unobserved gaps (war years) break the line.
  if (nrow(ann)) {
    grid <- data.frame(year = seq(min(ann$year), max(ann$year)))
    ann <- merge(grid, ann[, c("year", "index")], by = "year", all.x = TRUE)
  }
  if (has_bench) {
    first_ann <- w[w$granularity == "annual", c("year", "index")]
    if (nrow(first_ann)) {
      first_ann <- first_ann[which.min(first_ann$year), , drop = FALSE]
      dash <- rbind(bench, first_ann)
    } else {
      dash <- bench
    }
    dash <- dash[order(dash$year), , drop = FALSE]
  }

  plot <- .add_bands(ggplot2::ggplot(), bands)
  if (has_bench) {
    plot <- plot +
      ggplot2::geom_line(
        data = dash, ggplot2::aes(x = .data[["year"]], y = .data[["index"]]),
        color = house_pal$accent, linewidth = 0.7, linetype = "22"
      ) +
      ggplot2::geom_point(
        data = bench, ggplot2::aes(x = .data[["year"]], y = .data[["index"]]),
        color = house_pal$accent, fill = house_pal$paper, shape = 21, size = 1.8, stroke = 0.9
      )
  }
  if (nrow(ann)) {
    plot <- plot + ggplot2::geom_line(
      data = ann, ggplot2::aes(x = .data[["year"]], y = .data[["index"]]),
      color = house_pal$accent, linewidth = 1.2
    )
  }
  plot <- plot +
    ggplot2::labs(title = title, subtitle = subtitle, caption = caption) +
    ggplot2::scale_x_continuous(expand = ggplot2::expansion(mult = c(0.03, 0.03))) +
    theme_house()

  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 170)
  invisible(path)
}

# The 1990s, where the DEPTH is the number to trust least. Same house line, but
# the contested part is drawn in: the pre-collapse high is marked at three
# candidate peaks (1986, 1989, 1990) so the reader sees the fall depends on
# where you start counting, and the reconstructed 1991-1995 window is amber
# dashed. `anchors` has columns peak_year, peak_index, fall_pct; `trough_index`
# is the spliced 1993 trough.
save_gdp_crisis1_chart <- function(
  long,
  anchors,
  trough_index,
  path,
  title,
  subtitle,
  caption,
  year_min = 1984,
  year_max = 2003,
  trough_year = 1993,
  recon_window = c(1990, 1995),
  width = 7.4,
  height = 4.2
) {
  dir_create(dirname(path))
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    message("save_gdp_crisis1_chart needs ggplot2; skipping ", basename(path))
    return(invisible(NULL))
  }
  pal <- house_pal

  w <- long[long$year >= year_min & long$year <= year_max, c("year", "index"), drop = FALSE]
  grid <- data.frame(year = seq(year_min, year_max))
  w <- merge(grid, w, by = "year", all.x = TRUE)
  firm <- w
  firm$index[firm$year >= recon_window[1] & firm$year <= recon_window[2]] <- NA
  recon <- long[long$year >= recon_window[1] & long$year <= recon_window[2], c("year", "index"), drop = FALSE]

  plot <- ggplot2::ggplot() +
    ggplot2::annotate("rect", xmin = recon_window[1], xmax = recon_window[2],
                      ymin = -Inf, ymax = Inf, fill = pal$surface) +
    ggplot2::annotate("text", x = mean(recon_window), y = Inf, vjust = 1.4,
                      label = "rekonstruirano", size = 2.5, color = pal$muted, family = "mono")

  # Dashed guide from each candidate peak across to the trough year, so the
  # different depths are visible as different drop heights.
  if (!is.null(anchors) && nrow(anchors)) {
    for (i in seq_len(nrow(anchors))) {
      yv <- anchors$peak_index[i]
      plot <- plot +
        ggplot2::annotate("segment", x = anchors$peak_year[i], xend = trough_year,
                          y = yv, yend = yv, color = pal$muted, linewidth = 0.3, linetype = "33") +
        ggplot2::annotate("text", x = year_min - 0.3, y = yv, hjust = 1,
                          label = paste0(anchors$peak_year[i], "  ", sprintf("%+d%%", round(anchors$fall_pct[i]))),
                          size = 2.5, color = pal$ink, family = "mono")
    }
  }

  plot <- plot +
    ggplot2::geom_line(data = firm, ggplot2::aes(x = .data[["year"]], y = .data[["index"]]),
                       color = pal$accent, linewidth = 1.2) +
    ggplot2::geom_line(data = recon, ggplot2::aes(x = .data[["year"]], y = .data[["index"]]),
                       color = pal$amber, linewidth = 1.1, linetype = "42") +
    ggplot2::geom_point(data = anchors, ggplot2::aes(x = .data[["peak_year"]], y = .data[["peak_index"]]),
                        color = pal$accent, fill = pal$paper, shape = 21, size = 2, stroke = 0.9) +
    ggplot2::annotate("point", x = trough_year, y = trough_index, color = pal$fall, size = 2.4) +
    ggplot2::annotate("text", x = trough_year, y = trough_index, vjust = 2.1,
                      label = "dno 1993.", size = 2.5, color = pal$fall, family = "mono") +
    ggplot2::annotate("text", x = 1989, y = 95,
                      label = "Miljković: vrh 1989.", size = 2.6, color = pal$ink, family = "mono", hjust = 0.5) +
    ggplot2::labs(title = title, subtitle = subtitle, caption = caption) +
    ggplot2::scale_x_continuous(expand = ggplot2::expansion(mult = c(0.12, 0.04))) +
    theme_house() +
    ggplot2::theme(plot.caption = ggplot2::element_text(size = 7.2))

  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 170)
  invisible(path)
}

# Horizontal growth-rate bars by era. Green for positive, red for negative, value
# labels with the sign. `eras` has columns era, cagr (numeric %), positive (lgl).
save_gdp_growth_bars <- function(
  eras,
  path,
  title,
  subtitle,
  caption,
  width = 7.6,
  height = 4.2
) {
  dir_create(dirname(path))
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    message("save_gdp_growth_bars needs ggplot2; skipping ", basename(path))
    return(invisible(NULL))
  }

  eras$era <- factor(eras$era, levels = rev(eras$era))
  eras$lab <- paste0(
    ifelse(eras$cagr >= 0, "+", "minus "),
    formatC(abs(eras$cagr), format = "f", digits = 1, decimal.mark = ","),
    "%"
  )

  plot <- ggplot2::ggplot(eras, ggplot2::aes(x = .data[["cagr"]], y = .data[["era"]])) +
    ggplot2::geom_col(ggplot2::aes(fill = .data[["positive"]]), width = 0.64, show.legend = FALSE) +
    ggplot2::scale_fill_manual(values = c("TRUE" = house_pal$rise, "FALSE" = house_pal$fall)) +
    ggplot2::geom_vline(xintercept = 0, color = house_pal$ink, linewidth = 0.5) +
    ggplot2::geom_text(
      ggplot2::aes(label = .data[["lab"]], hjust = ifelse(.data[["cagr"]] >= 0, -0.12, 1.12)),
      size = 3.3, color = house_pal$ink, family = "mono"
    ) +
    ggplot2::scale_x_continuous(expand = ggplot2::expansion(mult = c(0.34, 0.2))) +
    ggplot2::labs(title = title, subtitle = subtitle, caption = caption) +
    theme_house() +
    ggplot2::theme(
      panel.grid.major.y = ggplot2::element_blank(),
      panel.grid.major.x = ggplot2::element_line(color = house_pal$hair, linewidth = 0.4),
      axis.text.x = ggplot2::element_blank()
    )

  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 170)
  invisible(path)
}
