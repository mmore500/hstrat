import numpy as np


def find_first_between_sorted_rows(
    rows: np.ndarray,
    after: np.ndarray,
    before: np.ndarray,
    num: int,
) -> np.ndarray:
    """Find the first `num` values of each ascending-sorted row of `rows`
    that lie strictly between that row's bounds, padding with inf where
    fewer exist.

    Parameters
    ----------
    rows : np.ndarray
        2D array, with each row sorted ascending.
    after : np.ndarray
        Exclusive lower bound values for each row.
    before : np.ndarray
        Exclusive upper bound values for each row.
    num : int
        Number of values to find per row.

    Returns
    -------
    np.ndarray
        The found values (not indices), as an array of shape
        `(len(rows), num)`, in ascending order within each row.
    """
    # index of first value after `after`, as rows are sorted ascending
    columns = (rows <= after[:, None]).sum(axis=1)[:, None] + np.arange(num)
    in_bounds = columns < rows.shape[1]
    result = np.take_along_axis(
        rows, np.minimum(columns, rows.shape[1] - 1), axis=1
    )
    return np.where(in_bounds & (result < before[:, None]), result, np.inf)
