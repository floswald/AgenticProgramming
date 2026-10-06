"""
S2 reference solution — corrected versions of the functions drafted (with bugs)
in s2-constructs.qmd. See that page for the buggy "agent draft" versions and
the reasoning behind each fix.
"""


def mean_positive(values):
    """Average of the positive numbers in `values`.

    Raises ValueError if there are no positive numbers, instead of the
    agent draft's silent ZeroDivisionError-on-Python /
    NaN-with-no-warning-in-R behavior.
    """
    positives = [v for v in values if v > 0]
    if len(positives) == 0:
        raise ValueError("no positive values in input")
    return sum(positives) / len(positives)


def running_total(values):
    """Cumulative sum of `values`, including the first element.

    The agent draft skipped the first element (off-by-one on the slice
    `values[1:]`). This version includes it and handles the empty list.
    """
    total = 0
    result = []
    for v in values:
        total += v
        result.append(total)
    return result
