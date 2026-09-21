"""
S8 reference solution: a verification toolkit for scripts/s8-pipeline.py.

This is the *instructor / worked-example* answer key -- shown in class only
after students have attempted the exercise themselves. It demonstrates the
four patterns covered in S8, each of which is capable of catching the
seeded bug in `weighted_remain_share_by_poll_type` on its own:

1. Property-based / invariant checks (Hypothesis)   -> test_invariant_*
2. Golden-output comparison (hand-computed expected) -> test_golden_*
3. Embedded assertions inside the pipeline itself    -> test_embedded_assertion_*
   (the assertions live in s8-pipeline.py; here we confirm they fire on
   bad input and stay silent on good input)
4. Systematic check for a "silent data decision"     -> test_weighting_*

Note on (3): the embedded assertions guard against bad *inputs*
(non-positive samplesize, missing poll_type) and implausible *outputs*
(a share outside [0, 1]). They do NOT catch today's seeded bug -- the
buggy output is still a valid share in [0, 1], computed from valid
inputs. That's deliberate: it shows assertions and golden/recomputation
checks answer different questions (see the Recap table in the slides).

Run:
    pytest scripts/test_s8_pipeline.py -v

Expected result against the buggy pipeline as shipped: the invariant tests
(1) and the "identical polls" property test pass -- they don't know the
bug exists and don't need to. `test_golden_weighted_remain_share` and
`test_weighting_is_actually_used` FAIL. That is the demonstration: those
two patterns are the ones that catch this specific bug. Fix the bug in
`weighted_remain_share_by_poll_type` (make it use `samplesize`) and rerun
-- all tests go green.
"""

import math

import pandas as pd
import pytest
from hypothesis import given, strategies as st

from importlib.machinery import SourceFileLoader

pipeline = SourceFileLoader("s8_pipeline", "scripts/s8-pipeline.py").load_module()


@pytest.fixture(scope="module")
def polls():
    return pipeline.load_polls()


# --- 1. Property-based / invariant checks -----------------------------
#
# These don't need to know the "right answer" for any specific number --
# they check a relationship that must hold for *any* valid row of data.

def test_invariant_remain_leave_undecided_sum_to_one(polls):
    total = polls["remain"] + polls["leave"] + polls["undecided"]
    # Individual polls round to 2 decimals and some report "don't know"
    # separately, so allow real slack -- but not unlimited slack.
    assert (total - 1.0).abs().max() < 0.1


def test_invariant_spread_equals_remain_minus_leave(polls):
    implied = polls["remain"] - polls["leave"]
    assert (implied - polls["spread"]).abs().max() < 1e-6


def test_invariant_days_before_vote_never_negative(polls):
    df = pipeline.add_days_before_vote(polls)
    assert (df["days_before_vote"] >= 0).all()


@given(remain=st.floats(min_value=0, max_value=1), n=st.integers(min_value=1, max_value=20))
def test_property_group_of_identical_polls_average_equals_that_value(remain, n):
    """If every poll in a group reports the same `remain` share, ANY
    correctly-weighted (or unweighted) average of that group must equal
    that share exactly -- weighting only matters when values differ."""
    df = pd.DataFrame({
        "poll_type": ["Online"] * n,
        "remain": [remain] * n,
        "samplesize": [1000] * n,
    })
    result = pipeline.weighted_remain_share_by_poll_type(df)
    assert math.isclose(result.loc[0, "weighted_remain_share"], remain, abs_tol=1e-9)


# --- 3. Embedded assertions (defined in s8-pipeline.py) -----------------
#
# These aren't a separate check written in the test file -- they run
# inside the pipeline itself, every time it's called, including when an
# agent calls it unattended. Here we verify they actually fire.

def test_embedded_assertion_rejects_non_positive_samplesize():
    bad = pd.DataFrame({
        "poll_type": ["Online"],
        "remain": [0.5],
        "samplesize": [0],
    })
    with pytest.raises(AssertionError, match="samplesize"):
        pipeline.weighted_remain_share_by_poll_type(bad)


def test_embedded_assertion_rejects_missing_poll_type():
    bad = pd.DataFrame({
        "poll_type": [None],
        "remain": [0.5],
        "samplesize": [1000],
    })
    with pytest.raises(AssertionError, match="poll_type"):
        pipeline.weighted_remain_share_by_poll_type(bad)


def test_embedded_assertion_stays_silent_on_valid_data(polls):
    # Should not raise.
    pipeline.weighted_remain_share_by_poll_type(polls)


# --- 2. Golden-output comparison ---------------------------------------
#
# Hand-computed by summing (remain * samplesize) / sum(samplesize) for
# each poll_type outside the pipeline, from the raw CSV. This is the
# pattern that most directly catches THIS bug: the pipeline's own number
# for "Online" (0.4213) does not match the independently-computed
# sample-size-weighted answer (0.4280).

GOLDEN_WEIGHTED_REMAIN = {
    "Online": 0.42797727636421834,
    "Telephone": 0.48178425815433584,
}


@pytest.mark.parametrize("poll_type,expected", GOLDEN_WEIGHTED_REMAIN.items())
def test_golden_weighted_remain_share(polls, poll_type, expected):
    result = pipeline.weighted_remain_share_by_poll_type(polls)
    got = result.loc[result["poll_type"] == poll_type, "weighted_remain_share"].iloc[0]
    assert math.isclose(got, expected, abs_tol=1e-4), (
        f"{poll_type}: got {got}, expected sample-size-weighted {expected}. "
        "This is the seeded bug: the pipeline is computing a plain mean, "
        "not the sample-size-weighted average its name promises."
    )


# --- 3. Systematic check for a silent data/weighting decision ----------
#
# Independent of any golden value: recompute the weighted average with an
# obviously-correct one-liner and compare. This is the check you'd write
# even if you had never seen the "true" numbers -- it directly targets
# "did this function actually use the column it claims to use".

def test_weighting_is_actually_used(polls):
    naive = polls.groupby("poll_type")["remain"].mean()
    def manual_weighted(g):
        return (g["remain"] * g["samplesize"]).sum() / g["samplesize"].sum()
    truly_weighted = polls.groupby("poll_type").apply(manual_weighted, include_groups=False)

    result = pipeline.weighted_remain_share_by_poll_type(polls).set_index("poll_type")[
        "weighted_remain_share"
    ]

    # If the pipeline's numbers match the *naive* unweighted mean instead
    # of the manually weighted one, `samplesize` is being silently ignored.
    matches_naive = (result - naive).abs().max() < 1e-9
    matches_weighted = (result - truly_weighted).abs().max() < 1e-9
    assert not matches_naive, "pipeline output equals the unweighted mean -- samplesize is being ignored"
    assert matches_weighted, "pipeline output does not match an independently computed weighted mean"
