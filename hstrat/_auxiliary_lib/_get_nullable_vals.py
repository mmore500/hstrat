import numpy as np
import pandas as pd


def get_nullable_vals(series: pd.Series) -> np.ndarray:
    """Get the integer underlying values in a Pandas Series with nullable
    integer dtype.

    Parameters
    ----------
    series : pd.Series
        The Pandas Series to get the null values for.

    Returns
    -------
    np.ndarray
        A 1-dimensional NumPy ndarray of the same dtype as the input series.
        The i-th element of the array is the underlying value at the i-th
        position in the input series.

    Notes
    -----
    This function returns a direct view into the Series data, so no copy is
    made. Changes to the returned array will propagate to the Series object's
    underlying values, and vice versa.
    """
    return series._data.array._data
