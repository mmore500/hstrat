import numpy as np
import pandas as pd
import pytest

from hstrat._auxiliary_lib import get_nullable_mask


@pytest.mark.parametrize("dtype_base", ["UInt{}", "Int{}"])
@pytest.mark.parametrize("dtype_bits", [8, 16, 32, 64])
def test_get_nullable_mask(dtype_base, dtype_bits):
    series = pd.Series([3, 2, pd.NA], dtype=dtype_base.format(dtype_bits))
    assert np.array_equal(get_nullable_mask(series), series.isna())
    get_nullable_mask(series)[0] = True
    assert np.array_equal(series.isna(), np.array([True, False, True]))
    get_nullable_mask(series)[2] = False
    assert np.array_equal(series.isna(), np.array([True, False, False]))
