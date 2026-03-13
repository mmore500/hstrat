import random
from typing import Any

import numpy as np

from ._seed_random import _seed_random_jitted


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
        _seed_random_jitted(self.seed)

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Exits the context manager and restores the RNG state to the value
        saved in _saved_state."""
        random.setstate(self._saved_state)
        np.random.set_state(self._saved_np_state)
        # Reseed jitted PRNG deterministically from the restored state.
        # Draw seed without consuming from the restored state, and
        # restore both states after _seed_random_jitted (which may
        # mutate Python-level state when the jit shim is active).
        jitted_reseed = random.randint(0, 2**32 - 1)
        _seed_random_jitted(jitted_reseed)
        random.setstate(self._saved_state)
        np.random.set_state(self._saved_np_state)
