# Replay one demonstration journal from a fresh R process:
# Rscript --vanilla replay.R DIRECTORY/tune NEW_DIRECTORY
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 2L)
source_dir <- normalizePath(args[1], mustWork = TRUE)
stopifnot(dir.create(args[2], recursive = FALSE))
output_dir <- normalizePath(args[2])
from_source <- function(name) file.path(source_dir, name)
decode <- function(line) jsonlite::fromJSON(line, simplifyVector = FALSE)
meta <- decode(paste(readLines(from_source("manifest.json"), warn = FALSE), collapse = "\n"))
journal <- lapply(readLines(from_source("events.jsonl")), decode)
init <- journal[[1]]
fin <- journal[[length(journal)]]
stopifnot(init$attr == "init", fin$attr == "fin", fin$info$status == "done",
          identical(meta$backend, "R"), identical(meta$package, "astrochron"),
          identical(init$info$op, paste(meta$package, meta[["function"]], sep = "::")),
          identical(as.character(getRversion()), meta$r_version),
          identical(as.character(packageVersion(meta$package)), meta$package_version))

read_value <- function(name) {
    h5 <- hdf5r::H5File$new(from_source(name), "r")
    on.exit(h5$close_all())
    h5[["value"]]$read()
}
param_h5 <- hdf5r::H5File$new(from_source(init$info$params), "r")
args_by_name <- lapply(names(meta$arguments), function(n) {
    spec <- meta$arguments[[n]]
    x <- param_h5[[paste0("value/", n)]]$read()
    switch(spec$kind,
           "data.frame" = {
               x <- as.data.frame(x)
               names(x) <- unlist(spec$columns, use.names = FALSE)
               row.names(x) <- unlist(spec$row_names, use.names = FALSE)
               x
           },
           "logical" = as.logical(x), "integer" = as.integer(x),
           "double" = as.double(x), stop("Unsupported input type"))
})
names(args_by_name) <- names(meta$arguments)
param_h5$close_all()

run <- function() {
    if (!is.null(meta$rng)) {
        do.call(RNGkind, unname(meta$rng$kind))
        assign(".Random.seed", as.integer(read_value(meta$rng$file)), envir = .GlobalEnv)
    }
    if (!is.null(meta$graphics)) {
        g <- meta$graphics
        grDevices::png(file.path(output_dir, g$file), width = g$width, height = g$height,
                       res = g$res, bg = g$bg)
        dev_number <- grDevices::dev.cur()
        on.exit(grDevices::dev.off(dev_number))
    }
    fn <- getExportedValue(meta$package, meta[["function"]])
    result <- do.call(fn, args_by_name)
    for (entry in journal) {
        if (entry$attr != "event") next
        detail <- entry$info$details
        stopifnot(identical(detail$op, "graphics::abline"),
                  identical(as.integer(graphics::par("mfg")), as.integer(unlist(detail$panel))))
        do.call(graphics::abline, detail$args)
    }
    result
}
out <- run()
# The saved result is first opened after execution. Verify types, labels and values separately.
expected <- read_value(fin$info$retval)
stopifnot(identical(class(out), meta[["return"]]$kind),
          identical(names(out), unlist(meta[["return"]]$columns, use.names = FALSE)),
          identical(row.names(out), unlist(meta[["return"]]$row_names, use.names = FALSE)),
          identical(unname(as.matrix(out)), unname(expected)))
write.csv(out, file.path(output_dir, "result.csv"), row.names = FALSE)
cat(init$info$op, nrow(out), "x", ncol(out), "identical values and labels\n")
