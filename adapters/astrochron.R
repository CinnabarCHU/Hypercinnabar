# Invoke the installed astrochron public functions with the supplied inputs.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 2L)
src <- args[1]; dest <- args[2]
dir.create(dest, showWarnings = FALSE, recursive = TRUE)
request <- jsonlite::fromJSON(file.path(src, "request.json"))
p <- request$params
read_table <- function(stem) read.csv(file.path(src, paste0(stem, ".csv")), check.names = FALSE)
if (file.exists(file.path(src, "data.csv"))) d <- read_table("data")
pkg <- as.character(packageVersion("astrochron"))
if (request$track == "case") {
    out <- switch(request$operation,
        tune = astrochron::tune(d, read_table("controls"), extrapolate=p$extrapolate, genplot=FALSE, verbose=FALSE),
        constant_rate = astrochron::constantSedrate(d, p$rate_m_per_ka, begin=p$begin_ka, genplot=FALSE, verbose=FALSE),
        integrate_rate = astrochron::sedrate2time(d, genplot=FALSE, verbose=FALSE),
        linear = astrochron::linterp(d, dt=p$step, genplot=FALSE, verbose=FALSE),
        ar1 = {
            RNGkind("Mersenne-Twister", "Inversion", "Rejection")
            assign(".Random.seed", as.integer(p$rng_state), envir=.GlobalEnv)
            astrochron::ar1(npts=p$npts, rho=p$rho, genplot=FALSE, verbose=FALSE)
        },
        stop("Unsupported operation: ", request$operation))
    names(out) <- request$output_columns
    options(digits=17)
    write.csv(out, file.path(dest,"result.csv"), row.names=FALSE, quote=FALSE)
} else if (request$id == "odp926b-timeopt") {
    grid <- astrochron::linterp(d, dt=.1, genplot=FALSE, verbose=FALSE)
    # Explicit modern approximation: one nominal cutoff wavelength across the LOESS span.
    fraction <- (1/.06) / diff(range(grid[,1]))
    residual <- astrochron::noLow(grid, smooth=fraction, genplot=FALSE, verbose=FALSE)
    scan <- astrochron::timeOpt(residual, sedmin=1.3, sedmax=5, numsed=100, linLog=1,
        flow=.035, fhigh=.065, roll=1000, output=1, genplot=FALSE, verbose=FALSE)
    write.csv(scan, file.path(dest,"timeopt-scan.csv"), row.names=FALSE)
    jsonlite::write_json(list(rate_cm_per_ka=scan$sedrate[which.max(scan$r2_opt)]),
        file.path(dest,"result.json"), auto_unbox=TRUE, digits=16)
} else {
    stop("Unsupported task: ", request$id)
}
jsonlite::write_json(list(method="astrochron",version=pkg, runtime=R.version.string),
    file.path(dest,"method.json"), auto_unbox=TRUE)
