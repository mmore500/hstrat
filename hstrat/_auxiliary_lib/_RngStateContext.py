import random
from typing import Any

import numpy as np

from ._jit import jit


@jit(nopython=True)
def _seed_jitted(seed: int) -> bool:
    """Seed numba-internal random state.

    Implementation detail. Numba maintains its own PRNG state separate
    from Python's random and NumPy's random, so it must be seeded
    independently from within a jitted function.
    """
    np.random.seed(seed)
    random.seed(seed)
    return True


class RngStateContext:
    """A context manager that temporarily reseeds the `random` module random
    number generator (RNG) and restores the original RNG state upon exiting the
    scope.
    """

    def __init__(self, seed: int):
        """Constructs an RngStateContext with the specified seed value.

        Parameters:
        -----------
        seed: int
            The seed value to use for reseeding the RNG temporarily.
        """
        self.seed = seed

    def __enter__(self) -> None:
        """Enters the context manager and saves the current state of the RNG to
        _saved_state, then reseeds the RNG with the specified seed value."""
        self._saved_state = random.getstate()
        self._saved_np_state = np.random.get_state()
        random.seed(self.seed)
        _seed_jitted(self.seed)

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Exits the context manager and restores the RNG state to the value
        saved in _saved_state."""
        random.setstate(self._saved_state)
        np.random.set_state(self._saved_np_state)
