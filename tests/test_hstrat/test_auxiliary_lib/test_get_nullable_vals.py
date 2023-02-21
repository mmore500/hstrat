import numpy as np
import pandas as pd
import pytest

from hstrat._auxiliary_lib import get_nullable_mask, get_nullable_vals


@pytest.mark.parametrize("dtype_base", ["UInt{}", "Int{}"])
@pytest.mark.parametrize("dtype_bits", [8, 16, 32, 64])
def test_get_nullable_vals(dtype_base, dtype_bits):
    series = pd.Series([3, 1, 2], dtype=dtype_base.format(dtype_bits))
    assert np.array_equal(get_nullable_vals(series), series)
    get_nullable_vals(series)[0] = 42
    assert np.array_equal(get_nullable_vals(series), np.array([42, 1, 2]))
    get_nullable_mask(series)[2] = False
    assert get_nullable_vals(series)[2] == 2
