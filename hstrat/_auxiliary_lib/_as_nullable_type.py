import pandas as pd

from ._capitalize_n import capitalize_n


def as_nullable_type(series: pd.Series) -> pd.Series:
    """Convert the input Series to ensure a nullable dtype.

    If the Series' type is already nullable, it will be returned unchanged.

    Parameters
    ----------
    series : pandas.Series
        Input Series to be converted to a nullable data type.

    Returns
    -------
    pandas.Series
        A new Pandas Series object with a nullable dtype, converted from the input Series.

    Notes
    -----
    See <https://pandas.pydata.org/pandas-docs/version/1.5/user_guide/integer_na.html>
    and <https://pandas.pydata.org/pandas-docs/version/1.5/user_guide/boolean.html> for information on nullable integer and boolean types.

    Examples
    --------
    >>> import pandas as pd
    >>> from typing import Any
    >>> from ._capitalize_n import capitalize_n

    >>> data = {'A': [1, 2, 3], 'B': [True, False, True]}
    >>> df = pd.DataFrame(data)
    >>> nullable_df = df.apply(as_nullable_type)
    >>> nullable_df.dtypes
    A          Int64
    B    BooleanDtype
    dtype: object
    """
    if pd.api.types.is_bool_dtype(series.dtype):
        return series.astype("boolean")
    elif pd.api.types.is_unsigned_integer_dtype(series.dtype):
        return series.astype(capitalize_n(series.dtype.name, 2))
    elif pd.api.types.is_signed_integer_dtype(series.dtype):
        return series.astype(series.dtype.name.capitalize())
    else:
        return series
