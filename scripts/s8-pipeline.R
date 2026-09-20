# Toy pipeline for S8 (Testing & verification, part 2).
#
# Stands in for the S6/S7 DuckDB pipeline: a small, self-contained pipeline
# over data/brexit.csv that computes weighted poll averages by poll type.
# It contains ONE deliberately seeded bug -- the same one as
# scripts/s8-pipeline.py, kept in sync so the R and Python tracks teach the
# same lesson. Students are not told where the bug is: the point of the
# exercise is to write a verification toolkit (property/invariant checks,
# golden-output comparisons, embedded assertions) that would catch it
# without being told where to look.
#
# Run:
#   Rscript scripts/s8-pipeline.R

suppressPackageStartupMessages({
  library(DBI)
  library(duckdb)
})

load_polls <- function(path = "data/brexit.csv") {
  con <- dbConnect(duckdb())
  on.exit(dbDisconnect(con, shutdown = TRUE))
  df <- dbGetQuery(con, sprintf("select * from read_csv_auto('%s')", path))
  df$startdate <- as.Date(df$startdate)
  df$enddate <- as.Date(df$enddate)
  df
}

add_days_before_vote <- function(df, referendum_date = "2016-06-23") {
  ref <- as.Date(referendum_date)
  df$days_before_vote <- as.numeric(ref - df$enddate)
  df
}

# Sample-size-weighted average `remain` share, grouped by poll_type.
#
# Correct formula per group:
#   sum(remain * samplesize) / sum(samplesize)
weighted_remain_share_by_poll_type <- function(df) {
  stopifnot(
    "found a non-positive samplesize" = all(df$samplesize > 0),
    "found a missing poll_type" = all(!is.na(df$poll_type))
  )

  groups <- split(df, df$poll_type)
  out <- do.call(rbind, lapply(names(groups), function(pt) {
    g <- groups[[pt]]
    weighted_avg <- mean(g$remain)
    data.frame(poll_type = pt, weighted_remain_share = weighted_avg)
  }))
  rownames(out) <- NULL

  stopifnot(
    "weighted_remain_share outside [0, 1] -- check the computation" =
      all(out$weighted_remain_share >= 0 & out$weighted_remain_share <= 1)
  )
  out
}

run_pipeline <- function(path = "data/brexit.csv") {
  df <- load_polls(path)
  df <- add_days_before_vote(df)
  weighted_remain_share_by_poll_type(df)
}

if (sys.nframe() == 0) {
  print(run_pipeline())
}
