import typing

import opytional as opyt
import ordered_set as ods
import pandas as pd

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

    if "origin_time" not in phylogeny_df and "generation" in phylogeny_df:
        phylogeny_df["origin_time"] = phylogeny_df["generation"]

    if "origin_time" in phylogeny_df:
        # ensure topological sort
        phylogeny_df = phylogeny_df.sort_values("origin_time")

    phylogeny_df = phylogeny_df.set_index("id", drop=False)

    def extract_ancestor_id(ancestor_list_str: str) -> typing.Optional[int]:
        if ancestor_list_str in (
            "[]",
            "[none]",
            "[None]",
            "[NONE]",
        ):
            return None
        else:
            without_brackets_str = ancestor_list_str[1:-1]
            return int(without_brackets_str)

    def find_leaf_ids() -> ods.OrderedSet:  # [int]
        all_ids = ods.OrderedSet(phylogeny_df["id"])
        internal_ids = ods.OrderedSet(
            extract_ancestor_id(ancestor_list)
            for ancestor_list in phylogeny_df["ancestor_list"]
        )
        return all_ids - internal_ids

    def lookup_ancestor_id(id: int) -> typing.Optional[int]:
        return extract_ancestor_id(phylogeny_df.at[id, "ancestor_list"])

    def ascending_lineage_iterator(leaf_id: int) -> typing.Iterator[int]:
        cur_id = leaf_id
        while True:
            yield cur_id
            cur_id = lookup_ancestor_id(cur_id)
            if cur_id is None:
                break

    def descending_tree_iterator() -> typing.Iterator[int]:
        # ensure exactly one root
        assert (
            extract_ancestor_id(phylogeny_df.iloc[0]["ancestor_list"]) is None
        ), phylogeny_df.iloc[0]["ancestor_list"]
        assert not any(phylogeny_df.iloc[1:]["ancestor_list"] == "[]")
        assert not any(phylogeny_df.iloc[1:]["ancestor_list"] == "[none]")
        assert not any(phylogeny_df.iloc[1:]["ancestor_list"] == "[None]")

        # assumes phylogeny dataframe is topologically sorted
        yield from phylogeny_df["id"]

    def get_stem_length(id: int) -> typing.Union[float, int]:
        ancestor_id = lookup_ancestor_id(id)
        if ancestor_id is None:
            return 0
        elif "origin_time" in phylogeny_df:
            res = (
                phylogeny_df.loc[id]["origin_time"]
                - phylogeny_df.loc[ancestor_id]["origin_time"]
            )
            assert res >= 0
            return res
        else:
            return 1

    return descend_template_phylogeny(
        (
            ascending_lineage_iterator(leaf_id)
            for leaf_id in opyt.or_else(extant_ids, find_leaf_ids)
        ),
        descending_tree_iterator(),
        lookup_ancestor_id,
        get_stem_length,
        seed_column,
    )
