from ...._auxiliary_lib import jit_if_has_numba


@jit_if_has_numba(nopython=True)
def _get_island_id(
    population_idx: int,
    island_size: int,
) -> int:
    return population_idx // island_size
