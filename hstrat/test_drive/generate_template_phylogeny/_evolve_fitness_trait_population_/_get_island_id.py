from ...._auxiliary_lib import jit


@jit(nopython=True)
def _get_island_id(
    population_loc: int,
    island_size: int,
) -> int:
    """Get population slot's island ID."""
    # islands are contiguous and sequential within population
    return population_loc // island_size
