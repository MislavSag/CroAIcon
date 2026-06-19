args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 1) {
  stop("Usage: Rscript scripts/new_post.R \"Naslov posta\"", call. = FALSE)
}

source(file.path("R", "00_config.R"))

title <- args[[1]]
date <- Sys.Date()

slugify <- function(x) {
  x <- iconv(x, to = "ASCII//TRANSLIT")
  x <- tolower(x)
  x <- gsub("[^a-z0-9]+", "-", x)
  x <- gsub("(^-|-$)", "", x)
  x
}

slug <- paste(format(date, "%Y-%m"), slugify(title), sep = "-")
post_dir <- path_project("posts", slug)
post_file <- file.path(post_dir, "index.qmd")

if (dir.exists(post_dir)) {
  stop(sprintf("Post already exists: %s", post_dir), call. = FALSE)
}

dir_create(post_dir)

template <- c(
  "---",
  sprintf('title: "%s"', title),
  sprintf("date: %s", format(date)),
  "categories: []",
  'description: ""',
  "---",
  "",
  "## Sažetak",
  "",
  "## Podaci i metodologija",
  "",
  "## Rezultati",
  "",
  "## Interpretacija",
  "",
  "## Ograničenja",
  "",
  "## Izvori"
)

writeLines(template, post_file, useBytes = TRUE)
message("Created ", post_file)

