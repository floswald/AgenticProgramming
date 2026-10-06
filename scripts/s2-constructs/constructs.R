# S2 reference solution — corrected versions of the functions drafted (with
# bugs) in s2-constructs.qmd. See that page for the buggy "agent draft"
# versions and the reasoning behind each fix.

mean_positive <- function(values) {
  # Average of the positive numbers in `values`.
  # Raises an error if there are no positive numbers, instead of the
  # agent draft's silent NaN.
  positives <- values[values > 0]
  if (length(positives) == 0) {
    stop("no positive values in input")
  }
  sum(positives) / length(positives)
}

running_total <- function(values) {
  # Cumulative sum of `values`, including the first element.
  # The agent draft skipped the first element (off-by-one on `values[-1]`).
  # This version includes it and handles the empty vector.
  if (length(values) == 0) {
    return(numeric(0))
  }
  total <- 0
  result <- c()
  for (v in values) {
    total <- total + v
    result <- c(result, total)
  }
  result
}
