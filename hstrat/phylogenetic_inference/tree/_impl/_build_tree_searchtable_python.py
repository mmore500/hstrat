import collections
import dataclasses
import itertools as it
import typing

import more_itertools as mit
import numpy as np
import opytional as opyt
import pandas as pd

from ...._auxiliary_lib import (
    HereditaryStratigraphicArtifact,
    alifestd_collapse_unifurcations,
    alifestd_count_children_of_asexual,
    alifestd_find_root_ids,
    alifestd_make_empty,
    alifestd_try_add_ancestor_list_col,
    argsort,
    give_len,
)


@dataclasses.dataclass(slots=True)
class _Record:
    rank: int
    taxon_id: int
    taxon_label: str
    search_first_child_id: int = 0
    search_next_sibling_id: int = 0
    search_ancestor_id: int = 0
    ancestor_id: int = 0  # represents parent in the build tree
    differentia: typing.Optional[int] = None


def _children(
    records: typing.List[_Record], taxon_id: int
) -> typing.Iterable[int]:
    prev = taxon_id
    cur = records[taxon_id].search_first_child_id
    while cur != prev:
        yield cur
        prev = cur
        cur = records[cur].search_next_sibling_id


def _has_search_parent(records: typing.List[_Record], taxon_id: int) -> bool:
    return records[taxon_id].search_ancestor_id != taxon_id


def _inner_children(
    records: typing.List[_Record],
    taxon_id: int,
) -> typing.Iterable[int]:
    for child in _children(records, taxon_id):
        if records[taxon_id].search_first_child_id != taxon_id:
            yield child


def _differentia(records: typing.List[_Record], taxon_id: int) -> int:
    return records[taxon_id].differentia


def _rank(records: typing.List[_Record], taxon_id: int) -> int:
    return records[taxon_id].rank


def _attach_search_parent(
    records: typing.List[_Record], *, taxon_id: int, parent_id: int
) -> None:
    if records[taxon_id].search_ancestor_id == parent_id:
        return

    records[taxon_id].search_ancestor_id = parent_id

    ancestor_first_child = records[parent_id].search_first_child_id
    is_first_child_ = ancestor_first_child == parent_id
    new_next_sibling = taxon_id if is_first_child_ else ancestor_first_child
    records[taxon_id].search_next_sibling_id = new_next_sibling
    records[parent_id].search_first_child_id = taxon_id


def _detach_search_parent(
    records: typing.List[_Record], taxon_id: int
) -> None:
    ancestor_id = records[taxon_id].search_ancestor_id
    assert _has_search_parent(records, taxon_id)

    is_first_child_ = records[ancestor_id].search_first_child_id == taxon_id
    next_sibling = records[taxon_id].search_next_sibling_id
    is_last_child = next_sibling == taxon_id

    if is_first_child_:
        new_first_child = ancestor_id if is_last_child else next_sibling
        records[ancestor_id].search_first_child_id = new_first_child
    else:
        for child1, child2 in it.pairwise(_children(records, ancestor_id)):
            if child2 == taxon_id:
                new_next_sib = child1 if is_last_child else next_sibling
                records[child1].search_next_sibling_id = new_next_sib
                break
        else:
            assert False

    records[taxon_id].search_ancestor_id = taxon_id
    records[taxon_id].search_next_sibling_id = taxon_id


def _create_offspring(
    records: typing.List[_Record],
    *,
    parent_id: int,
    differentia: int,
    rank: int,
    taxon_label: str,
) -> int:

    taxon_id = len(records)
    record = _Record(
        ancestor_id=parent_id,
        differentia=differentia,
        rank=rank,
        taxon_id=taxon_id,
        taxon_label=taxon_label,
        search_ancestor_id=taxon_id,  # will be set in attach_search_parent
        search_first_child_id=taxon_id,
        search_next_sibling_id=taxon_id,
    )
    records.append(record)
    assert not _has_search_parent(records, taxon_id)
    _attach_search_parent(records, taxon_id=taxon_id, parent_id=parent_id)
    return taxon_id


def _collapse_indistinguishable_nodes(
    records: typing.List[_Record],
    cur_node: int,
) -> None:
    # group nodes made indistinguishable by collapsed precursors...
    groups = collections.defaultdict(list)
    for child in _inner_children(records, cur_node):
        key = (_rank(records, child), _differentia(records, child))
        groups[key].append(child)
    for group in groups.values():
        winner, *losers = sorted(group)
        for loser in losers:  # keep only the 0th tiebreak winner
            # reassign loser's children to winner
            # must grab a copy of inner children to prevent
            # iterator invalidation
            for loser_child in [*_inner_children(records, loser)]:
                _detach_search_parent(records, loser_child)
                _attach_search_parent(
                    records, taxon_id=loser_child, parent_id=winner
                )
            # detach loser from search trie
            _detach_search_parent(records, loser)


def _consolidate_trie(
    records: typing.List[_Record],
    *,
    next_rank: int,
    cur_node: int,
) -> None:

    next_child = next(_inner_children(records, cur_node), None)  # type: ignore
    if next_child is None or _rank(records, next_child) >= next_rank:
        return

    node_stack = [*_inner_children(records, cur_node)]

    # collapse away nodes with ranks that have been dropped
    while node_stack:
        pop_node = node_stack.pop()
        _detach_search_parent(records, pop_node)
        # must grab a copy of inner children to prevent iterator
        # invalidation
        for grandchild in [*_inner_children(records, pop_node)]:
            # reattach dropped's children
            if _rank(records, grandchild) >= next_rank:
                _detach_search_parent(records, grandchild)
                _attach_search_parent(
                    records, taxon_id=grandchild, parent_id=cur_node
                )
            else:
                node_stack.append(grandchild)

    _collapse_indistinguishable_nodes(records, cur_node)


def _place_allele(
    records: typing.List[_Record],
    *,
    cur_node: int,
    next_rank: int,
    next_differentia: int,
) -> int:
    for child in _inner_children(records, cur_node):
        # check immediate children for next allele
        rank_matches = _rank(records, child) == next_rank
        differentia_matches = _differentia(records, child) == next_differentia
        if rank_matches and differentia_matches:
            return child
    else:
        # if no congruent node exists, create a new node
        return _create_offspring(
            differentia=next_differentia,
            parent_id=cur_node,
            rank=next_rank,
            records=records,
            taxon_label=f"_inner{len(records)}",
        )


def _insert_artifact(
    records: typing.List[_Record],
    *,
    ranks: typing.Iterable[int],
    differentiae: typing.Iterable[int],
    taxon_label: int,
    num_strata_deposited: int,
) -> None:
    cur_node = 0  # root
    for next_rank, next_differentia in zip(ranks, differentiae):
        _consolidate_trie(records, next_rank=next_rank, cur_node=cur_node)
        cur_node = _place_allele(
            records,
            cur_node=cur_node,
            next_rank=next_rank,
            next_differentia=next_differentia,
        )

    _create_offspring(  # leaf node
        differentia=None,
        parent_id=cur_node,
        rank=num_strata_deposited - 1,
        records=records,
        taxon_label=taxon_label,
    )


def _finalize_records(
    records: typing.List[_Record],
    *,
    force_common_ancestry: bool,
) -> pd.DataFrame:
    df = pd.DataFrame([*map(dataclasses.asdict, records)])
    df["id"] = df["taxon_id"].astype(np.uint64)
    df["ancestor_id"] = df["ancestor_id"].astype(np.uint64)
    df["origin_time"] = df["rank"].astype(np.uint64)

    df = df[["id", "ancestor_id", "origin_time", "taxon_label"]]
    df = alifestd_try_add_ancestor_list_col(df, mutate=True)
    root_id = mit.one(alifestd_find_root_ids(df))
    multiple_true_roots = alifestd_count_children_of_asexual(df, root_id) > 1
    if multiple_true_roots and not force_common_ancestry:
        raise ValueError(
            "Reconstruction resulted in multiple independent trees, "
            "due to artifacts definitively sharing no common ancestor. "
            "Consider setting force_common_ancestry=True.",
        )
    df = alifestd_collapse_unifurcations(df, mutate=True)

    return df


def build_tree_searchtable_python(
    population: typing.Sequence[HereditaryStratigraphicArtifact],
    taxon_labels: typing.Optional[typing.Iterable] = None,
    progress_wrap: typing.Callable = lambda x: x,
    force_common_ancestry: bool = False,
) -> pd.DataFrame:
    """
    Uses the consolidated algorithm to build a tree, using a
    searchtable to access elements thereof.
    """

    pop_len = len(population)
    if pop_len == 0:
        return alifestd_make_empty()

    taxon_labels = [*opyt.or_value(taxon_labels, map(str, range(pop_len)))]
    sort_order = argsort([x.GetNumStrataDeposited() for x in population])
    sorted_population = [*map(population.__getitem__, sort_order)]
    taxon_labels = [*map(taxon_labels.__getitem__, sort_order)]

    records = [_Record(rank=0, taxon_id=0, taxon_label="_root")]
    for taxon_label, artifact in progress_wrap(
        give_len(zip(taxon_labels, sorted_population), len(sorted_population)),
    ):
        _insert_artifact(
            records,
            ranks=artifact.IterRetainedRanks(),
            differentiae=artifact.IterRetainedDifferentia(),
            taxon_label=taxon_label,
            num_strata_deposited=artifact.GetNumStrataDeposited(),
        )
    return _finalize_records(
        records,
        force_common_ancestry=force_common_ancestry,
    )
