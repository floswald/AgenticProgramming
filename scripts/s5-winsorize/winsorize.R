# Starting fixture for the S5 live demo. Untested, contains a seeded bug:
# the upper cutoff uses quantile(x, p) instead of quantile(x, 1 - p), so it
# caps far too many high values instead of just the top p fraction.

winsorize <- function(x, p = 0.05) {
  lo <- quantile(x, p, names = FALSE)
  hi <- quantile(x, p, names = FALSE)  # bug: should be quantile(x, 1 - p)
  x[x < lo] <- lo
  x[x > hi] <- hi
  x
}
