"""Tools for perfect phylogenetic tracking."""

from ._DecantingPhyloTracker import DecantingPhyloTracker
from ._GarbageCollectingPhyloTracker import GarbageCollectingPhyloTracker
from ._PerfectBacktrackHandle import PerfectBacktrackHandle
from ._compile_perfect_backtrack_phylogeny import (
    compile_perfect_backtrack_phylogeny,
)
from ._compile_phylogeny_from_lineage_iters import (
    compile_phylogeny_from_lineage_iters,
)
from ._iter_perfect_backtrack_lineage import iter_perfect_backtrack_lineage

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "compile_perfect_backtrack_phylogeny",
    "compile_phylogeny_from_lineage_iters",
    "DecantingPhyloTracker",
    "GarbageCollectingPhyloTracker",
    "iter_perfect_backtrack_lineage",
    "PerfectBacktrackHandle",
]

from ..._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
