"""scripts/s7/pipeline.py

Small stand-in for the S6 DuckDB pipeline, used here so S7 has real
transformations to write unit tests against. Once S6 (#7) lands with its
own pipeline, these tests should be pointed at that pipeline instead --
the *tests* are the point of this session, not this particular script.

Pipeline: read a table of Brexit referendum polls, flag polls whose
reported shares don't add up, and summarise valid polls by pollster.
"""

from __future__ import annotations

import duckdb
import pandas as pd


def read_polls(path: str) -> pd.DataFrame:
    """Read the polls table into a DataFrame via DuckDB."""
    con = duckdb.connect()
    df = con.execute(f"SELECT * FROM read_csv_auto('{path}')").fetchdf()
    con.close()
    return df


def check_shares(df: pd.DataFrame, tol: float = 0.01) -> pd.DataFrame:
    """Flag polls whose remain/leave/undecided shares don't sum to ~1.

    This is the kind of silent-data-decision check emphasized in S6/S7:
    an agent asked to "clean this data" might just trust the columns.
    """
    required = {"remain", "leave", "undecided"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"check_shares: missing columns {missing}")

    out = df.copy()
    out["share_total"] = out["remain"] + out["leave"] + out["undecided"]
    out["valid"] = (out["share_total"] - 1).abs() <= tol
    return out


def pollster_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarise valid polls by pollster: n_polls, avg_remain, avg_leave.

    Rows that failed `check_shares()`, or have a non-positive sample
    size, are dropped before summarising -- they are not trustworthy
    inputs.
    """
    if "valid" not in df.columns:
        raise ValueError("pollster_summary: run check_shares() first")

    kept = df[df["valid"] & (df["samplesize"] > 0)]
    out = (
        kept.groupby("pollster")
        .agg(n_polls=("pollster", "size"), avg_remain=("remain", "mean"), avg_leave=("leave", "mean"))
        .reset_index()
    )
    return out
