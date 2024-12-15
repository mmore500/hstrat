import collections
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
from ._Searchtable import Searchtable


def _collapse_indistinguishable_children(
    table: Searchtable, cur_node: int
) -> None:
    """Collapse that have been made collapsed-away precursors."""
    # group nodes made indistinguishable by collapsed precursors...
    groups = collections.defaultdict(list)
    for child in table.iter_inner_search_children_of(cur_node):
        key = (table.get_rank_of(child), table.get_differentia_of(child))
        groups[key].append(child)
    assert len(groups) == len(set(key[1] for key in groups.keys()))
    # ^^^ check assumption used in cpp implementation (differentiae are unique)
    for group in groups.values():
        winner, *losers = sorted(group)
        for loser in losers:  # keep only the 0th tiebreak winner
            # reassign loser's children to winner
            # must grab a copy of inner children to prevent
            # iterator invalidation
            for loser_child in [*table.iter_inner_search_children_of(loser)]:
                table.detach_search_parent(loser_child)
                table.attach_search_parent(
                    taxon_id=loser_child, parent_id=winner
                )
            # detach loser from search trie
            table.detach_search_parent(loser)


def _consolidate_if_rank_dropped(
    table: Searchtable, *, cur_node: int, next_rank: int
) -> None:
    """Collapse away a descendant nodes from "search trie" if their ranks have
    been dropped by stratum retention policy.

    Ranks are recognized as "dropped" if `next_rank` skips past them. Performs
    a depth-first search to discover all nodes with ranks prior to `next_rank`.
    """

    next_child = next(table.iter_inner_search_children_of(cur_node), None)  # type: ignore
    if next_child is None or table.get_rank_of(next_child) >= next_rank:
        return

    node_stack = [*table.iter_inner_search_children_of(cur_node)]

    # collapse away nodes with ranks that have been dropped
    while node_stack:
        pop_node = node_stack.pop()
        table.detach_search_parent(pop_node)
        # must grab a copy of inner children to prevent iterator
        # invalidation
        for grandchild in [*table.iter_inner_search_children_of(pop_node)]:
            # reattach dropped's children
            if table.get_rank_of(grandchild) >= next_rank:
                table.detach_search_parent(grandchild)
                table.attach_search_parent(
                    taxon_id=grandchild, parent_id=cur_node
                )
            else:
                node_stack.append(grandchild)

    _collapse_indistinguishable_children(table, cur_node)


def _place_allele(
    table: Searchtable,
    *,
    cur_node: int,
    next_rank: int,
    next_differentia: int,
) -> int:
    """Descends the subtrie from `cur_node` to retrieve the child node
    consistent with the given rank/differentia combination, creating a new
    node if necessary."""

    for child in table.iter_inner_search_children_of(cur_node):
        # check immediate children for next allele
        rank_matches = table.get_rank_of(child) == next_rank
        differentia_matches = (
            table.get_differentia_of(child) == next_differentia
        )
        if rank_matches and differentia_matches:
            return child
    else:
        # if no congruent node exists, create a new node
        return table.create_offspring(
            differentia=next_differentia,
            parent_id=cur_node,
            rank=next_rank,
        )


def _insert_artifact(
    table: "Searchtable",
    *,
    ranks: typing.Iterable[int],
    differentiae: typing.Iterable[int],
    taxon_label: int,
    num_strata_deposited: int,
) -> None:
    """Insert a taxon into the trie, ultimately resulting in the creation
    of an additional leaf node and --- if necessary --- a unifurcating chain of
    inner nodes subtending it."""

    cur_node = 0  # root
    for next_rank, next_differentia in zip(ranks, differentiae):
        _consolidate_if_rank_dropped(
            table=table, cur_node=cur_node, next_rank=next_rank
        )
        cur_node = _place_allele(
            table,
            cur_node=cur_node,
            next_rank=next_rank,
            next_differentia=next_differentia,
        )

    table.create_offspring(  # leaf node
        differentia=None,
        parent_id=cur_node,
        rank=num_strata_deposited - 1,
        taxon_label=taxon_label,
    )


def _finalize_records(
    records: typing.List[dict], *, force_common_ancestry: bool
) -> pd.DataFrame:
    """Collate as phylogeny dataframe in alife standard format."""
    df = pd.DataFrame(records)
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
    progress_wrap: typing.Optional[typing.Callable] = None,
    force_common_ancestry: bool = False,
) -> pd.DataFrame:
    """Pure-python implementation of `build_tree_searchtable`.

    Parameters
    ----------
    population: Sequence[HereditaryStratigraphicArtifact]
        Hereditary stratigraphic columns corresponding to extant population members.

        Each member of population will correspond to a unique leaf node in the
        reconstructed tree.
    taxon_labels: Optional[Iterable], optional
        How should leaf nodes representing extant hereditary stratigraphic
        columns be named?

        Label order should correspond to the order of corresponding hereditary
        stratigraphic columns within `population`. If None, taxons will be
        named according to their numerical index.
    force_common_ancestry: bool, default False
        How should columns that definitively share no common ancestry be
        handled?

        If set to True, treat columns with no common ancestry as if they
        shared a common ancestor immediately before the genesis of the
        lineages. If set to False, columns within `population` that
        definitively do not share common ancestry will raise a ValueError.
    progress_wrap : Callable, optional
        Pass tqdm or equivalent to display a progress bar.

    Returns
    -------
    pd.DataFrame
        The reconstructed phylogenetic tree in alife standard format.

    Notes
    -----
    See `build_tree_searchtable` for algorithm overview.
    """
    pop_len = len(population)
    if pop_len == 0:
        return alifestd_make_empty()

    taxon_labels = [*opyt.or_value(taxon_labels, map(str, range(pop_len)))]
    sort_order = argsort([x.GetNumStrataDeposited() for x in population])
    sorted_population = [*map(population.__getitem__, sort_order)]
    taxon_labels = [*map(taxon_labels.__getitem__, sort_order)]

    table = Searchtable()
    for taxon_label, artifact in opyt.or_value(progress_wrap, lambda x: x)(
        give_len(zip(taxon_labels, sorted_population), len(sorted_population)),
    ):
        _insert_artifact(
            table,
            ranks=artifact.IterRetainedRanks(),
            differentiae=artifact.IterRetainedDifferentia(),
            taxon_label=taxon_label,
            num_strata_deposited=artifact.GetNumStrataDeposited(),
        )

    return _finalize_records(
        table.to_records(),
        force_common_ancestry=force_common_ancestry,
    )
