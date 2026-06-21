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

# Spliced long index. Accent line, gray recession/break bands, reference line
# at the base year, source caption. `long` has columns year, index.
save_gdp_index_chart <- function(
  long,
  path,
  title,
  subtitle,
  caption,
  base_index = 100,
  bands = list(c(1991, 1995), c(2009, 2014)),
  width = 8.2,
  height = 4.8
) {
  dir_create(dirname(path))
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    message("save_gdp_index_chart needs ggplot2; skipping ", basename(path))
    return(invisible(NULL))
  }

  if (is.null(long[["granularity"]])) long$granularity <- "annual"

  # Annual part: complete the year grid so unobserved gaps (war years missing in
  # Tica) BREAK the solid line instead of being interpolated across.
  ann <- long[long$granularity == "annual", , drop = FALSE]
  grid <- data.frame(year = seq(min(ann$year), max(ann$year)))
  ann <- merge(grid, ann[, c("year", "index")], by = "year", all.x = TRUE)

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

  x_min <- min(long$year)
  plot <- ggplot2::ggplot()
  for (b in bands) {
    plot <- plot + ggplot2::annotate(
      "rect", xmin = b[1], xmax = b[2], ymin = -Inf, ymax = Inf,
      fill = house_pal$surface
    )
  }
  plot <- plot +
    ggplot2::geom_hline(yintercept = base_index, color = house_pal$hair, linewidth = 0.5)
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
  plot <- plot +
    ggplot2::geom_line(
      data = ann, ggplot2::aes(x = .data[["year"]], y = .data[["index"]]),
      color = house_pal$accent, linewidth = 1.1
    ) +
    ggplot2::labs(title = title, subtitle = subtitle, caption = caption) +
    ggplot2::scale_x_continuous(expand = ggplot2::expansion(mult = c(0.01, 0.03))) +
    theme_house()

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
    ggplot2::facet_wrap(~source, scales = "free_y", ncol = 2) +
    ggplot2::labs(title = title, subtitle = subtitle, caption = caption) +
    theme_house(base_size = 11)

  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 170)
  invisible(path)
}

# Fan of estimates: many thin muted lines for the alternative series, one bold
# accent line for the chosen one. `long` has columns year, estimate, value,
# chosen (logical). For showing a reconstruction rests on a spread of estimates.
save_gdp_fan_chart <- function(
  long,
  path,
  title,
  subtitle,
  caption,
  width = 8.2,
  height = 4.8
) {
  dir_create(dirname(path))
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    message("save_gdp_fan_chart needs ggplot2; skipping ", basename(path))
    return(invisible(NULL))
  }

  variants <- long[!long$chosen, , drop = FALSE]
  chosen <- long[long$chosen, , drop = FALSE]

  plot <- ggplot2::ggplot() +
    ggplot2::geom_line(
      data = variants,
      ggplot2::aes(x = .data[["year"]], y = .data[["value"]], group = .data[["estimate"]]),
      color = house_pal$muted, linewidth = 0.5, alpha = 0.5
    ) +
    ggplot2::geom_line(
      data = chosen,
      ggplot2::aes(x = .data[["year"]], y = .data[["value"]]),
      color = house_pal$accent, linewidth = 1.3
    ) +
    ggplot2::labs(title = title, subtitle = subtitle, caption = caption) +
    theme_house()

  ggplot2::ggsave(path, plot = plot, width = width, height = height, dpi = 170)
  invisible(path)
}
