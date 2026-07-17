source(file.path("R", "house_style.R"))

suppressPackageStartupMessages({
  library(ggplot2)
})

groups_path <- file.path("outputs", "tables", "state_aid_concentration_groups.csv")
size_path <- file.path("outputs", "tables", "state_aid_concentration_by_size.csv")
output_dir <- file.path("outputs", "figures")
post_dir <- file.path("posts", "2026-07-drzavne-potpore-koncentracija", "images")

dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(post_dir, recursive = TRUE, showWarnings = FALSE)

hr_number <- function(x, digits = 0) {
  formatted <- formatC(
    x,
    format = "f",
    digits = digits,
    big.mark = ".",
    decimal.mark = ","
  )
  sub(",0+$", "", formatted)
}

save_chart <- function(plot, filename, width, height) {
  output_path <- file.path(output_dir, filename)
  post_path <- file.path(post_dir, filename)

  ggsave(
    filename = output_path,
    plot = plot,
    width = width,
    height = height,
    units = "in",
    dpi = 180,
    bg = house_pal$paper
  )
  file.copy(output_path, post_path, overwrite = TRUE)
}

# Figure 1. A 100% bar makes the concentration share the only visual task.
groups <- read.csv(groups_path, check.names = FALSE, encoding = "UTF-8")
groups <- groups[order(groups$display_order), ]
groups$xmax <- cumsum(groups$amount_share_pct)
groups$xmin <- c(0, head(groups$xmax, -1))
groups$xmid <- (groups$xmin + groups$xmax) / 2
groups$label <- paste0(
  groups$group,
  "\n",
  vapply(groups$amount_share_pct, hr_number, character(1), digits = 1),
  "%"
)
groups$label[groups$display_order == 3] <- paste0(
  "Donjih\n90%\n",
  hr_number(groups$amount_share_pct[groups$display_order == 3], 1),
  "%"
)
groups$label_size <- c(4.2, 4.2, 2.7)
groups$fill <- c(house_pal$accent, house_pal$amber, house_pal$surface)
groups$text_colour <- c(house_pal$paper, house_pal$paper, house_pal$ink)

top_one_share <- groups$amount_share_pct[groups$display_order == 1]

p_concentration <- ggplot(groups) +
  geom_rect(
    aes(xmin = xmin, xmax = xmax, ymin = 0, ymax = 1, fill = fill),
    colour = house_pal$paper,
    linewidth = 1.2
  ) +
  geom_text(
    aes(
      x = xmid,
      y = 0.5,
      label = label,
      colour = text_colour,
      size = label_size
    ),
    family = "mono",
    fontface = "bold",
    lineheight = 0.9
  ) +
  scale_fill_identity() +
  scale_colour_identity() +
  scale_size_identity() +
  scale_x_continuous(limits = c(0, 100), expand = c(0, 0)) +
  scale_y_continuous(limits = c(0, 1), expand = c(0, 0)) +
  labs(
    title = paste0(
      "Gornjih 1% primatelja dobiva ",
      hr_number(top_one_share, 0),
      "% iznosa"
    ),
    subtitle = "Udio u provjerenom iznosu elementa potpore, primatelji s valjanim OIB-om, 2017. do 2025.",
    caption = "Izvor: Registar državnih potpora i potpora male vrijednosti; izračun AI.econ"
  ) +
  theme_house(base_size = 13) +
  theme(
    axis.text = element_blank(),
    panel.grid = element_blank(),
    plot.margin = margin(14, 18, 10, 14)
  )

save_chart(
  p_concentration,
  "state-aid-concentration-groups.png",
  width = 10,
  height = 4.1
)

# Figure 2. Common-baseline bars compare the registered amount by company size.
size_data <- read.csv(size_path, check.names = FALSE, encoding = "UTF-8")
size_data$company_size <- factor(
  size_data$company_size,
  levels = size_data$company_size[order(size_data$amount_eur)]
)
size_data$bar_colour <- ifelse(
  size_data$company_size == "Veliki",
  house_pal$accent,
  ifelse(size_data$company_size == "Mikro", house_pal$amber, house_pal$surface)
)
size_data$axis_label <- paste0(
  as.character(size_data$company_size),
  "  ·  ",
  vapply(size_data$award_count, hr_number, character(1)),
  " dodjela"
)
size_data$axis_label <- factor(
  size_data$axis_label,
  levels = size_data$axis_label[order(size_data$amount_eur)]
)
size_data$value_label <- paste0(
  vapply(size_data$amount_eur / 1e9, hr_number, character(1), digits = 2),
  " mlrd. €"
)

large_amount <- size_data$amount_eur[as.character(size_data$company_size) == "Veliki"]
micro_amount <- size_data$amount_eur[as.character(size_data$company_size) == "Mikro"]
amount_ratio <- large_amount / micro_amount

p_size <- ggplot(size_data, aes(x = amount_eur, y = axis_label)) +
  geom_col(aes(fill = bar_colour), width = 0.68) +
  geom_text(
    aes(label = value_label),
    hjust = -0.08,
    family = "mono",
    fontface = "bold",
    colour = house_pal$ink,
    size = 3.8
  ) +
  scale_fill_identity() +
  scale_x_continuous(
    limits = c(0, max(size_data$amount_eur) * 1.22),
    breaks = seq(0, 2e9, by = 0.5e9),
    labels = function(x) paste0(hr_number(x / 1e9, 1), " mlrd. €"),
    expand = c(0, 0)
  ) +
  labs(
    title = paste0(
      "Kategorija Veliki nosi ",
      ifelse(amount_ratio >= 1.9 & amount_ratio <= 2.1, "dvostruko", paste0(hr_number(amount_ratio, 1), " puta")),
      " više od kategorije Mikro"
    ),
    subtitle = "Registrirani iznos elementa potpore po veličini primatelja; uz kategoriju je broj dodjela",
    caption = "Izvor: Registar državnih potpora i potpora male vrijednosti; izračun AI.econ"
  ) +
  theme_house(base_size = 13) +
  theme(
    axis.text.y = element_text(color = house_pal$ink, hjust = 1),
    panel.grid = element_blank(),
    plot.margin = margin(14, 26, 10, 14)
  )

save_chart(
  p_size,
  "state-aid-concentration-size.png",
  width = 10,
  height = 5.8
)

message("OK - wrote state-aid concentration charts")
