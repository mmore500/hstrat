import typing

import numpy as np


def apply_unique_rows(
    func: typing.Callable[..., typing.Tuple[float, ...]],
    *columns: np.ndarray,
) -> typing.Tuple[np.ndarray, ...]:
    """Apply scalar-valued `func` row-wise over `columns`, calling it only
    once for each unique row.

    Useful to vectorize expensive pure Python functions over arrays with
    many repeated rows.

    Parameters
    ----------
    func : Callable
        Takes one int argument per column, returning a tuple of floats.
    *columns : np.ndarray
        Equal-length integer arrays, one per argument to `func`.

    Returns
    -------
    tuple of np.ndarray
        One float64 array per element of `func`'s return tuple.
    """
    num_rows = len(columns[0]) if columns else 0
    stacked = np.stack(columns, axis=1).reshape(num_rows, len(columns))
    uniques, inverse = np.unique(stacked, axis=0, return_inverse=True)
    results = np.array(
        [func(*map(int, row)) for row in uniques], dtype=np.float64
    )
    if len(uniques) == 0:
        # can't determine number of outputs without calling func
        return tuple()
    results = results.reshape(len(uniques), -1)
    inverse = inverse.ravel()
    return tuple(results[inverse, i] for i in range(results.shape[1]))
