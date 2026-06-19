if (!exists("path_project")) {
  source(file.path("R", "00_config.R"))
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
