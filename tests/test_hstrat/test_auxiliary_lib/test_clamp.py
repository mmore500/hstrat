import math

import pytest

from hstrat._auxiliary_lib import clamp, jit


@pytest.mark.parametrize(
    "value, lo, hi, expected",
    [
        (5.0, 0.0, 3.0, 3.0),
        (-1.0, 0.0, 3.0, 0.0),
        (2.0, 0.0, 3.0, 2.0),
        (0.0, 0.0, 3.0, 0.0),
        (3.0, 0.0, 3.0, 3.0),
        (1.0, 1.0, 1.0, 1.0),
        (7, 2, 4, 4),
        (-7, -4, -2, -4),
    ],
)
def test_clamp(value, lo, hi, expected):
    assert clamp(value, lo, hi) == expected


def test_clamp_nan():
    # std::clamp semantics: comparisons with nan are false, so nan passes
    assert math.isnan(clamp(math.nan, 0.0, 1.0))


def test_clamp_within_jit():
    @jit(nopython=True)
    def clamp_sum(lo: float, hi: float) -> float:
        total = 0.0
        for i in range(-5, 6):
            total += clamp(float(i), lo, hi)
        return total

    assert clamp_sum(-1.0, 2.0) == -1.0 * 5 + 0.0 + 1.0 + 2.0 * 4


def test_clamp_invalid_bounds():
    with pytest.raises(AssertionError):
        clamp(0.0, 1.0, 0.0)
