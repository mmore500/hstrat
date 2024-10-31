import dataclasses
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


@dataclasses.dataclass(slots=True)
class Record:
    ix_id: int = 0
    ix_search_first_child_id: int = 0
    ix_search_next_sibling_id: int = 0
    ix_search_ancestor_id: int = 0
    ix_ancestor_id: int = 0
    ix_differentia: int = 0
    ix_rank: int = 0

records_type = typing.List[Record]


def children(records: records_type, id_: int) -> typing.Iterable[int]:
    prev = id_
    cur = records[id_].ix_search_first_child_id
    while cur != prev:
        yield cur
        prev = cur
        cur = records[cur].ix_search_next_sibling_id


def has_search_parent(records: records_type, id_: int) -> bool:
    return records[id_].ix_search_ancestor_id != id_


def inner_children(
    records: records_type,
    id_: int,
) -> typing.Iterable[int]:
    for child in children(records, id_):
        if records[id_].ix_search_first_child_id != id_:
            yield child


def differentia(records: records_type, id_: int) -> int:
    return records[id_].ix_differentia


def rank(records: records_type, id_: int) -> int:
    return records[id_].ix_rank


def attach_search_parent(
    records: records_type, id_: int, parent_id: int
) -> None:
    if records[id_].ix_search_ancestor_id == parent_id:
        return

    records[id_].ix_search_ancestor_id = parent_id

    ancestor_first_child = records[parent_id].ix_search_first_child_id
    is_first_child_ = ancestor_first_child == parent_id
    new_next_sibling = id_ if is_first_child_ else ancestor_first_child
    records[id_].ix_search_next_sibling_id = new_next_sibling
    records[parent_id].ix_search_first_child_id = id_


def detach_search_parent(records: records_type, id_: int) -> None:
    ancestor_id = records[id_].ix_search_ancestor_id
    assert has_search_parent(records, id_)

    is_first_child_ = records[ancestor_id].ix_search_first_child_id == id_
    next_sibling = records[id_].ix_search_next_sibling_id
    is_last_child = next_sibling == id_

    if is_first_child_:
        new_first_child = ancestor_id if is_last_child else next_sibling
        records[ancestor_id].ix_search_first_child_id = new_first_child
    else:
        for child1, child2 in it.pairwise(children(records, ancestor_id)):
            if child2 == id_:
                new_next_sib = child1 if is_last_child else next_sibling
                records[child1].ix_search_next_sibling_id = new_next_sib
                break
        else:
            assert False

    records[id_].ix_search_ancestor_id = id_
    records[id_].ix_search_next_sibling_id = id_


def create_offspring(
    records: records_type,
    parent_id: int,
    differentia: int = 0,
    rank: int = 0,
) -> int:
    size = len(records)

    id_ = size
    records.append(Record())
    record = records[id_]
    record.ix_id = id_
    record.ix_search_first_child_id = id_
    record.ix_search_next_sibling_id = id_
    record.ix_ancestor_id = parent_id
    record.ix_differentia = differentia
    record.ix_rank = rank

    # handles
    records[id_].ix_search_ancestor_id = id_
    attach_search_parent(records, id_, parent_id)

    return id_


def insert_artifact(
    records: records_type,
    taxon_labels: typing.List[str],
    ranks: typing.List[int],
    differentiae: typing.List[int],
    label: str,
    num_strata_deposited: int = 0,
) -> None:

    cur_node = 0  # root
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
            groups = dict()
            for child in inner_children(records, cur_node):
                key = (rank(records, child), differentia(records, child))
                if key not in groups:
                    groups[key] = [child]
                else:
                    groups[key].append(child)
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
            )
            taxon_labels.append(f"inner_{len(records)}")

    create_offspring(  # leaf node
        records=records,
        parent_id=cur_node,
        rank=num_strata_deposited - 1,
    )
    taxon_labels.append(label)


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

    outlabels = ["root"]
    records = [Record()]

    for label, artifact in progress_wrap(
        give_len(zip(sorted_labels, sorted_population), len(population)),
    ):
        insert_artifact(
            records,
            outlabels,
            np.array([*artifact.IterRetainedRanks()], dtype=np.uint64),
            np.array([*artifact.IterRetainedDifferentia()], dtype=np.uint64),
            label,
            artifact.GetNumStrataDeposited(),
        )

    df = pd.DataFrame(map(dataclasses.asdict, records))
    df["id"] = df["ix_id"]
    df["ancestor_id"] = df["ix_ancestor_id"]
    df["taxon_label"] = outlabels
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

    df["origin_time"] = df["ix_rank"]
    return df
