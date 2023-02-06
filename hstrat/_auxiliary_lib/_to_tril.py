import typing

import numpy as np


def to_tril(matrix: np.ndarray) -> typing.List[typing.List[float]]:
    return [
        row[:row_idx] + [0.0] for row_idx, row in enumerate(matrix.tolist())
    ]
