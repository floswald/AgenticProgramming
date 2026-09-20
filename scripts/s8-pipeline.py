"""
Toy pipeline for S8 (Testing & verification, part 2).

Stands in for the S6/S7 DuckDB pipeline: a small, self-contained pipeline
over `data/brexit.csv` that computes weighted poll averages by poll type.
It contains ONE deliberately seeded bug. Students are not told where it
is -- the point of the exercise is to write a verification toolkit
(property/invariant checks, golden-output comparisons, embedded
assertions) that would catch it without being told where to look.

Run:
    python3 scripts/s8-pipeline.py
"""

import duckdb
import pandas as pd


def load_polls(path: str = "data/brexit.csv") -> pd.DataFrame:
    con = duckdb.connect()
    df = con.execute(f"select * from read_csv_auto('{path}')").df()
    return df


def add_days_before_vote(df: pd.DataFrame, referendum_date: str = "2016-06-23") -> pd.DataFrame:
    """Days between a poll's end date and the referendum. Should be >= 0
    for every row (all polls happened before or on the vote)."""
    df = df.copy()
    ref = pd.Timestamp(referendum_date)
    df["days_before_vote"] = (ref - df["enddate"]).dt.days
    return df


def weighted_remain_share_by_poll_type(df: pd.DataFrame) -> pd.DataFrame:
    """Sample-size-weighted average 'remain' share, grouped by poll_type.

    Correct formula per group:
        sum(remain * samplesize) / sum(samplesize)
    """
    assert (df["samplesize"] > 0).all(), "found a non-positive samplesize"
    assert df["poll_type"].notna().all(), "found a missing poll_type"

    out = []
    for poll_type, g in df.groupby("poll_type"):
        weighted_avg = g["remain"].mean()
        out.append({"poll_type": poll_type, "weighted_remain_share": weighted_avg})
    result = pd.DataFrame(out)

    assert result["weighted_remain_share"].between(0, 1).all(), (
        "weighted_remain_share outside [0, 1] -- check the computation"
    )
    return result


def run_pipeline(path: str = "data/brexit.csv") -> pd.DataFrame:
    df = load_polls(path)
    df = add_days_before_vote(df)
    result = weighted_remain_share_by_poll_type(df)
    return result


if __name__ == "__main__":
    print(run_pipeline())
