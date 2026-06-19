if (!exists("path_project")) {
  source(file.path("R", "00_config.R"))
}

gfi_source_dir <- function() {
  read_env("GFI_SOURCE_DIR", path_project("data", "raw", "gfi"))
}

list_gfi_files <- function(pattern = "\\.(csv|xlsx|xls|parquet|rds)$") {
  source_dir <- gfi_source_dir()
  if (!dir.exists(source_dir)) {
    return(character())
  }

  list.files(source_dir, pattern = pattern, recursive = TRUE, full.names = TRUE, ignore.case = TRUE)
}

read_gfi_file <- function(path) {
  ext <- tolower(tools::file_ext(path))

  if (identical(ext, "csv")) {
    if (requireNamespace("readr", quietly = TRUE)) {
      return(readr::read_csv(path, show_col_types = FALSE))
    }
    return(utils::read.csv(path, stringsAsFactors = FALSE, check.names = FALSE))
  }

  if (ext %in% c("xlsx", "xls")) {
    require_package("readxl")
    return(readxl::read_excel(path))
  }

  if (identical(ext, "parquet")) {
    require_package("arrow")
    return(as.data.frame(arrow::read_parquet(path)))
  }

  if (identical(ext, "rds")) {
    return(readRDS(path))
  }

  stop(sprintf("Unsupported GFI file format: %s", ext), call. = FALSE)
}

load_gfi_dataset <- function(file_name_or_path) {
  if (file.exists(file_name_or_path)) {
    return(read_gfi_file(file_name_or_path))
  }

  candidate <- file.path(gfi_source_dir(), file_name_or_path)
  if (!file.exists(candidate)) {
    stop(sprintf("GFI file not found: %s", file_name_or_path), call. = FALSE)
  }

  read_gfi_file(candidate)
}
