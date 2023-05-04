import typing

import numpy as np


def to_tril(matrix: np.ndarray) -> typing.List[typing.List[float]]:
    """Convert a distance matrix to the lower triangular form representation
    required by BioPython.

    Excludes upper triangular entries (i.e., returned list of lists is ragged).
    Sets all diagonal elements to zero.

    Parameters
    ----------
    matrix : np.ndarray
        The input matrix, represented as a 2-dimensional numpy array.

    Returns
    -------
    typing.List[typing.List[float]]
        The lower triangular form of the input matrix, represented as a list of
        lists of floats.

    Examples
    --------
    >>> import numpy as np
    >>> matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    >>> to_tril(matrix)
    [[0.0], [4, 0.0, 0], [7, 8, 0.0]]
    """
    return [
        row[:row_idx] + [0.0] for row_idx, row in enumerate(matrix.tolist())
    ]
