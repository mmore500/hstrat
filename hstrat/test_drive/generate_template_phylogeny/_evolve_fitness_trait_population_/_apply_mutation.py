import numpy as np


def _apply_mutation(
    pop_arr: np.array,
) -> None:
    pop_arr += np.random.standard_normal(size=len(pop_arr))
