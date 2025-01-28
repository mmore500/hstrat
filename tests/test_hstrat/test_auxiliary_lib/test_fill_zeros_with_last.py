import numpy as np

from hstrat._auxiliary_lib import fill_zeros_with_last


def test_fill_zeros_with_last_empty_array():
    arr = np.array([])
    expected = np.array([])
    result = fill_zeros_with_last(arr)
    assert np.array_equal(result, expected)


def test_fill_zeros_with_last_singleton_zero():
    arr = np.array([0])
    # No non-zero value exists to fill from, so the result remains zero.
    expected = np.array([0])
    result = fill_zeros_with_last(arr)
    assert np.array_equal(result, expected)


def test_fill_zeros_with_last_singleton_nonzero():
    arr = np.array([5])
    # No zeros to replace; the result should be the same.
    expected = np.array([5])
    result = fill_zeros_with_last(arr)
    assert np.array_equal(result, expected)


def test_fill_zeros_with_last_all_zeros():
    arr = np.array([0, 0, 0])
    # No non-zero values to fill from, so the result should stay all zeros.
    expected = np.array([0, 0, 0])
    result = fill_zeros_with_last(arr)
    assert np.array_equal(result, expected)


def test_fill_zeros_with_last_no_zeros():
    arr = np.array([1, 2, 3])
    expected = np.array([1, 2, 3])
    result = fill_zeros_with_last(arr)
    assert np.array_equal(result, expected)


def test_fill_zeros_with_last_mixed_zeros():
    arr = np.array([1, 0, 0, 2, 0])
    expected = np.array([1, 1, 1, 2, 2])
    result = fill_zeros_with_last(arr)
    assert np.array_equal(result, expected)


def test_fill_zeros_floating_point():
    arr = np.array([1, 0, 0, 2, 0], dtype=float)
    expected = np.array([1, 1, 1, 2, 2], dtype=float)
    result = fill_zeros_with_last(arr)
    assert np.array_equal(result, expected)
