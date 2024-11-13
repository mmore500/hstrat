import collections
import dataclasses
import itertools as it
import typing

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
    taxon_label: str
    ix_id: int = 0
    ix_search_first_child_id: int = 0
    ix_search_next_sibling_id: int = 0
    ix_search_ancestor_id: int = 0
    ix_ancestor_id: int = 0  # represents parent in the build tree
    ix_differentia: int = 0
    ix_rank: int = 0


def children(records: typing.List[Record], id_: int) -> typing.Iterable[int]:
    prev = id_
    cur = records[id_].ix_search_first_child_id
    while cur != prev:
        yield cur
        prev = cur
        cur = records[cur].ix_search_next_sibling_id


def has_search_parent(records: typing.List[Record], id_: int) -> bool:
    return records[id_].ix_search_ancestor_id != id_


def inner_children(
    records: typing.List[Record],
    id_: int,
) -> typing.Iterable[int]:
    for child in children(records, id_):
        if records[id_].ix_search_first_child_id != id_:
            yield child


def differentia(records: typing.List[Record], id_: int) -> int:
    return records[id_].ix_differentia


def rank(records: typing.List[Record], id_: int) -> int:
    return records[id_].ix_rank


def attach_search_parent(
    records: typing.List[Record], id_: int, parent_id: int
) -> None:
    if records[id_].ix_search_ancestor_id == parent_id:
        return

    records[id_].ix_search_ancestor_id = parent_id

    ancestor_first_child = records[parent_id].ix_search_first_child_id
    is_first_child_ = ancestor_first_child == parent_id
    new_next_sibling = id_ if is_first_child_ else ancestor_first_child
    records[id_].ix_search_next_sibling_id = new_next_sibling
    records[parent_id].ix_search_first_child_id = id_


def detach_search_parent(records: typing.List[Record], id_: int) -> None:
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
    records: typing.List[Record],
    parent_id: int,
    differentia: int,
    rank: int,
    taxon_label: str,
) -> int:
    size = len(records)

    id_ = size
    records.append(Record(taxon_label))
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


def collapse_indistinguishable_nodes(
    records: typing.List[Record],
    cur_node: int,
) -> None:
    # group nodes made indistinguishable by collapsed precursors...
    groups = collections.defaultdict(list)
    for child in inner_children(records, cur_node):
        key = (rank(records, child), differentia(records, child))
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


def consolidate_trie(
    records: typing.List[Record],
    next_rank: int,
    cur_node: int,
) -> None:

    next_child = next(inner_children(records, cur_node), None)  # type: ignore
    if next_child is None or rank(records, next_child) >= next_rank:
        return

    node_stack = [*inner_children(records, cur_node)]

    # collapse away nodes with ranks that have been dropped
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

    collapse_indistinguishable_nodes(records, cur_node)


def place_allele(
    records: typing.List[Record],
    cur_node: int,
    next_rank: int,
    next_differentia: int,
) -> int:
    for child in inner_children(records, cur_node):
        # check immediate children for next allele
        rank_matches = rank(records, child) == next_rank
        differentia_matches = differentia(records, child) == next_differentia
        if rank_matches and differentia_matches:
            return child
    else:
        # if no congruent node exists, create a new TrieInnerNode
        return create_offspring(
            records=records,
            parent_id=cur_node,
            differentia=next_differentia,
            rank=next_rank,
            taxon_label=f"i{len(records)}",
        )


def insert_artifact(
    records: typing.List[Record],
    ranks: typing.List[int],
    differentiae: typing.List[int],
    label: str,
    num_strata_deposited: int,
) -> None:

    cur_node = 0  # root
    for next_rank, next_differentia in zip(ranks, differentiae):
        consolidate_trie(records, next_rank, cur_node)
        cur_node = place_allele(
            records,
            cur_node,
            next_rank,
            next_differentia,
        )

    create_offspring(  # leaf node
        records=records,
        parent_id=cur_node,
        rank=num_strata_deposited - 1,
        differentia=-1,
        taxon_label=label,
    )


def finalize_records(
    records: typing.List[Record],
    force_common_ancestry: bool,
) -> pd.DataFrame:
    df = pd.DataFrame(map(dataclasses.asdict, records))
    df["id"] = df["ix_id"]
    df["ancestor_id"] = df["ix_ancestor_id"]
    df["origin_time"] = df["ix_rank"]

    multiple_true_roots = (
        (df["id"] != 0) & (df["ancestor_id"] == 0)
    ).sum() > 1
    if multiple_true_roots and not force_common_ancestry:
        raise ValueError(
            "Reconstruction resulted in multiple independent trees, "
            "due to artifacts definitively sharing no common ancestor. "
            "Consider setting force_common_ancestry=True.",
        )

    return alifestd_try_add_ancestor_list_col(df, mutate=True)


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

    records = [Record(taxon_label="root")]

    for label, artifact in progress_wrap(
        give_len(zip(sorted_labels, sorted_population), len(population)),
    ):
        insert_artifact(
            records,
            # map int to make invariant to numpy input
            [*map(int, artifact.IterRetainedRanks())],
            [*map(int, artifact.IterRetainedDifferentia())],
            label,
            artifact.GetNumStrataDeposited(),
        )

    return finalize_records(records, force_common_ancestry)
