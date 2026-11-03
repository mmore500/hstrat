import pandas as pd
import pytest

from hstrat._auxiliary_lib import get_sole_scalar_value_pandas


def test_get_sole_scalar_value_pandas_single_value():
    df = pd.DataFrame({"col": [42, 42, 42]})
    assert get_sole_scalar_value_pandas(df, "col") == 42


def test_get_sole_scalar_value_pandas_multiple_values():
    df = pd.DataFrame({"col": [42, 43]})
    with pytest.raises(ValueError):
        get_sole_scalar_value_pandas(df, "col")


def test_get_sole_scalar_value_pandas_empty():
    df = pd.DataFrame({"col": []})
    with pytest.raises(ValueError):
        get_sole_scalar_value_pandas(df, "col")
