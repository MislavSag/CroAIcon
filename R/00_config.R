project_root <- function() {
  path <- normalizePath(getwd(), winslash = "/", mustWork = TRUE)
  markers <- c("_quarto.yml", "CroAIcon.Rproj")

  repeat {
    if (any(file.exists(file.path(path, markers)))) {
      return(path)
    }

    parent <- dirname(path)
    if (identical(parent, path)) {
      stop("Cannot locate CroAIcon project root.", call. = FALSE)
    }
    path <- parent
  }
}

path_project <- function(...) {
  file.path(project_root(), ...)
}

dir_create <- function(path) {
  if (!dir.exists(path)) {
    dir.create(path, recursive = TRUE, showWarnings = FALSE)
  }
  invisible(path)
}

require_package <- function(package) {
  if (!requireNamespace(package, quietly = TRUE)) {
    stop(
      sprintf(
        "Missing R package `%s`. Install dependencies with `Rscript -e \"install.packages('%s')\"` or restore renv.",
        package,
        package
      ),
      call. = FALSE
    )
  }
}

read_env <- function(name, default = NULL) {
  value <- Sys.getenv(name, unset = NA_character_)
  if (is.na(value) || !nzchar(value)) {
    return(default)
  }
  value
}

load_env_file <- function(path = path_project(".env")) {
  if (!file.exists(path)) {
    return(invisible(FALSE))
  }

  lines <- readLines(path, warn = FALSE)
  lines <- trimws(lines)
  lines <- lines[nzchar(lines) & !startsWith(lines, "#")]

  for (line in lines) {
    parts <- strsplit(line, "=", fixed = TRUE)[[1]]
    if (length(parts) < 2) {
      next
    }
    key <- trimws(parts[[1]])
    value <- trimws(paste(parts[-1], collapse = "="))
    value <- sub("^['\"]", "", value)
    value <- sub("['\"]$", "", value)

    if (nzchar(key) && !nzchar(Sys.getenv(key, unset = ""))) {
      Sys.setenv(stats::setNames(value, key))
    }
  }

  invisible(TRUE)
}

json_escape <- function(value) {
  value <- gsub("\\\\", "\\\\\\\\", value)
  value <- gsub('"', '\\"', value, fixed = TRUE)
  value <- gsub("\n", "\\n", value, fixed = TRUE)
  value <- gsub("\r", "\\r", value, fixed = TRUE)
  value <- gsub("\t", "\\t", value, fixed = TRUE)
  value
}

to_json_value <- function(x) {
  if (is.data.frame(x)) {
    rows <- lapply(seq_len(nrow(x)), function(i) as.list(x[i, , drop = FALSE]))
    return(to_json_value(rows))
  }

  if (is.list(x)) {
    names_x <- names(x)
    if (!is.null(names_x) && all(nzchar(names_x))) {
      items <- vapply(
        names_x,
        function(name) sprintf('"%s": %s', json_escape(name), to_json_value(x[[name]])),
        character(1)
      )
      return(sprintf("{\n%s\n}", paste(paste0("  ", items), collapse = ",\n")))
    }

    items <- vapply(x, to_json_value, character(1))
    return(sprintf("[%s]", paste(items, collapse = ", ")))
  }

  if (length(x) == 0 || all(is.na(x))) {
    return("null")
  }

  if (length(x) > 1) {
    return(sprintf("[%s]", paste(vapply(as.list(x), to_json_value, character(1)), collapse = ", ")))
  }

  if (inherits(x, c("Date", "POSIXct", "POSIXlt"))) {
    return(sprintf('"%s"', json_escape(format(x))))
  }

  if (is.logical(x)) {
    return(if (isTRUE(x)) "true" else "false")
  }

  if (is.numeric(x)) {
    return(format(x, scientific = FALSE, trim = TRUE))
  }

  sprintf('"%s"', json_escape(as.character(x)))
}

write_json <- function(x, path, pretty = TRUE) {
  dir_create(dirname(path))

  if (requireNamespace("jsonlite", quietly = TRUE)) {
    jsonlite::write_json(x, path, pretty = pretty, auto_unbox = TRUE, na = "null")
  } else {
    writeLines(to_json_value(x), path, useBytes = TRUE)
  }

  invisible(path)
}

write_table_data <- function(data, path) {
  dir_create(dirname(path))
  ext <- tolower(tools::file_ext(path))

  if (identical(ext, "parquet")) {
    require_package("arrow")
    arrow::write_parquet(data, path)
  } else if (identical(ext, "rds")) {
    saveRDS(data, path)
  } else if (identical(ext, "csv")) {
    utils::write.csv(data, path, row.names = FALSE, fileEncoding = "UTF-8")
  } else {
    stop(sprintf("Unsupported table output extension: %s", ext), call. = FALSE)
  }

  invisible(path)
}

read_table_data <- function(path) {
  ext <- tolower(tools::file_ext(path))

  if (identical(ext, "parquet")) {
    require_package("arrow")
    return(as.data.frame(arrow::read_parquet(path)))
  }
  if (identical(ext, "rds")) {
    return(readRDS(path))
  }
  if (identical(ext, "csv")) {
    return(utils::read.csv(path, stringsAsFactors = FALSE, check.names = FALSE))
  }

  stop(sprintf("Unsupported table input extension: %s", ext), call. = FALSE)
}

load_env_file()

