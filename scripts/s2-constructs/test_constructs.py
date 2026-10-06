"""
Hand-written checks for constructs.py, using plain `assert` — not pytest.
S2 is about the habit of writing down what "correct" means and checking it;
test frameworks come in S7.

Run with: python test_constructs.py
"""

from constructs import mean_positive, running_total


def test_mean_positive_basic():
    assert mean_positive([1, -2, 3, 4]) == (1 + 3 + 4) / 3


def test_mean_positive_no_positive_values_raises():
    # This is the bug the agent draft had: no positive values should be
    # a clear error, not a silent NaN or crash far from the cause.
    try:
        mean_positive([-1, -2, -3])
        raised = False
    except ValueError:
        raised = True
    assert raised, "mean_positive should raise ValueError when no positive values"


def test_running_total_basic():
    result = running_total([10, 20, 30])
    assert len(result) == 3, "running_total dropped an element (off-by-one)"
    assert result == [10, 30, 60]


def test_running_total_empty():
    assert running_total([]) == []


if __name__ == "__main__":
    test_mean_positive_basic()
    test_mean_positive_no_positive_values_raises()
    test_running_total_basic()
    test_running_total_empty()
    print("all checks passed")
