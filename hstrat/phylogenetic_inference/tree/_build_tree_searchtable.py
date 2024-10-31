import collections
import itertools as it
import typing

import numpy as np
import opytional as opyt
import pandas as pd

from ..._auxiliary_lib import (
    HereditaryStratigraphicArtifact,
    alifestd_make_empty,
    alifestd_try_add_ancestor_list_col,
    argsort,
    give_len,
)


def children(records: typing.List[dict], id_: int) -> typing.Iterable[int]:
    cur, prev = records[id_]["search first_child_id"], id_
    while cur != prev:
        yield cur
        cur, prev = records[cur]["search next_sibling_id"], cur


def has_search_parent(records: typing.List[dict], id_: int) -> bool:
    return records[id_]["search ancestor_id"] != id_


def inner_children(
    records: typing.List[dict],
    id_: int,
) -> typing.Iterable[int]:
    for child in children(records, id_):
        if records[id_]["search first_child_id"] != id_:
            yield child


def differentia(records: typing.List[dict], id_: int) -> int:
    return records[id_]["differentia"]


def rank(records: typing.List[dict], id_: int) -> int:
    return records[id_]["rank"]


def attach_search_parent(
    records: typing.List[dict], id_: int, parent_id: int
) -> None:
    if records[id_]["search ancestor_id"] == parent_id:
        return

    records[id_]["search ancestor_id"] = parent_id

    ancestor_first_child = records[parent_id]["search first_child_id"]
    is_first_child_ = ancestor_first_child == parent_id
    new_next_sibling = id_ if is_first_child_ else ancestor_first_child
    records[id_]["search next_sibling_id"] = new_next_sibling
    records[parent_id]["search first_child_id"] = id_


def detach_search_parent(records: typing.List[dict], id_: int) -> None:
    ancestor_id = records[id_]["search ancestor_id"]
    assert has_search_parent(records, id_)

    is_first_child_ = records[ancestor_id]["search first_child_id"] == id_
    next_sibling = records[id_]["search next_sibling_id"]
    is_last_child = next_sibling == id_

    if is_first_child_:
        new_first_child = ancestor_id if is_last_child else next_sibling
        records[ancestor_id]["search first_child_id"] = new_first_child
    else:
        for child1, child2 in it.pairwise(children(records, ancestor_id)):
            if child2 == id_:
                new_next_sib = child1 if is_last_child else next_sibling
                records[child1]["search next_sibling_id"] = new_next_sib
                break
        else:
            assert False

    records[id_]["search ancestor_id"] = id_
    records[id_]["search next_sibling_id"] = id_


def create_offspring(
    records: typing.List[dict],
    parent_id: int,
    differentia: int = np.uint64(0),
    rank: int = np.uint64(0),
    label: str = "",
) -> int:
    size = len(records)

    id_ = size
    records.append(dict())
    records[id_]["id"] = id_
    records[id_]["search first_child_id"] = id_
    records[id_]["search next_sibling_id"] = id_
    records[id_]["ancestor_id"] = parent_id
    records[id_]["taxon_label"] = label
    records[id_]["differentia"] = differentia
    records[id_]["rank"] = rank

    # handles
    records[id_]["search ancestor_id"] = id_
    attach_search_parent(records, id_, parent_id)

    return id_


def insert_artifact(
    records: typing.List[dict],
    ranks: typing.Sequence[int],
    differentiae: typing.Sequence[int],
    label: str,
    num_strata_deposited: int = np.uint64(0),
) -> None:

    cur_node = np.uint64(0)  # root
    for next_rank, next_differentia in zip(ranks, differentiae):

        ###################################################################
        # BEGIN HANDLING SEARCH TREE CONSOLIDATION ########################

        # collapse away nodes with ranks that have been dropped
        node_stack = [
            inner_child
            for inner_child in inner_children(records, cur_node)
            if rank(records, inner_child) < next_rank
        ]
        if node_stack:
            while node_stack:
                pop_node = node_stack.pop()
                detach_search_parent(records, pop_node)
                # must grab a copy of inner children to prevent iterator
                # invalidation
                for grandchild in [*inner_children(records, pop_node)]:
                    # reattach dropped's children
                    if rank(records, grandchild) >= next_rank:
                        detach_search_parent(records, grandchild)
                        attach_search_parent(records, grandchild, cur_node)
                    else:
                        node_stack.append(grandchild)

            # group nodes made indistinguishable by collapsed precursors...
            groups = collections.defaultdict(list)
            for child in inner_children(records, cur_node):
                groups[
                    (rank(records, child), differentia(records, child))
                ].append(child)
            # ... in order to keep only the tiebreak winner
            for group in groups.values():
                group = sorted(group)
                winner, losers = group[0], group[1:]
                for loser in losers:  # keep only the 0th tiebreak winner
                    # reassign loser's children to winner
                    # must grab a copy of inner children to prevent
                    # iterator invalidation
                    for loser_child in [*inner_children(records, loser)]:
                        detach_search_parent(records, loser_child)
                        attach_search_parent(records, loser_child, winner)
                    # detach loser from search trie
                    detach_search_parent(records, loser)

        # DONE HANDLING SEARCH TREE CONSOLIDATION #########################
        ###################################################################

        for child in inner_children(records, cur_node):
            # check immediate children for next allele
            #
            # common allele origination trace is for special condition
            # optimization where GetDeepestCongruousAlleleOrigination
            # isn't needed
            if (
                rank(records, child) == next_rank
                and differentia(records, child) == next_differentia
            ):
                cur_node = child
                break
        else:
            # if no congruent node exists, create a new TrieInnerNode
            cur_node = create_offspring(
                records=records,
                parent_id=cur_node,
                differentia=next_differentia,
                rank=next_rank,
                label=f"inner_{len(records)}",
            )

    create_offspring(  # leaf node
        records=records,
        parent_id=cur_node,
        label=label,
        rank=num_strata_deposited - 1,
    )


def build_tree_searchtable(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    taxon_labels: typing.Optional[typing.Iterable] = None,
    progress_wrap: typing.Callable = lambda x: x,
    force_common_ancestry: bool = False,
) -> pd.DataFrame:
    """TODO."""
    # for simplicity, return early for this special case
    if len(population) == 0:
        return alifestd_make_empty()

    taxon_labels = list(
        opyt.or_value(
            taxon_labels,
            map(str, range(len(population))),
        )
    )

    sort_order = argsort([x.GetNumStrataDeposited() for x in population])
    sorted_labels = [taxon_labels[i] for i in sort_order]
    sorted_population = [population[i] for i in sort_order]

    records = [
        {
            "id": np.uint64(0),
            "ancestor_id": np.uint64(0),
            "search ancestor_id": np.uint64(0),
            "search first_child_id": np.uint64(0),
            "search next_sibling_id": np.uint64(0),
            "taxon_label": "root",
            "differentia": np.int64(0),
            "rank": np.uint64(0),
        },
    ]

    for label, artifact in progress_wrap(
        give_len(zip(sorted_labels, sorted_population), len(population)),
    ):
        insert_artifact(
            records,
            [*artifact.IterRetainedRanks()],
            [*artifact.IterRetainedDifferentia()],
            label,
            artifact.GetNumStrataDeposited(),
        )

    df = pd.DataFrame(records)
    df = alifestd_try_add_ancestor_list_col(df, mutate=True)
    multiple_true_roots = (
        (df["id"] != 0) & (df["ancestor_id"] == 0)
    ).sum() > 1
    if multiple_true_roots and not force_common_ancestry:
        raise ValueError(
            "Reconstruction resulted in multiple independent trees, "
            "due to artifacts definitively sharing no common ancestor. "
            "Consider setting force_common_ancestry=True.",
        )

    df["origin_time"] = df["rank"]
    return df
