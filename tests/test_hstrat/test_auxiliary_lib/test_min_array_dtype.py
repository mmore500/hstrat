import numpy as np

from hstrat._auxiliary_lib import min_array_dtype


def test_single_value():
    arr = np.array([5])
    expected_dtype = np.dtype("uint8")
    assert min_array_dtype(arr) == expected_dtype
    assert (arr.astype(expected_dtype) == arr).all()


def test_single_value_negative():
    arr = np.array([-5])
    expected_dtype = np.dtype("int8")
    assert min_array_dtype(arr) == expected_dtype
    assert (arr.astype(expected_dtype) == arr).all()


def test_positive_values():
    arr = np.array([5, 10, 100])
    expected_dtype = np.dtype("uint8")
    assert min_array_dtype(arr) == expected_dtype
    assert (arr.astype(expected_dtype) == arr).all()


def test_mixed_values1():
    arr = np.array([-5, 0, 10])
    expected_dtype = np.dtype("int8")
    assert min_array_dtype(arr) == expected_dtype
    assert (arr.astype(expected_dtype) == arr).all()


def test_mixed_values2():
    arr = np.array([5, 0, -255])
    expected_dtype = np.dtype("int16")
    assert min_array_dtype(arr) == expected_dtype
    assert (arr.astype(expected_dtype) == arr).all()


def test_large_values():
    arr = np.array([10000, 100000, 1000000])
    expected_dtype = np.dtype("uint32")
    assert min_array_dtype(arr) == expected_dtype
    assert (arr.astype(expected_dtype) == arr).all()


def test_large_mixed_values():
    arr = np.array([-10000, 100000, 1000000])
    expected_dtype = np.dtype("int32")
    assert min_array_dtype(arr) == expected_dtype
    assert (arr.astype(expected_dtype) == arr).all()


def test_float_values():
    arr = np.array([-0.5, 1.0, 1.5])
    expected_dtype = np.dtype("float16")
    assert min_array_dtype(arr) == expected_dtype
    assert (arr.astype(expected_dtype) == arr).all()


def test_large_float_values():
    arr = np.array([0.5, 1.0e100, 1.5])
    expected_dtype = np.dtype("float64")
    assert min_array_dtype(arr) == expected_dtype
    assert (arr.astype(expected_dtype) == arr).all()


def test_complex_values():
    arr = np.array([1 + 2j, 3 + 4j, 5 + 6j])
    expected_dtype = np.dtype("complex64")
    assert min_array_dtype(arr) == expected_dtype
    assert (arr.astype(expected_dtype) == arr).all()


def test_empty_array():
    arr = np.array([])
    expected_dtype = np.dtype("uint8")
    assert min_array_dtype(arr) == expected_dtype
    assert (arr.astype(expected_dtype) == arr).all()
