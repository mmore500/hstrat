import numpy as np

from hstrat._auxiliary_lib import iter_monotonic_equivalencies


def test_empty_arrays():
    first = np.array([])
    second = np.array([])
    res = [*iter_monotonic_equivalencies(first, second)]
    assert res == []
    for i, j in res:
        assert first[i] == second[j]


def test_one_element_arrays():
    first = np.array([1])
    second = np.array([1])
    res = [*iter_monotonic_equivalencies(first, second)]
    assert res == [(0, 0)]
    for i, j in res:
        assert first[i] == second[j]


def test_identical_arrays():
    first = np.array([1, 2, 3, 4, 5])
    second = np.array([1, 2, 3, 4, 5])
    res = [*iter_monotonic_equivalencies(first, second)]
    assert res == [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
    for i, j in res:
        assert first[i] == second[j]


def test_non_overlapping_arrays():
    first = np.array([1, 3, 5, 7, 9])
    second = np.array([2, 4, 6, 8, 10])
    res = [*iter_monotonic_equivalencies(first, second)]
    assert res == []
    for i, j in res:
        assert first[i] == second[j]


def test_some_overlapping_arrays():
    first = np.array([1, 2, 3, 4, 5])
    second = np.array([2, 4, 6, 8, 10])
    res = [*iter_monotonic_equivalencies(first, second)]
    assert res == [(1, 0), (3, 1)]
    for i, j in res:
        assert first[i] == second[j]


def test_non_decreasing_arrays():
    first = np.array([1, 2, 3, 3, 3, 4, 5, 7])
    second = np.array([2, 3, 3, 4, 4, 4, 6, 7])
    res = [*iter_monotonic_equivalencies(first, second)]
    assert res == [(1, 0), (2, 1), (3, 2), (5, 3), (7, 7)]
    for i, j in res:
        assert first[i] == second[j]


def test_start_parameter1():
    first = np.array([1, 2, 3, 4, 5])
    second = np.array([2, 4, 6, 8, 10])
    res = [*iter_monotonic_equivalencies(first, second, start=(1, 0))]
    assert res == [(1, 0), (3, 1)]
    for i, j in res:
        assert first[i] == second[j]


def test_start_parameter2():
    first = np.array([1, 2, 3, 4, 5])
    second = np.array([2, 4, 6, 8, 10])
    res = [*iter_monotonic_equivalencies(first, second, start=(2, 0))]
    assert res == [(3, 1)]
    for i, j in res:
        assert first[i] == second[j]
