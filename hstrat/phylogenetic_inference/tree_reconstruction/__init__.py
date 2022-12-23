"""Functions to reconstruct a phylogenetic tree from extant hereditary strata."""

__all__ = []

from itertools import combinations
from typing import Iterable

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from ..._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
