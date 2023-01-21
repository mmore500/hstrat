from ...._auxiliary_lib import jit_if_has_numba


@jit_if_has_numba(nopython=True)
def _get_niche_id(
    population_idx: int, island_niche_size: int, num_niches: int
) -> int:
    return (population_idx // island_niche_size) % num_niches
