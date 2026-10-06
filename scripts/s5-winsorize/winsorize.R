# Starting fixture for the S5 live demo. Untested.

winsorize <- function(x, p = 0.05) {
  lo <- quantile(x, p, names = FALSE)
  hi <- quantile(x, p, names = FALSE)
  x[x < lo] <- lo
  x[x > hi] <- hi
  x
}
