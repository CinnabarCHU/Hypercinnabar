# Execute the released astrochron 1.8 R functions on the benchmark's measured data.
options(digits=17)
dir.create("evidence", showWarnings=FALSE)
for (f in c("linterp_v11", "noLow_v5", "periodogram_v21", "tanerFC_v1", "hilbert_v18", "timeOpt_v19")) {
  source(file.path("astrochron", "R", paste0("FUNCTION-", f, ".R")))
}
dat <- read.csv("benchmarks/fixtures/records/odp926b.csv")
grid <- linterp(dat, dt=0.1, genplot=FALSE, verbose=FALSE)
fraction <- (1/0.06)/diff(range(grid[,1]))
residual <- noLow(grid, smooth=fraction, genplot=FALSE, verbose=FALSE)
write.csv(residual, "evidence/odp926b-prepared-m.csv", row.names=FALSE)
scan <- timeOpt(residual, sedmin=1.3, sedmax=5, numsed=100, linLog=1, limit=TRUE,
                fit=1, fitModPwr=TRUE, flow=.035, fhigh=.065, roll=1000, detrend=TRUE,
                output=1, genplot=FALSE, verbose=FALSE)
write.csv(scan, "evidence/odp926b-astrochron.csv", row.names=FALSE)
archived <- read.csv("benchmarks/baselines/odp926b-timeopt.csv")
stopifnot(isTRUE(all.equal(as.matrix(scan), as.matrix(archived), tolerance=1e-8, check.attributes=FALSE)))
