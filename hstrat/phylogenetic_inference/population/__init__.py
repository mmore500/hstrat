"""Functions to infer phylogenetic history among a population of extant hstrat
columns."""

from ._does_definitively_share_no_common_ancestor import (
    does_definitively_share_no_common_ancestor,
)

__all__ = [
    "does_definitively_share_no_common_ancestor",
]

from ..._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
