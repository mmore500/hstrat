import numpy as np

from hstrat._auxiliary_lib import cmp


def test_cmp_greater_than():
    assert cmp(2, 1) == 1


def test_cmp_less_than():
    assert cmp(1, 2) == -1


def test_cmp_equal():
    assert cmp(2, 2) == 0


def test_cmp_strings():
    assert cmp("a", "b") == -1


def test_cmp_lists():
    assert cmp([1, 2, 3], [1, 2, 4]) == -1


def test_cmp_greater_than_numpy():
    assert cmp(np.double(2), np.double(1)) == 1


def test_cmp_less_than_numpy():
    assert cmp(np.double(1), np.double(2)) == -1


def test_cmp_equal_numpy():
    assert cmp(np.double(2), np.double(2)) == 0
