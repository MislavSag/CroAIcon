if (!exists("path_project")) {
  source(file.path("R", "00_config.R"))
}

write_markdown_table <- function(data, path, digits = 2) {
  dir_create(dirname(path))

  if (requireNamespace("knitr", quietly = TRUE)) {
    table_text <- capture.output(knitr::kable(data, format = "pipe", digits = digits))
    writeLines(table_text, path, useBytes = TRUE)
    return(invisible(path))
  }

  utils::write.table(
    data,
    file = path,
    sep = " | ",
    row.names = FALSE,
    quote = FALSE,
    fileEncoding = "UTF-8"
  )

  invisible(path)
}
