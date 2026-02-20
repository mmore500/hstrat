import random

import numpy as np
import polars as pl

from ._jit import jit


@jit(nopython=True)
def _seed_random_jitted(seed: int) -> bool:
    """Seed numba-internal random state.

    Implementation detail. Numba maintains its own PRNG state separate
    from Python's random and NumPy's random, so it must be seeded
    independently from within a jitted function.
    """
    np.random.seed(seed)
    random.seed(seed)
    return True


def seed_random(seed: int) -> bool:
    """Seed all random sources used by hstrat library.

    Ensures reproducible execution.
    """
    random.seed(seed)
    np.random.seed(seed)
    pl.set_random_seed(seed)
    _seed_random_jitted(seed)
