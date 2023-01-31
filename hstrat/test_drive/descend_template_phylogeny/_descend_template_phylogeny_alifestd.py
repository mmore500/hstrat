from collections import abc
import typing

import numpy as np
import pandas as pd

from ..._auxiliary_lib._alifestd_assign_contiguous_ids import _reassign_ids
from ..._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_has_contiguous_ids,
    alifestd_has_multiple_roots,
    alifestd_is_topologically_sorted,
    alifestd_topological_sort,
    alifestd_to_working_format,
)
from ...genome_instrumentation import HereditaryStratigraphicColumn
from ._descend_template_phylogeny import descend_template_phylogeny


def descend_template_phylogeny_alifestd(
    phylogeny_df: pd.DataFrame,
    seed_column: HereditaryStratigraphicColumn,
    extant_ids: typing.Optional[typing.Iterable[int]] = None,
) -> typing.List[HereditaryStratigraphicColumn]:
    """Generate a population of hereditary stratigraphic columns that could
    have resulted from the template phylogeny.

    Parameters
    ----------
    phylogeny_df : pandas.DataFrame
        Phylogeny record as an alife-standard DataFrame.
    seed_column : HereditaryStratigraphicColumn
        Hereditary stratigraphic column to seed at root node of phylogeny.

        Returned hereditary stratigraphic column population will be generated
        as if repeatedly calling `CloneDescendant()` on `seed_column`. As such,
        specifies configuration (i.e., differentia bit width and stratum
        retention policy) for returned columns. May already have strata
        deposited, which will be incorporated into generated extant population.
    extant_ids : optional list of int
        Which organisms should hereditary stratigraphic columns be created for?

        Designates content and order of returned list of hereditary
        stratigraphic column, with id values corresponding to "id" column in
        `phylogeny_df`.

        If None, hereditary stratigraphic columns will be created for all
        phylogenetic leaves (organisms without offspring) in order of
        appearance in `phylogeny_df`.

    Returns
    -------
    list of HereditaryStratigraphicColumn
        Population of hereditary stratigraphic columns for extant lineage
        members (i.e., phylogeny leaf nodes).

        Columns ordered in order of appearance of corresponding extant organism
        id.
    """

    assert not alifestd_has_multiple_roots(phylogeny_df)

    # must take leaf_ids before possible topological sort to preserve order
    if extant_ids is None:
        extant_ids = alifestd_find_leaf_ids(phylogeny_df)

    working_df = alifestd_to_working_format(phylogeny_df)
    assert "ancestor_id" in working_df

    if not alifestd_has_contiguous_ids(phylogeny_df):
        if not alifestd_is_topologically_sorted(phylogeny_df):
            phylogeny_df = alifestd_topological_sort(phylogeny_df)

        __, extant_ids = _reassign_ids(
            phylogeny_df["id"].to_numpy(), np.fromiter(extant_ids, int)
        )

    def lookup_ancestor_id(id_: int) -> typing.Optional[int]:
        return working_df["ancestor_id"].iloc[id_]

    def ascending_lineage_iterator(leaf_id: int) -> typing.Iterator[int]:
        cur_id = leaf_id
        while True:
            yield cur_id
            next_id = lookup_ancestor_id(cur_id)
            if cur_id == next_id:
                break
            cur_id = next_id

    def descending_tree_iterator() -> typing.Iterator[int]:
        # assumes phylogeny dataframe is topologically sorted
        yield from working_df["id"]

    def get_stem_length(id_: int) -> typing.Union[float, int]:
        ancestor_id = lookup_ancestor_id(id_)
        if ancestor_id == id_:
            return 0
        elif "origin_time" in working_df:
            res = (
                working_df["origin_time"].iloc[id_]
                - working_df["origin_time"].iloc[ancestor_id]
            )
            assert res >= 0
            return res
        elif "generation" in working_df:
            res = (
                working_df["generation"].iloc[id_]
                - working_df["generation"].iloc[ancestor_id]
            )
            assert res >= 0
            return res
        else:
            return 1

    return descend_template_phylogeny(
        (ascending_lineage_iterator(leaf_id) for leaf_id in extant_ids),
        descending_tree_iterator(),
        lookup_ancestor_id,
        get_stem_length,
        seed_column,
        demark=lambda x: x,
    )
