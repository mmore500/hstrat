from collections import defaultdict
from functools import lru_cache
import itertools as it
import typing

import more_itertools as mit

from .._auxiliary_lib import splicewhile
from ..genome_instrumentation import (
    HereditaryStratigraphicColumn,
    HereditaryStratum,
    HereditaryStratumOrderedStoreList,
)


# descend tree to prepare lookup table for node depths
def _calc_node_depths(
    descending_tree_iterator: typing.Iterator,
    get_parent: typing.Callable,
    get_stem_length: typing.Callable,
) -> typing.Dict[int, int]:

    node_depth_lookup = dict()

    for root_node in descending_tree_iterator:
        node_depth_lookup[id(root_node)] = 0
        break

    for node in descending_tree_iterator:
        stem_length = get_stem_length(node)
        parent_node = get_parent(node)
        node_depth_lookup[id(node)] = (
            node_depth_lookup[id(parent_node)] + stem_length
        )

    return node_depth_lookup


def _educe_stratum_ordered_store(
    ascending_lineage_iterator: typing.Iterator,
    deposition_count_lookup: typing.Dict[int, int],
    stem_strata_lookup: typing.Dict[
        int, typing.Callable[[int], HereditaryStratum]
    ],
    stratum_retention_policy,
) -> HereditaryStratumOrderedStoreList:

    # usage ensures ascending_lineage_iterator not empty
    (tip_node,), ascending_lineage_iterator = mit.spy(
        ascending_lineage_iterator
    )
    tip_deposition_count = deposition_count_lookup[id(tip_node)]

    rising_required_ranks_iterator = (
        stratum_retention_policy.IterRetainedRanks(
            tip_deposition_count,
        )
    )

    # pairwise ensures we exclude root node
    stratum_ordered_store = HereditaryStratumOrderedStoreList()
    descending_lineage_iterator = iter(reversed([*ascending_lineage_iterator]))

    cur_node = next(descending_lineage_iterator)

    for rank in rising_required_ranks_iterator:
        while rank >= deposition_count_lookup[id(cur_node)]:
            cur_node = next(descending_lineage_iterator)

        rank_stratum_lookup = stem_strata_lookup[id(cur_node)]
        stratum_ordered_store.DepositStratum(
            rank=rank,
            stratum=rank_stratum_lookup(rank),
        )

    return stratum_ordered_store, tip_deposition_count


def descend_template_phylogeny_posthoc(
    ascending_lineage_iterators: typing.Iterator[typing.Iterator],
    descending_tree_iterator: typing.Iterator,
    get_parent: typing.Callable,
    get_stem_length: typing.Callable,
    seed_column: HereditaryStratigraphicColumn,
) -> typing.List[HereditaryStratigraphicColumn]:

    stratum_retention_policy = seed_column._stratum_retention_policy
    assert stratum_retention_policy.IterRetainedRanks is not None

    tree_depth_lookup = _calc_node_depths(
        descending_tree_iterator, get_parent, get_stem_length
    )
    deposition_count_lookup = {
        k: v + seed_column.GetNumStrataDeposited()
        for k, v in tree_depth_lookup.items()
    }

    stem_strata_lookup = defaultdict(
        # use lru_cache as defaultdict with default factory conditioned on key
        lambda: lru_cache(maxsize=None)(
            lambda rank: (
                # if applicable, use stratum from seed column
                # otherwise, create new stratum
                seed_column.GetStratumAtRank(rank)
                if rank < seed_column.GetNumStrataDeposited()
                else seed_column._CreateStratum(rank)
            )
        )
    )

    extant_population = [
        HereditaryStratigraphicColumn(
            always_store_rank_in_stratum=seed_column._always_store_rank_in_stratum,
            stratum_retention_policy=stratum_retention_policy,
            stratum_differentia_bit_width=seed_column.GetStratumDifferentiaBitWidth(),
            stratum_ordered_store=_educe_stratum_ordered_store(
                iter_,
                deposition_count_lookup,
                stem_strata_lookup,
                stratum_retention_policy,
            ),
        )
        for iter_ in ascending_lineage_iterators
    ]
    return extant_population
