from ...._auxiliary_lib import jit


@jit(nopython=True)
def _get_island_id(
    population_idx: int,
    island_size: int,
) -> int:
    return population_idx // island_size
