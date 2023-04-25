import random

import numpy as np


def seed_random(seed: int) -> bool:
    """Seed all random sources used by hstrat library.

    Ensures reproducible execution.
    """
    random.seed(seed)
    np.random.seed(seed)
