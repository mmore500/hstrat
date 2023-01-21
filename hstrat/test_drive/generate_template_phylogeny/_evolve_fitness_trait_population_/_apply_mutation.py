import typing

import numpy as np


def _apply_mutation(
    pop_arr: np.array,
    mut_distn: typing.Callable,
) -> None:
    pop_arr += mut_distn(size=len(pop_arr))
