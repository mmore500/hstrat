import typing

from astropy.utils.decorators import deprecated_renamed_argument
import numpy as np
import pandas as pd

from hstrat._auxiliary_lib import HereditaryStratigraphicInstrument

from ..._auxiliary_lib import (
    alifestd_find_leaf_ids,
    alifestd_has_contiguous_ids,
    alifestd_has_multiple_roots,
    alifestd_is_topologically_sorted,
    alifestd_to_working_format,
    alifestd_topological_sort,
    cast_int_lossless,
    give_len,
    unfurl_lineage_with_contiguous_ids,
)
from ..._auxiliary_lib._alifestd_assign_contiguous_ids import (
    _reassign_ids_asexual,
)
from ._descend_template_phylogeny import descend_template_phylogeny


@deprecated_renamed_argument("seed_column", "seed_instrument", since="1.20.0")
def descend_template_phylogeny_alifestd(
    phylogeny_df: pd.DataFrame,
    seed_instrument: HereditaryStratigraphicInstrument,
    extant_ids: typing.Optional[typing.Iterable[int]] = None,
    progress_wrap: typing.Callable = lambda x: x,
) -> typing.List[HereditaryStratigraphicInstrument]:
    """Generate a population of hereditary stratigraphic instruments that could
    have resulted from the template phylogeny.

    Parameters
    ----------
    phylogeny_df : pandas.DataFrame
        Phylogeny record as an alife-standard DataFrame.
    seed_instrument : HereditaryStratigraphicInstrument
        Hereditary stratigraphic instrument to seed at root node of phylogeny.

        Returned hereditary stratigraphic column population will be generated
        as if repeatedly calling `CloneDescendant()` on `seed_instrument`. As
        such, specifies configuration (i.e., differentia bit width and stratum
        retention policy) for returned columns. May already have strata
        deposited, which will be incorporated into generated extant population.
    extant_ids : optional list of int
        Which organisms should hereditary stratigraphic instruments be created
        for?

        Designates content and order of returned list of hereditary
        stratigraphic instrument, with id values corresponding to "id"
        instrument in `phylogeny_df`.

        If None, hereditary stratigraphic instruments will be created for all
        phylogenetic leaves (organisms without offspring) in order of
        appearance in `phylogeny_df`.
    progress_wrap : Callable, optional
        Wrapper applied around generation iterator and row generator for final
        phylogeny compilation process.

        Pass tqdm or equivalent to display progress bars.

    Returns
    -------
    list of HereditaryStratigraphicInstrument
        Population of hereditary stratigraphic instruments for extant lineage
        members (i.e., phylogeny leaf nodes).

        Instruments ordered in order of appearance of corresponding extant
        organism id.
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

        extant_ids = _reassign_ids_asexual(
            phylogeny_df["id"].to_numpy(), np.fromiter(extant_ids, int)
        )

    ancestor_id_lookup = working_df["ancestor_id"].iloc

    def lookup_ancestor_id(id_: int) -> int:
        return ancestor_id_lookup[id_]

    def get_stem_length(id_: int) -> int:
        ancestor_id = lookup_ancestor_id(id_)
        if ancestor_id == id_:
            return 0
        elif "origin_time" in working_df:
            res = (
                working_df["origin_time"].iloc[id_]
                - working_df["origin_time"].iloc[ancestor_id]
            )
            assert res >= 0
            return cast_int_lossless(
                res, action="warn", context="origin time difference"
            )
        elif "generation" in working_df:
            res = (
                working_df["generation"].iloc[id_]
                - working_df["generation"].iloc[ancestor_id]
            )
            assert res >= 0
            return cast_int_lossless(
                res, action="warn", context="origin time difference"
            )
        else:
            return 1

    return descend_template_phylogeny(
        give_len(
            (
                unfurl_lineage_with_contiguous_ids(
                    working_df["ancestor_id"].to_numpy(),
                    leaf_id,
                )
                for leaf_id in extant_ids
            ),
            len(extant_ids),
        ),
        working_df["id"].to_numpy(),  # descending_tree_iterable
        lookup_ancestor_id,
        get_stem_length,
        seed_instrument=seed_instrument,
        demark=lambda x: x,
        progress_wrap=progress_wrap,
    )
