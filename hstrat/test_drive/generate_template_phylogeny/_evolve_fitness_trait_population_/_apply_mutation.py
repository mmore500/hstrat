import typing

import numpy as np


def _apply_mutation(
    pop_arr: np.ndarray,
    mut_distn: typing.Callable,
) -> None:
    """Apply mutation to all organisms' genetic trait, altering `pop_arr`
    inplace.
    """
    pop_arr += mut_distn(size=len(pop_arr))
