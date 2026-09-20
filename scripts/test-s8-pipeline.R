# S8 reference solution: a verification toolkit for scripts/s8-pipeline.R
#
# Instructor / worked-example answer key -- show in class only after
# students have attempted the exercise themselves. Mirrors
# scripts/test_s8_pipeline.py: same four patterns, same seeded bug.
#
# Run:
#   Rscript -e 'testthat::test_file("scripts/test-s8-pipeline.R")'
#
# Expected result against the buggy pipeline as shipped: the invariant
# tests and embedded-assertion tests pass (they don't need to know the bug
# exists); the golden-output test and the "weighting is actually used"
# test FAIL. That failure is the demonstration -- those two patterns are
# the ones that catch this bug.

suppressPackageStartupMessages({
  library(testthat)
})

source(testthat::test_path("s8-pipeline.R"))

polls <- load_polls(testthat::test_path("..", "data", "brexit.csv"))

# --- 1. Property-based / invariant checks -------------------------------

test_that("remain + leave + undecided is approximately 1 for every poll", {
  total <- polls$remain + polls$leave + polls$undecided
  expect_true(max(abs(total - 1.0)) < 0.1)
})

test_that("spread equals remain minus leave", {
  implied <- polls$remain - polls$leave
  expect_equal(implied, polls$spread, tolerance = 1e-6)
})

test_that("days_before_vote is never negative", {
  df <- add_days_before_vote(polls)
  expect_true(all(df$days_before_vote >= 0))
})

test_that("a group of identical polls averages to that value regardless of weighting", {
  df <- data.frame(
    poll_type = rep("Online", 10),
    remain = rep(0.37, 10),
    samplesize = rep(1000, 10)
  )
  result <- weighted_remain_share_by_poll_type(df)
  expect_equal(result$weighted_remain_share[1], 0.37, tolerance = 1e-9)
})

# --- 3. Embedded assertions (defined in s8-pipeline.R) -------------------
#
# These run inside the pipeline itself via stopifnot(), every time it's
# called. Here we verify they actually fire on bad input and stay silent
# on good input. Note: they do NOT catch the seeded bug -- the buggy
# output is still a valid share in [0, 1], from valid inputs.

test_that("embedded assertion rejects non-positive samplesize", {
  bad <- data.frame(poll_type = "Online", remain = 0.5, samplesize = 0)
  expect_error(weighted_remain_share_by_poll_type(bad), "samplesize")
})

test_that("embedded assertion rejects missing poll_type", {
  bad <- data.frame(poll_type = NA, remain = 0.5, samplesize = 1000)
  expect_error(weighted_remain_share_by_poll_type(bad), "poll_type")
})

test_that("embedded assertion stays silent on valid data", {
  expect_no_error(weighted_remain_share_by_poll_type(polls))
})

# --- 2. Golden-output comparison -----------------------------------------
#
# Hand-computed sample-size-weighted average from the raw CSV, independent
# of the pipeline code.

golden <- c(Online = 0.42797727636421834, Telephone = 0.48178425815433584)

test_that("weighted remain share matches independently hand-computed golden values", {
  result <- weighted_remain_share_by_poll_type(polls)
  for (pt in names(golden)) {
    got <- result$weighted_remain_share[result$poll_type == pt]
    expect_equal(
      got, golden[[pt]],
      tolerance = 1e-4,
      info = sprintf(
        "%s: got %f, expected sample-size-weighted %f. Seeded bug: the pipeline computes a plain mean, not the weighted average its name promises.",
        pt, got, golden[[pt]]
      )
    )
  }
})

# --- 3. Systematic check for a silent weighting decision -----------------

test_that("samplesize is actually used in the weighted average", {
  naive <- tapply(polls$remain, polls$poll_type, mean)
  truly_weighted <- sapply(split(polls, polls$poll_type), function(g) {
    sum(g$remain * g$samplesize) / sum(g$samplesize)
  })

  result <- weighted_remain_share_by_poll_type(polls)
  got <- setNames(result$weighted_remain_share, result$poll_type)

  matches_naive <- all(abs(got[names(naive)] - naive) < 1e-9)
  matches_weighted <- all(abs(got[names(truly_weighted)] - truly_weighted) < 1e-9)

  expect_false(matches_naive, info = "pipeline output equals the unweighted mean -- samplesize is being ignored")
  expect_true(matches_weighted, info = "pipeline output does not match an independently computed weighted mean")
})
