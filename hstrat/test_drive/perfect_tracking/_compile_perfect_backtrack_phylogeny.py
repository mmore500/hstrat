import typing

import pandas as pd

from ._PerfectBacktrackHandle import PerfectBacktrackHandle
from ._compile_phylogeny_from_lineage_iters import (
    compile_phylogeny_from_lineage_iters,
)
from ._iter_perfect_backtrack_lineage import iter_perfect_backtrack_lineage


def compile_perfect_backtrack_phylogeny(
    population: typing.Iterable[PerfectBacktrackHandle],
) -> pd.DataFrame:
    """Compile phylogenetic history tracked using `PerfectBacktrackHandle`
    breadcrumbs.

    Parameters
    ----------
    population : iterable of `PerfectBactrackHandle`
        PerfectBacktrackHandle objects associated with extant population
        members.

    Returns
    -------
    pd.DataFrame
        Phylogenetic record in alife data standards format.
    """

    return compile_phylogeny_from_lineage_iters(
        iter_perfect_backtrack_lineage(extant_handle)
        for extant_handle in population
    )
