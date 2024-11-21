import numpy as np

from ._jit import jit


@jit(nopython=True)
def is_subset(subset: np.ndarray, superset: np.ndarray) -> bool:
    """Are all values in `subset` contained in `superset`?"""
    superset_lookup = set(superset)
    for val in subset:
        if val not in superset_lookup:
            return False

    return True
