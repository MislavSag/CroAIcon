if (!exists("path_project")) {
  source(file.path("R", "00_config.R"))
}

# House chart palette and theme. Single source of truth, mirrors the python
# sectors charts (python/sectors_charts.py) so R and Python output match.
house_pal <- list(
  paper = "#F7F7F4",
  ink = "#18181B",
  muted = "#71717A",
  hair = "#E6E6E1",
  accent = "#2348E5",
  rise = "#1C8F5A",
  fall = "#D2463A",
  surface = "#ECE9E1",
  amber = "#C77B30",
  purple = "#6D4AA6"
)

# Cycle palette for multi-series charts (same order as the python PAL).
house_series <- c(
  house_pal$accent, house_pal$fall, house_pal$rise,
  house_pal$amber, house_pal$purple, house_pal$ink
)

# ggplot theme: paper background, monospace, left-aligned bold title, muted
# subtitle/caption, no top/right spines, no ticks, hairline y-grid only.
theme_house <- function(base_size = 12) {
  ggplot2::theme_minimal(base_size = base_size, base_family = "mono") +
    ggplot2::theme(
      plot.background = ggplot2::element_rect(fill = house_pal$paper, color = NA),
      panel.background = ggplot2::element_rect(fill = house_pal$paper, color = NA),
      plot.title.position = "plot",
      plot.caption.position = "plot",
      plot.title = ggplot2::element_text(face = "bold", color = house_pal$ink, hjust = 0, size = base_size + 3),
      plot.subtitle = ggplot2::element_text(color = house_pal$muted, hjust = 0, size = base_size - 2.5, margin = ggplot2::margin(t = 4, b = 12)),
      plot.caption = ggplot2::element_text(color = house_pal$muted, hjust = 0, size = base_size - 4, margin = ggplot2::margin(t = 12)),
      axis.text = ggplot2::element_text(color = house_pal$muted, size = base_size - 3),
      axis.title = ggplot2::element_blank(),
      axis.ticks = ggplot2::element_blank(),
      panel.grid.minor = ggplot2::element_blank(),
      panel.grid.major.x = ggplot2::element_blank(),
      panel.grid.major.y = ggplot2::element_line(color = house_pal$hair, linewidth = 0.4),
      strip.text = ggplot2::element_text(face = "bold", color = house_pal$ink, hjust = 0, size = base_size - 1),
      plot.margin = ggplot2::margin(14, 18, 10, 14)
    )
}
