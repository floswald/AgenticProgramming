# Hand-written checks for constructs.R, using plain stopifnot() -- not
# testthat. S2 is about the habit of writing down what "correct" means and
# checking it; test frameworks come in S7.
#
# Run with: Rscript test_constructs.R

source("constructs.R")

# mean_positive: basic case
stopifnot(mean_positive(c(1, -2, 3, 4)) == (1 + 3 + 4) / 3)

# mean_positive: this is the bug the agent draft had -- no positive values
# should be a clear error, not a silent NaN.
raised <- tryCatch(
  {
    mean_positive(c(-1, -2, -3))
    FALSE
  },
  error = function(e) TRUE
)
stopifnot(raised)

# running_total: basic case -- catches the off-by-one from the agent draft
result <- running_total(c(10, 20, 30))
stopifnot(length(result) == 3)
stopifnot(all(result == c(10, 30, 60)))

# running_total: empty input
stopifnot(length(running_total(numeric(0))) == 0)

cat("all checks passed\n")
