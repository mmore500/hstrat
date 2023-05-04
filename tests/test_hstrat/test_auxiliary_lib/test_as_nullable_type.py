import numpy as np
import pandas as pd

from hstrat._auxiliary_lib import as_nullable_type


def test_as_nullable_type_integer():
    s_int = pd.Series([1, 2, 3, 4], dtype="int16")
    s_int_nullable = as_nullable_type(s_int)
    print(s_int_nullable)
    assert s_int_nullable.dtype == "Int16"
    assert all(s_int_nullable == s_int)


def test_as_nullable_type_unsigned_integer():
    s_int = pd.Series([1, 2, 3, 4], dtype="uint8")
    s_int_nullable = as_nullable_type(s_int)
    print(s_int_nullable)
    assert s_int_nullable.dtype == "UInt8"
    assert all(s_int_nullable == s_int)


def test_as_nullable_type_Integer():
    s_int = pd.Series([1, 2, 3, 4, pd.NA], dtype="Int64")
    s_int_nullable = as_nullable_type(s_int)
    print(s_int_nullable)
    assert s_int_nullable.dtype == "Int64"
    pd.testing.assert_series_equal(s_int_nullable, s_int)


def test_as_nullable_type_float():
    s_float = pd.Series([1.0, 2.0, 3.0, np.nan, 4.0])
    s_float_nullable = as_nullable_type(s_float)
    assert s_float_nullable.dtype == "float64"
    pd.testing.assert_series_equal(s_float_nullable, s_float)


def test_as_nullable_type_bool():
    s_bool = pd.Series([True, False, True])
    s_bool_nullable = as_nullable_type(s_bool)
    assert s_bool_nullable.dtype == "boolean"
    assert all(s_bool_nullable == s_bool)


def test_as_nullable_type_boolean():
    s_bool = pd.Series([True, False, True], dtype="boolean")
    s_bool_nullable = as_nullable_type(s_bool)
    assert s_bool_nullable.dtype == "boolean"
    pd.testing.assert_series_equal(s_bool_nullable, s_bool)


def test_as_nullable_type_mixed_type():
    s_mixed = pd.Series([1, "foo", True])
    s_mixed_nullable = as_nullable_type(s_mixed)
    assert s_mixed_nullable.dtype == "object"
    pd.testing.assert_series_equal(s_mixed_nullable, s_mixed)
