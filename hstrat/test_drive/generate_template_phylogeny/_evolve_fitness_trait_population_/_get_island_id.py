from ...._auxiliary_lib import jit


@jit(nopython=True)
def _get_island_id(
    population_loc: int,
    island_size: int,
) -> int:
    return population_loc // island_size
