import numpy as np

from hstrat._auxiliary_lib import iter_monotonic_equivalencies_reverse


def test_empty_arrays():
    first = np.array([])
    second = np.array([])
    res = [*iter_monotonic_equivalencies_reverse(first, second)]
    assert res == [*reversed([])]
    for i, j in res:
        assert first[i] == second[j]


def test_one_element_arrays():
    first = np.array([1])
    second = np.array([1])
    res = [*iter_monotonic_equivalencies_reverse(first, second)]
    assert res == [*reversed([(0, 0)])]
    for i, j in res:
        assert first[i] == second[j]


def test_identical_arrays():
    first = np.array([1, 2, 3, 4, 5])
    second = np.array([1, 2, 3, 4, 5])
    res = [*iter_monotonic_equivalencies_reverse(first, second)]
    assert res == [*reversed([(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)])]
    for i, j in res:
        assert first[i] == second[j]


def test_non_overlapping_arrays():
    first = np.array([1, 3, 5, 7, 9])
    second = np.array([2, 4, 6, 8, 10])
    res = [*iter_monotonic_equivalencies_reverse(first, second)]
    assert res == [*reversed([])]
    for i, j in res:
        assert first[i] == second[j]


def test_some_overlapping_arrays():
    first = np.array([1, 2, 3, 4, 5])
    second = np.array([2, 4, 6, 8, 10])
    res = [*iter_monotonic_equivalencies_reverse(first, second)]
    assert res == [*reversed([(1, 0), (3, 1)])]
    for i, j in res:
        assert first[i] == second[j]


def test_non_decreasing_arrays():
    first = np.array([1, 2, 3, 3, 3, 4, 5, 7])
    second = np.array([2, 3, 3, 4, 4, 4, 6, 7])
    res = [*iter_monotonic_equivalencies_reverse(first, second)]
    assert res == [*reversed([(1, 0), (3, 1), (4, 2), (5, 5), (7, 7)])]
    for i, j in res:
        assert first[i] == second[j]


def test_start_parameter1():
    first = np.array([1, 2, 3, 4, 5])
    second = np.array([2, 4, 6, 8, 10])
    res = [*iter_monotonic_equivalencies_reverse(first, second, start=(1, 0))]
    assert res == [*reversed([(1, 0)])]
    for i, j in res:
        assert first[i] == second[j]


def test_start_parameter2():
    first = np.array([1, 2, 3, 4, 5])
    second = np.array([2, 4, 6, 8, 10])
    res = [*iter_monotonic_equivalencies_reverse(first, second, start=(0, 0))]
    assert res == [*reversed([])]
    for i, j in res:
        assert first[i] == second[j]


def test_start_parameter3():
    first = np.array([1, 2, 3, 4, 5])
    second = np.array([2, 4, 6, 8, 10])
    res = [
        *iter_monotonic_equivalencies_reverse(first, second, start=(-3, -1))
    ]
    assert res == [*reversed([(1, 0)])]
    for i, j in res:
        assert first[i] == second[j]
