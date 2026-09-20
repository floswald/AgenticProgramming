"""scripts/s7/test_pipeline.py

pytest unit tests for scripts/s7/pipeline.py.
Run with: pytest scripts/s7/test_pipeline.py -v
"""

import pandas as pd
import pytest

from pipeline import check_shares, pollster_summary


# --- fixture -------------------------------------------------------------
# A fixture builds fixed, known input so we know exactly what the "right"
# answer is -- never write a unit test whose expected value you had to
# compute by re-running the code under test.
@pytest.fixture
def polls() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "pollster": ["A", "A", "B", "C"],
            "samplesize": [1000, 1000, 500, -1],
            "remain": [0.52, 0.48, 0.50, 0.50],
            "leave": [0.48, 0.50, 0.50, 0.50],
            "undecided": [0.00, 0.00, 0.00, 0.00],
        }
    )


def test_check_shares_flags_rows_that_sum_to_one(polls):
    # Arrange: `polls` fixture
    # Act
    out = check_shares(polls)
    # Assert
    assert list(out["share_total"]) == [1.00, 0.98, 1.00, 1.00]
    assert list(out["valid"]) == [True, False, True, True]


def test_check_shares_respects_tolerance(polls):
    # row 2 sums to 0.98 -- a tolerance of 0.03 should let it through
    out = check_shares(polls, tol=0.03)
    assert out["valid"].all()


def test_pollster_summary_drops_invalid_and_nonpositive_samplesize(polls):
    out = pollster_summary(check_shares(polls))
    # Row 2 (pollster A, share_total 0.98) and row 4 (pollster C,
    # samplesize -1) should both be dropped.
    assert set(out["pollster"]) == {"A", "B"}


def test_pollster_summary_aggregates_single_valid_row(polls):
    out = pollster_summary(check_shares(polls))
    b_row = out[out["pollster"] == "B"].iloc[0]
    assert b_row["n_polls"] == 1
    assert b_row["avg_remain"] == pytest.approx(0.50)


def test_pollster_summary_on_all_invalid_input_returns_zero_rows():
    # Edge case: what happens when nothing survives filtering? An
    # agent's first draft often forgets this and errors out, or worse,
    # silently returns something for the wrong pollster.
    bad = pd.DataFrame(
        {
            "pollster": ["Z"],
            "samplesize": [100],
            "remain": [0.9],
            "leave": [0.9],
            "undecided": [0.9],
        }
    )
    out = pollster_summary(check_shares(bad))
    assert len(out) == 0


def test_check_shares_raises_clearly_on_missing_columns():
    # We are not testing pandas or duckdb internals here -- only our own
    # assumption that the required columns exist. This is the "don't
    # bother testing the library, test your usage of it" line from S7.
    bad = pd.DataFrame({"pollster": ["A"], "remain": [0.5]})
    with pytest.raises(ValueError):
        check_shares(bad)
