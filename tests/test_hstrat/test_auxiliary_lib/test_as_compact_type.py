import numpy as np

from hstrat._auxiliary_lib import as_compact_type


def test_as_compact_type_empty():
    arr = np.array([])
    assert np.array_equal(
        as_compact_type(arr), np.array([], dtype=np.dtype("int64"))
    )


def test_as_compact_type_int8():
    arr = np.array([1, 2, 3, 4, 5])
    assert np.array_equal(
        as_compact_type(arr), np.array([1, 2, 3, 4, 5], dtype=np.dtype("int8"))
    )


def test_as_compact_type_uint8():
    arr = np.array([255, 0, 1])
    assert np.array_equal(
        as_compact_type(arr), np.array([255, 0, 1], dtype=np.dtype("uint8"))
    )


def test_as_compact_type_int16():
    arr = np.array([-128, 0, 127])
    assert np.array_equal(
        as_compact_type(arr), np.array([-128, 0, 127], dtype=np.dtype("int8"))
    )


def test_as_compact_type_uint16():
    arr = np.array([-32768, 0, 32767])
    assert np.array_equal(
        as_compact_type(arr),
        np.array([-32768, 0, 32767], dtype=np.dtype("int16")),
    )


def test_as_compact_type_float16():
    arr = np.array([-0.5, 0, 0.5])
    assert np.array_equal(
        as_compact_type(arr),
        np.array([-0.5, 0, 0.5], dtype=np.dtype("float16")),
    )

    arr = np.array([1e-6])
    assert np.array_equal(
        as_compact_type(arr), np.array([1e-6], dtype=np.dtype("float16"))
    )

    arr = np.array([1e-20])
    assert np.array_equal(
        as_compact_type(arr), np.array([1e-20], dtype=np.dtype("float16"))
    )


def test_as_compact_type_float32():
    arr = np.array([-1e-8, 0, 1e8])
    assert np.array_equal(
        as_compact_type(arr),
        np.array([-1e-8, 0, 1e8], dtype=np.dtype("float32")),
    )


def test_as_compact_type_float64():
    arr = np.array([1e200])
    assert np.array_equal(
        as_compact_type(arr), np.array([1e200], dtype=np.dtype("float64"))
    )

    arr = np.array([1e-200, 1, 1e200])
    assert np.array_equal(
        as_compact_type(arr),
        np.array([1e-200, 1, 1e200], dtype=np.dtype("float64")),
    )
