import itertools as it
import typing

import opytional as opyt
import pandas as pd

from ..._auxiliary_lib import demark


def compile_phylogeny_from_lineage_iters(
    population: typing.Iterable[typing.Iterable[typing.Any]],
) -> pd.DataFrame:
    """Compile phylogenetic history tracked using generic backtracking breadcrumbs.

    Parameters
    ----------
    population : iterable of iterable
        Ascending lineage iterators associated with extant population members.

    Returns
    -------
    pd.DataFrame
        Phylogenetic record in alife data standards format.
    """

    seen_handle_ids = set()

    records = list()
    for lineage_it1, lineage_it2 in map(it.tee, population):
        for descendant_handle, ancestor_handle in it.zip_longest(
            lineage_it1,
            it.islice(lineage_it2, 1, None),
        ):
            assert descendant_handle is not None
            if demark(descendant_handle) not in seen_handle_ids:
                seen_handle_ids.add(demark(descendant_handle))
                records.append(
                    {
                        **{
                            "id": demark(descendant_handle),
                            "ancestor_list": str(
                                [opyt.apply_if(ancestor_handle, demark)]
                            ),
                        },
                        **(
                            {}
                            if not hasattr(descendant_handle, "data")
                            else descendant_handle.data
                            if isinstance(descendant_handle.data, dict)
                            else {"data": descendant_handle.data}
                            if descendant_handle.data is not None
                            else {}
                        ),
                    }
                )

    return pd.DataFrame.from_dict(records)
