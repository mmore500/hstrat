from ...._auxiliary_lib import jit


@jit(nopython=True)
def _get_niche_id(
    population_loc: int, island_niche_size: int, num_niches: int
) -> int:
    return (population_loc // island_niche_size) % num_niches
