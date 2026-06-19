packages <- c(
  "arrow",
  "DBI",
  "duckdb",
  "eurostat",
  "ggplot2",
  "jsonlite",
  "knitr",
  "readr",
  "readxl",
  "rmarkdown",
  "scales"
)

use_renv <- identical(Sys.getenv("CROAICON_USE_RENV"), "true")

if (use_renv) {
  if (!requireNamespace("renv", quietly = TRUE)) {
    install.packages("renv", repos = "https://cloud.r-project.org")
  }

  if (!file.exists("renv/activate.R")) {
    renv::init(bare = TRUE)
  }

  renv::install(packages, prompt = FALSE)
  renv::snapshot(prompt = FALSE)
} else {
  installed <- rownames(installed.packages())
  missing <- setdiff(packages, installed)

  if (length(missing) > 0) {
    install.packages(missing, repos = "https://cloud.r-project.org")
  } else {
    message("All R packages are already installed.")
  }
}
