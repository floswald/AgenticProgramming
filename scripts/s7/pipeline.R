# scripts/s7/pipeline.R
#
# Small stand-in for the S6 DuckDB pipeline, used here so S7 has real
# transformations to write unit tests against. Once S6 (#7) lands with its
# own pipeline, these tests should be pointed at that pipeline instead —
# the *tests* are the point of this session, not this particular script.
#
# Pipeline: read a table of Brexit referendum polls, flag polls whose
# reported shares don't add up, and summarise valid polls by pollster.

library(duckdb)
library(dplyr)

#' Read the polls table into a data frame via DuckDB.
#'
#' @param path path to a CSV with columns: pollster, samplesize, remain,
#'   leave, undecided (at minimum).
#' @return a data.frame/tibble, one row per poll.
read_polls <- function(path) {
  con <- dbConnect(duckdb())
  on.exit(dbDisconnect(con, shutdown = TRUE))
  query <- sprintf("SELECT * FROM read_csv_auto('%s')", path)
  dbGetQuery(con, query)
}

#' Flag polls whose remain/leave/undecided shares don't sum to ~1.
#'
#' This is the kind of silent-data-decision check emphasized in S6/S7:
#' an agent asked to "clean this data" might just trust the columns.
#'
#' @param df data frame with columns remain, leave, undecided.
#' @return df with two extra columns: share_total, valid.
check_shares <- function(df, tol = 0.01) {
  stopifnot(all(c("remain", "leave", "undecided") %in% names(df)))
  df$share_total <- df$remain + df$leave + df$undecided
  df$valid <- abs(df$share_total - 1) <= tol
  df
}

#' Summarise valid polls by pollster: number of polls and mean remain/leave.
#'
#' Rows that failed `check_shares()`, or have a non-positive sample size,
#' are dropped before summarising — they are not trustworthy inputs.
#'
#' @param df output of `check_shares()`.
#' @return a data.frame with columns: pollster, n_polls, avg_remain,
#'   avg_leave.
pollster_summary <- function(df) {
  stopifnot("valid" %in% names(df))
  df %>%
    filter(valid, samplesize > 0) %>%
    group_by(pollster) %>%
    summarise(
      n_polls = n(),
      avg_remain = mean(remain),
      avg_leave = mean(leave),
      .groups = "drop"
    )
}
