"""Tools to generate example phylogenies."""

from ._evolve_fitness_trait_population import evolve_fitness_trait_population

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "evolve_fitness_trait_population",
]

from ..._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
