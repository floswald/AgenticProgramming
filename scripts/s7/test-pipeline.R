# scripts/s7/test-pipeline.R
#
# testthat unit tests for scripts/s7/pipeline.R.
# Run with: testthat::test_file("scripts/s7/test-pipeline.R")

library(testthat)
source("pipeline.R")

# --- fixture -----------------------------------------------------------
# A small, hand-built table is a *fixture*: fixed, known input so we know
# exactly what the "right" answer is. Never write a unit test whose
# expected value you had to compute by re-running the code under test.
make_polls <- function() {
  data.frame(
    pollster = c("A", "A", "B", "C"),
    samplesize = c(1000, 1000, 500, -1),
    remain = c(0.52, 0.48, 0.50, 0.50),
    leave = c(0.48, 0.50, 0.50, 0.50),
    undecided = c(0.00, 0.00, 0.00, 0.00),
    stringsAsFactors = FALSE
  )
}

test_that("check_shares flags rows that sum to 1 as valid", {
  # Arrange
  polls <- make_polls()

  # Act
  out <- check_shares(polls)

  # Assert
  expect_equal(out$share_total, c(1.00, 0.98, 1.00, 1.00))
  expect_equal(out$valid, c(TRUE, FALSE, TRUE, TRUE))
})

test_that("check_shares respects the tolerance argument", {
  polls <- make_polls()
  # row 2 sums to 0.98 -- a tolerance of 0.03 should let it through
  out <- check_shares(polls, tol = 0.03)
  expect_true(all(out$valid))
})

test_that("pollster_summary drops invalid rows and non-positive sample sizes", {
  polls <- make_polls()
  out <- pollster_summary(check_shares(polls))

  # Row 2 (pollster A, share_total 0.98) and row 4 (pollster C,
  # samplesize -1) should both be dropped.
  expect_setequal(out$pollster, c("A", "B"))
})

test_that("pollster_summary aggregates correctly for a single valid row", {
  polls <- make_polls()
  out <- pollster_summary(check_shares(polls))
  b_row <- out[out$pollster == "B", ]

  expect_equal(b_row$n_polls, 1)
  expect_equal(b_row$avg_remain, 0.50)
})

test_that("pollster_summary on an empty (all-invalid) input returns zero rows", {
  # Edge case: what happens when nothing survives filtering? An agent's
  # first draft often forgets this and errors out, or worse, silently
  # returns something for the wrong pollster.
  polls <- data.frame(
    pollster = "Z",
    samplesize = 100,
    remain = 0.9,
    leave = 0.9,
    undecided = 0.9
  )
  out <- pollster_summary(check_shares(polls))
  expect_equal(nrow(out), 0)
})

test_that("check_shares errors clearly on missing columns", {
  # We are not testing dplyr or duckdb internals here -- only our own
  # assumption that the required columns exist. This is the "don't
  # bother testing the library, test your usage of it" line from S7.
  bad <- data.frame(pollster = "A", remain = 0.5)
  expect_error(check_shares(bad))
})
