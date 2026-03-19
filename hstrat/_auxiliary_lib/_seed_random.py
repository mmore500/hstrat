import random

import numpy as np
import polars as pl


def seed_random(seed: int) -> bool:
    """Seed all random sources used by hstrat library.

    Ensures reproducible execution.
    """
    random.seed(seed)
    np.random.seed(seed)
    pl.set_random_seed(seed)
