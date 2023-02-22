import numpy as np

from hstrat._auxiliary_lib import numpy_fromiter_polyfill


def test_numpy_fromiter_polyfill_int32():
    iterable = [1, 2, 3, 4, 5]
    dtype = np.int32
    expected = np.array(iterable, dtype=dtype)
    result = numpy_fromiter_polyfill(iterable, dtype=dtype)
    assert np.array_equal(expected, result)


def test_numpy_fromiter_polyfill_int32_iterator():
    iterable = [1, 2, 3, 4, 5]
    dtype = np.int32
    expected = np.array(iterable, dtype=dtype)
    result = numpy_fromiter_polyfill(iter(iterable), dtype=dtype)
    assert np.array_equal(expected, result)


def test_numpy_fromiter_polyfill_float64():
    iterable = [1.0, 2.0, 3.0, 4.0, 5.0]
    dtype = np.float64
    expected = np.array(iterable, dtype=dtype)
    result = numpy_fromiter_polyfill(iterable, dtype=dtype)
    assert np.array_equal(expected, result)


def test_numpy_fromiter_polyfill_string():
    iterable = ["a", "b", "c", "d", "e"]
    dtype = np.object_
    expected = np.array(iterable, dtype=dtype)
    result = numpy_fromiter_polyfill(iterable, dtype=dtype)
    assert np.array_equal(expected, result)


def test_numpy_fromiter_polyfill_object():
    iterable = [None, "a", None, "b", "c", None, "d", "e", None]
    dtype = np.object_
    expected = np.array(iterable, dtype=dtype)
    result = numpy_fromiter_polyfill(iterable, dtype=dtype)
    assert np.array_equal(expected, result)


def test_numpy_fromiter_polyfill_object_iterator():
    iterable = [None, "a", None, "b", "c", None, "d", "e", None]
    dtype = np.object_
    expected = np.array(iterable, dtype=dtype)
    result = numpy_fromiter_polyfill(iter(iterable), dtype=dtype)
    assert np.array_equal(expected, result)


def test_numpy_fromiter_polyfill_object_empty():
    iterable = []
    dtype = np.object_
    expected = np.array(iterable, dtype=dtype)
    result = numpy_fromiter_polyfill(iter(iterable), dtype=dtype)
    assert np.array_equal(expected, result)
