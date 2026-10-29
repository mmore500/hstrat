import numpy as np

from hstrat._auxiliary_lib import apply_unique_rows


def test_apply_unique_rows():
    calls = []

    def func(a: int, b: int):
        calls.append((a, b))
        return a + b, a * b

    sums, prods = apply_unique_rows(
        func, np.array([1, 1, 2, 1]), np.array([3, 3, 4, 5])
    )
    np.testing.assert_array_equal(sums, [4, 4, 6, 6])
    np.testing.assert_array_equal(prods, [3, 3, 8, 5])
    assert sorted(calls) == [(1, 3), (1, 5), (2, 4)]


def test_apply_unique_rows_single_column():
    (res,) = apply_unique_rows(lambda a: (a * 2,), np.array([3, 1, 3]))
    np.testing.assert_array_equal(res, [6, 2, 6])


def test_apply_unique_rows_empty():
    res = apply_unique_rows(lambda a: (a,), np.array([], dtype=int))
    assert res == tuple()
