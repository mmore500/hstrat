import itertools as it
import typing

import opytional as opyt
import pandas as pd

from ..._auxiliary_lib import pairwise
from ._PerfectBacktrackHandle import PerfectBacktrackHandle
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

    seen_handle_ids = set()

    records = list()
    for extant_handle in population:
        for descendant_handle, ancestor_handle in pairwise(
            it.chain(
                iter_perfect_backtrack_lineage(extant_handle),
                (None,),
            )
        ):
            assert descendant_handle is not None
            if id(descendant_handle) not in seen_handle_ids:
                seen_handle_ids.add(id(descendant_handle))
                records.append(
                    {
                        **{
                            "id": id(descendant_handle),
                            "ancestor_list": str(
                                [opyt.apply_if(ancestor_handle, id)]
                            ),
                        },
                        **(
                            descendant_handle.data
                            if isinstance(descendant_handle.data, dict)
                            else {"data": descendant_handle.data}
                            if descendant_handle.data is not None
                            else {}
                        ),
                    }
                )

    return pd.DataFrame.from_dict(records)
