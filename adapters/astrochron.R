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
method <- list(method="astrochron",version=pkg,runtime=R.version.string)
if (request$track == "case") {
    out <- switch(request$operation,
        tune = astrochron::tune(d, read_table("controls"), extrapolate=p$extrapolate, genplot=FALSE, verbose=FALSE),
        constant_rate = astrochron::constantSedrate(d, p$rate_m_per_ka, begin=p$begin_ka, genplot=FALSE, verbose=FALSE),
        integrate_rate = astrochron::sedrate2time(d, genplot=FALSE, verbose=FALSE),
        linear = astrochron::linterp(d, dt=p$step, genplot=FALSE, verbose=FALSE),
        hilbert_envelope = astrochron::hilbert(d, padfac=1, demean=FALSE, genplot=FALSE, verbose=FALSE),
        imbrie_euler = astrochron::imbrie(d, Tm=p$tm_ka, b=p$b, initial=p$initial,
            burnin=1, standardize=FALSE, genplot=0, verbose=FALSE),
        segmented_clock = {
            nodes <- read_table("controls")
            age <- numeric(nrow(d))
            for (s in unique(d[[1]])) {
                queries <- d[[1]] == s
                n <- nodes[[1]] == s
                age[queries] <- stats::approx(nodes[n,2], nodes[n,3], xout=d[queries,2])$y
            }
            method$operation <- "stats::approx within each sedimentary segment"
            data.frame(d, age)
        },
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
} else if (request$id %in% c("xiamaling-precession","walvis1262-precession")) {
    grid <- astrochron::linterp(d, dt=p$interpolation_step_m, genplot=FALSE, verbose=FALSE)
    # In astrochron 1.8 the marginal summaries are printed, not returned in the fit vector.
    transcript <- capture.output(fit <- astrochron::timeOptB(grid, age=p$age_ma,
        sedmin=p$rate_search_cm_per_ka[1], sedmax=p$rate_search_cm_per_ka[2],
        kmin=p$precession_search_arcsec_yr[1], kmax=p$precession_search_arcsec_yr[2],
        numsed=61, numk=61, genplot=FALSE, verbose=TRUE))
    section <- grep("Marginal posterior PDF", transcript, fixed=TRUE)
    stopifnot(length(section) == 1L)
    lines <- transcript[seq(section+1L, min(section+5L,length(transcript)))]
    marginal <- function(symbol) {
        line <- grep(paste0("^",symbol,":"), lines, value=TRUE)
        stopifnot(length(line) == 1L)
        numbers <- as.numeric(regmatches(line, gregexpr("[+-]?[0-9]+(?:\\.[0-9]+)?",line,perl=TRUE))[[1]])
        stopifnot(length(numbers) == 5L, all(is.finite(numbers)))
        numbers
    }
    u <- marginal("u")
    k <- marginal("k")
    day <- astrochron::alodfromk(k[2], k[3], genplot=FALSE, verbose=FALSE)
    writeLines(transcript, file.path(dest,"timeoptb-summary.txt"))
    jsonlite::write_json(list(rate_cm_per_ka=u[2], precession_arcsec_yr=k[2], lod_h=day[1,"lod"],
        rate_ci95=u[4:5], precession_ci95=k[4:5]), file.path(dest,"result.json"), auto_unbox=TRUE, digits=16)
    method$operation <- "timeOptB 61 by 61 grid, marginal means, alodfromk evaluated at mean k"
} else {
    stop("Unsupported task: ", request$id)
}
jsonlite::write_json(method,
    file.path(dest,"method.json"), auto_unbox=TRUE)
