import numpy as np

from hstrat._auxiliary_lib import cmp_approx


def test_cmp_approx_returns_0_for_close_values():
    assert cmp_approx(1.0, 1.0000000001) == 0
    assert cmp_approx(1.0000000001, 1.0) == 0


def test_cmp_approx_returns_1_for_a_greater_than_b():
    assert cmp_approx(2.0, 1.0) == 1


def test_cmp_approx_returns_minus_1_for_a_less_than_b():
    assert cmp_approx(1.0, 2.0) == -1


def test_cmp_approx_returns_0_for_equal_values():
    assert cmp_approx(2.0, 2.0) == 0


def test_cmp_approx_returns_0_for_close_values_numpy():
    assert cmp_approx(np.double(1.0), np.double(1.0000000001)) == 0
    assert cmp_approx(np.double(1.0000000001), np.double(1.0)) == 0


def test_cmp_approx_returns_1_for_a_greater_than_b_numpy():
    assert cmp_approx(np.double(2.0), np.double(1.0)) == 1


def test_cmp_approx_returns_minus_1_for_a_less_than_b_numpy():
    assert cmp_approx(np.double(1.0), np.double(2.0)) == -1


def test_cmp_approx_returns_0_for_equal_values_numpy():
    assert cmp_approx(np.double(2.0), np.double(2.0)) == 0
