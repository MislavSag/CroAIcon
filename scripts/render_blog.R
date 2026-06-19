if (!nzchar(Sys.which("quarto"))) {
  stop("Quarto CLI is not available on PATH.", call. = FALSE)
}

status <- system2("quarto", c("render"), stdout = TRUE, stderr = TRUE)
cat(paste(status, collapse = "\n"), "\n")

exit_code <- attr(status, "status")
if (!is.null(exit_code) && exit_code != 0) {
  quit(status = exit_code)
}

