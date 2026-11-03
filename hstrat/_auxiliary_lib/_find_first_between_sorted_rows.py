import numpy as np


def find_first_between_sorted_rows(
    rows: np.ndarray,
    after: np.ndarray,
    before: np.ndarray,
    num: int,
) -> np.ndarray:
    """First `num` values of each ascending-sorted row of `rows` strictly
    between that row's `after` and `before` (inf where fewer)."""
    # index of first value after `after`, as rows are sorted ascending
    columns = (rows <= after[:, None]).sum(axis=1)[:, None] + np.arange(num)
    in_bounds = columns < rows.shape[1]
    result = np.take_along_axis(
        rows, np.minimum(columns, rows.shape[1] - 1), axis=1
    )
    return np.where(in_bounds & (result < before[:, None]), result, np.inf)
