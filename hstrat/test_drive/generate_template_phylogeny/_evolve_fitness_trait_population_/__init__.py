"""Implementation for `evolve_fitness_trait_population`."""

from ._apply_island_migrations import _apply_island_migrations
from ._apply_mutation import _apply_mutation
from ._apply_niche_invasions import _apply_niche_invasions
from ._get_island_id import _get_island_id
from ._get_niche_id import _get_niche_id
from ._select_parents import _select_parents

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "_apply_island_migrations",
    "_apply_mutation",
    "_apply_niche_invasions",
    "_get_island_id",
    "_get_niche_id",
    "_select_parents",
]
