import numpy as np
import pandas as pd


def get_nullable_mask(series: pd.Series) -> np.ndarray:
    """Get a boolean mask indicating which elements in a Pandas Series with
    nullable integer dtype are null.

    Parameters
    ----------
    series : pd.Series
        The Pandas Series to get the null mask for.

    Returns
    -------
    np.ndarray
        A 1-dimensional NumPy ndarray of boolean values. The i-th element of the
        array is True if the i-th element of the input series is null, and False
        otherwise.

    Notes
    -----
    This function returns the underlying boolean mask used by the Pandas Series
    object to represent null values. This mask is a direct view into the Series
    data, so no copy is made. Changes to the mask will propagate to the Series
    object, and vice versa.
    """
    return series._data.array._mask
