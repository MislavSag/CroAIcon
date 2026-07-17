source(file.path("R", "house_style.R"))

suppressPackageStartupMessages({
  library(ggplot2)
})

groups_path <- file.path("outputs", "tables", "state_aid_concentration_groups.csv")
size_path <- file.path("outputs", "tables", "state_aid_concentration_by_size.csv")
coverage_path <- file.path("outputs", "tables", "state_aid_coverage_comparison.csv")
type_path <- file.path("outputs", "tables", "state_aid_concentration_within_type.csv")
recurrence_path <- file.path("outputs", "tables", "state_aid_recipient_recurrence_2023_2024.csv")
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

# Figure 3. The official series is the denominator; the current register is the audit.
coverage <- read.csv(coverage_path, check.names = FALSE, fileEncoding = "UTF-8-BOM")
coverage_long <- rbind(
  data.frame(
    year = coverage$year,
    series = "Službeni godišnji iznos",
    share = 100
  ),
  data.frame(
    year = coverage$year,
    series = "Današnji javni registar",
    share = coverage$registry_to_official_pct
  ),
  data.frame(
    year = coverage$year,
    series = "Analitički uzorak s OIB-om",
    share = coverage$analytical_to_official_pct
  )
)
coverage_long$year <- factor(coverage_long$year, levels = rev(coverage$year))
coverage_long$series <- factor(
  coverage_long$series,
  levels = c(
    "Službeni godišnji iznos",
    "Današnji javni registar",
    "Analitički uzorak s OIB-om"
  )
)
coverage_long$label <- paste0(
  vapply(coverage_long$share, hr_number, character(1), digits = 1),
  "%"
)

p_coverage <- ggplot(
  coverage_long,
  aes(x = share, y = year, colour = series, shape = series)
) +
  geom_col(
    aes(fill = series),
    width = 0.18,
    alpha = 0.24,
    position = position_dodge(width = 0.62),
    show.legend = FALSE
  ) +
  geom_point(size = 4.2, stroke = 1.2, position = position_dodge(width = 0.62)) +
  geom_text(
    aes(label = label),
    hjust = -0.35,
    family = "mono",
    fontface = "bold",
    size = 3.4,
    position = position_dodge(width = 0.62),
    show.legend = FALSE
  ) +
  scale_colour_manual(
    values = c(
      "Službeni godišnji iznos" = house_pal$ink,
      "Današnji javni registar" = house_pal$accent,
      "Analitički uzorak s OIB-om" = house_pal$amber
    )
  ) +
  scale_fill_manual(
    values = c(
      "Službeni godišnji iznos" = house_pal$ink,
      "Današnji javni registar" = house_pal$accent,
      "Analitički uzorak s OIB-om" = house_pal$amber
    )
  ) +
  scale_shape_manual(values = c(15, 16, 17)) +
  scale_x_continuous(
    limits = c(0, 108),
    breaks = seq(0, 100, by = 25),
    labels = function(x) paste0(x, "%"),
    expand = c(0, 0)
  ) +
  labs(
    title = "Današnji registar dobro pokriva 2023., ali ne i starije godine",
    subtitle = "Iznos u registru kao udio službenog godišnjeg iznosa Ministarstva financija",
    colour = NULL,
    shape = NULL,
    caption = "Izvori: Ministarstvo financija (izvješće za 2023.) i Registar državnih potpora; izračun AI.econ"
  ) +
  theme_house(base_size = 13) +
  theme(
    axis.text.y = element_text(colour = house_pal$ink, face = "bold"),
    legend.position = "top",
    legend.justification = "left",
    legend.box.margin = margin(0, 0, 6, 0),
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank(),
    plot.margin = margin(14, 28, 10, 14)
  )

save_chart(
  p_coverage,
  "state-aid-coverage-audit.png",
  width = 10,
  height = 5.6
)

# Figure 4. Aligned panels compare composition without a dual axis.
aid_types <- read.csv(type_path, check.names = FALSE, fileEncoding = "UTF-8-BOM")
aid_types$short_type <- c(
  "Skupno izuzeće",
  "Prijava Europskoj komisiji",
  "Usluge od općeg interesa (izuzeće)",
  "Potpore male vrijednosti",
  "Ostalo",
  "Ostalo",
  "Ostalo"
)
aid_types_grouped <- aggregate(
  cbind(award_count, amount_eur) ~ short_type,
  data = aid_types,
  FUN = sum
)
aid_types_grouped$award_share_pct <- (
  aid_types_grouped$award_count / sum(aid_types_grouped$award_count) * 100
)
aid_types_grouped$amount_share_pct <- (
  aid_types_grouped$amount_eur / sum(aid_types_grouped$amount_eur) * 100
)
de_minimis_amount_share <- aid_types_grouped$amount_share_pct[
  aid_types_grouped$short_type == "Potpore male vrijednosti"
]
type_order <- aid_types_grouped$short_type[order(aid_types_grouped$amount_share_pct)]
aid_type_panels <- rbind(
  data.frame(
    short_type = aid_types_grouped$short_type,
    panel = "Udio u broju dodjela",
    share = aid_types_grouped$award_share_pct
  ),
  data.frame(
    short_type = aid_types_grouped$short_type,
    panel = "Udio u iznosu",
    share = aid_types_grouped$amount_share_pct
  )
)
aid_type_panels$short_type <- factor(aid_type_panels$short_type, levels = type_order)
aid_type_panels$panel <- factor(
  aid_type_panels$panel,
  levels = c("Udio u broju dodjela", "Udio u iznosu")
)
aid_type_panels$label <- paste0(
  vapply(aid_type_panels$share, hr_number, character(1), digits = 1),
  "%"
)

p_type_mix <- ggplot(aid_type_panels, aes(x = share, y = short_type)) +
  geom_col(fill = house_pal$accent, width = 0.66) +
  geom_text(
    aes(label = label),
    hjust = -0.18,
    family = "mono",
    fontface = "bold",
    colour = house_pal$ink,
    size = 3.4
  ) +
  facet_grid(. ~ panel) +
  scale_x_continuous(
    limits = c(0, 60),
    breaks = seq(0, 60, by = 10),
    labels = function(x) paste0(x, "%"),
    expand = c(0, 0)
  ) +
  labs(
    title = "Broj dodjela i novac pričaju različite priče",
    subtitle = paste0(
      "Potpore male vrijednosti čine polovinu dodjela, ali ",
      hr_number(de_minimis_amount_share, 0),
      "% promatranog iznosa"
    ),
    caption = "Izvor: Registar državnih potpora; provjereni pozitivni iznosi s valjanim OIB-om, 2017.–2025.; izračun AI.econ"
  ) +
  theme_house(base_size = 13) +
  theme(
    axis.text.y = element_text(colour = house_pal$ink),
    strip.text = element_text(colour = house_pal$ink, face = "bold"),
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank(),
    panel.spacing.x = grid::unit(1.3, "lines"),
    plot.margin = margin(14, 28, 10, 14)
  )

save_chart(
  p_type_mix,
  "state-aid-type-count-versus-amount.png",
  width = 11.2,
  height = 6.2
)

# Figure 5. A common scale tests whether total concentration is only a mix effect.
within_type <- aid_types[aid_types$amount_share_pct >= 10, ]
within_type$short_type <- c(
  "Skupno izuzeće",
  "Prijava Europskoj komisiji",
  "Usluge od općeg interesa (izuzeće)",
  "Potpore male vrijednosti"
)
within_type$axis_label <- paste0(
  within_type$short_type,
  "  ·  ",
  vapply(within_type$recipient_count, hr_number, character(1)),
  " primatelja"
)
within_type$axis_label <- factor(
  within_type$axis_label,
  levels = within_type$axis_label[order(within_type$top_1_amount_share_pct)]
)
within_type$value_label <- paste0(
  vapply(within_type$top_1_amount_share_pct, hr_number, character(1), digits = 1),
  "%"
)

p_within_type <- ggplot(
  within_type,
  aes(x = top_1_amount_share_pct, y = axis_label)
) +
  geom_segment(
    aes(x = 0, xend = top_1_amount_share_pct, yend = axis_label),
    colour = house_pal$surface,
    linewidth = 2.2
  ) +
  geom_point(colour = house_pal$accent, size = 4.8) +
  geom_text(
    aes(label = value_label),
    hjust = -0.35,
    family = "mono",
    fontface = "bold",
    colour = house_pal$ink,
    size = 3.8
  ) +
  scale_x_continuous(
    limits = c(0, 62),
    breaks = seq(0, 60, by = 10),
    labels = function(x) paste0(x, "%"),
    expand = c(0, 0)
  ) +
  labs(
    title = "Koncentracija ostaje visoka i unutar svake glavne vrste potpore",
    subtitle = "Udio iznosa koji dobiva gornjih 1% primatelja unutar vrste potpore",
    caption = "Izvor: Registar državnih potpora; provjereni pozitivni iznosi s valjanim OIB-om, 2017.–2025.; izračun AI.econ"
  ) +
  theme_house(base_size = 13) +
  theme(
    axis.text.y = element_text(colour = house_pal$ink),
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank(),
    plot.margin = margin(14, 28, 10, 14)
  )

save_chart(
  p_within_type,
  "state-aid-concentration-within-type.png",
  width = 10.5,
  height = 5.5
)

# Figure 6. Two 100% bars separate how many recipients repeat from how much they receive.
recurrence <- read.csv(recurrence_path, check.names = FALSE, fileEncoding = "UTF-8-BOM")
recurrence_panels <- rbind(
  data.frame(
    metric = "Primatelji",
    recurrence_group = recurrence$recurrence_group,
    share = recurrence$recipient_share_pct
  ),
  data.frame(
    metric = "Iznos",
    recurrence_group = recurrence$recurrence_group,
    share = recurrence$amount_share_pct
  )
)
recurrence_panels$metric <- factor(recurrence_panels$metric, levels = c("Iznos", "Primatelji"))
recurrence_panels$recurrence_group <- factor(
  recurrence_panels$recurrence_group,
  levels = c("Jedna godina", "Obje godine")
)
recurrence_panels$label <- paste0(
  recurrence_panels$recurrence_group,
  "\n",
  vapply(recurrence_panels$share, hr_number, character(1), digits = 1),
  "%"
)

p_recurrence <- ggplot(
  recurrence_panels,
  aes(x = share, y = metric, fill = recurrence_group)
) +
  geom_col(width = 0.64, colour = house_pal$paper, linewidth = 1.1) +
  geom_text(
    aes(label = label),
    position = position_stack(vjust = 0.5),
    family = "mono",
    fontface = "bold",
    colour = house_pal$paper,
    lineheight = 0.92,
    size = 3.6
  ) +
  scale_fill_manual(values = c("Jedna godina" = house_pal$amber, "Obje godine" = house_pal$accent)) +
  scale_x_continuous(
    limits = c(0, 100),
    breaks = seq(0, 100, by = 25),
    labels = function(x) paste0(x, "%"),
    expand = c(0, 0)
  ) +
  labs(
    title = "Trećina primatelja prisutna je obje godine, ali nosi dvije trećine iznosa",
    subtitle = "Primatelji s provjerenim pozitivnim iznosima i valjanim OIB-om u registru za 2023. i 2024.",
    fill = NULL,
    caption = "Izvor: Registar državnih potpora i potpora male vrijednosti; izračun AI.econ"
  ) +
  theme_house(base_size = 13) +
  theme(
    axis.text.y = element_text(colour = house_pal$ink, face = "bold"),
    legend.position = "none",
    panel.grid.major.y = element_blank(),
    panel.grid.minor = element_blank(),
    plot.margin = margin(14, 18, 10, 14)
  )

save_chart(
  p_recurrence,
  "state-aid-recipient-recurrence.png",
  width = 10,
  height = 4.8
)

message("OK - wrote six state-aid concentration charts")
