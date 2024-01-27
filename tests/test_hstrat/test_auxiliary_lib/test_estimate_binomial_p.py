import itertools as it

import pytest

from hstrat._auxiliary_lib import estimate_binomial_p


def always_success_sampler():
    """A sampler that always returns success."""
    return True


def never_success_sampler():
    """A sampler that never returns success."""
    return False


_half_success_state = iter(it.cycle([True, False]))


def half_success_sampler():
    """A sampler that returns success half of the time."""
    # Alternate between True and False
    return next(_half_success_state)


@pytest.mark.parametrize(
    "sampler,expected_success",
    [
        (always_success_sampler, 1.0),
        (never_success_sampler, 0.0),
        (half_success_sampler, 0.5),
    ],
)
@pytest.mark.parametrize("precision", [0.02, 0.1])
def test_estimate_binomial_p(sampler, expected_success, precision):
    p_estimate, confint, nobs1 = estimate_binomial_p(
        sampler=sampler, precision=precision, confidence=0.8
    )
    assert abs(p_estimate - expected_success) <= precision
    assert 0 <= confint[1] - confint[0] <= precision
    assert nobs1 > 0

    p_estimate, confint, nobs2 = estimate_binomial_p(
        sampler=sampler, precision=precision, confidence=0.9
    )
    assert abs(p_estimate - expected_success) <= precision
    assert 0 <= confint[1] - confint[0] <= precision
    assert nobs2 > 0
    assert nobs2 > nobs1

    p_estimate, confint, nobs3 = estimate_binomial_p(
        sampler=sampler, precision=precision / 2, confidence=0.8
    )
    assert abs(p_estimate - expected_success) <= precision
    assert 0 <= confint[1] - confint[0] <= precision
    assert nobs3 > 0
    assert nobs3 > nobs1
