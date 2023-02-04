from ...._auxiliary_lib import jit


@jit(nopython=True)
def _get_niche_id(
    population_loc: int, island_niche_size: int, num_niches: int
) -> int:
    """Get population slot's niche ID."""
    # niches are contiguous and sequential within islands
    # if multiple islands are simulated, niches are fragmented in round robin
    # order across population
    return (population_loc // island_niche_size) % num_niches
