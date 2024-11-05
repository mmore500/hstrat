"""Tools to infer phylogenetic history from extant genome annotations."""

from . import estimators, pairwise, population, priors, tree
from .._auxiliary_lib import lazy_attach

__getattr__, __dir__, __all__ = lazy_attach(
    __name__,
    submodules=["estimators", "pairwise", "population", "priors", "tree"],
    submod_attrs={
        "estimators": estimators.__all__,
        "pairwise": pairwise.__all__,
        "population": population.__all__,
        "priors": priors.__all__,
        "tree": tree.__all__,
    },
    should_launder=[].__contains__,
)
