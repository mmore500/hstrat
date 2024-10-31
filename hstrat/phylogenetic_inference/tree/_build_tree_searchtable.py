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

    fill_value = -1
    initial_capacity = max(len(population) * 2, 64)
    fill_values = [fill_value] * initial_capacity
    df = pd.DataFrame(
        {
            "id": pd.Series(fill_values, dtype=np.int64),
            "ancestor_id": pd.Series(fill_values, dtype=np.int64),
            "search ancestor_id": pd.Series(fill_values, dtype=np.int64),
            "search first_child_id": pd.Series(fill_values, dtype=np.int64),
            "search next_sibling_id": pd.Series(fill_values, dtype=np.int64),
            "taxon_label": [""] * initial_capacity,
            "differentia": pd.Series([0] * initial_capacity, dtype=np.uint64),
            "rank": pd.Series(fill_values, dtype=np.int64),
        },
    )
    id_cols = [x for x in df.columns if x.endswith("id")]
    df.loc[0, id_cols] = 0  # root
    size = 1

    def children(id_: int) -> typing.Iterable[int]:
        nonlocal df
        cur, prev = df.at[id_, "search first_child_id"], id_
        while cur != prev:
            yield cur
            cur, prev = df.at[cur, "search next_sibling_id"], cur

    def has_search_parent(id_: int) -> bool:
        nonlocal df
        return df.at[id_, "search ancestor_id"] != id_

    def inner_children(id_: int) -> typing.Iterable[int]:
        nonlocal df
        for child in children(id_):
            if df.at[id_, "search first_child_id"] != id_:
                yield child

    def differentia(id_: int) -> int:
        nonlocal df
        return df.at[id_, "differentia"]

    def rank(id_: int) -> int:
        nonlocal df
        return df.at[id_, "rank"]

    def attach_search_parent(id_: int, parent_id: int) -> None:
        nonlocal df
        if df.at[id_, "search ancestor_id"] == parent_id:
            return

        df.at[id_, "search ancestor_id"] = parent_id

        ancestor_first_child = df.at[parent_id, "search first_child_id"]
        is_first_child_ = ancestor_first_child == parent_id
        new_next_sibling = id_ if is_first_child_ else ancestor_first_child
        df.at[id_, "search next_sibling_id"] = new_next_sibling
        df.at[parent_id, "search first_child_id"] = id_

    def detach_search_parent(id_: int) -> None:
        nonlocal df
        ancestor_id = df.at[id_, "search ancestor_id"]
        if not has_search_parent(id_):  # root
            return

        is_first_child_ = df.at[ancestor_id, "search first_child_id"] == id_
        next_sibling = df.at[id_, "search next_sibling_id"]
        is_last_child = next_sibling == id_

        if is_first_child_:
            new_first_child = ancestor_id if is_last_child else next_sibling
            df.at[ancestor_id, "search first_child_id"] = new_first_child
        else:
            for child1, child2 in it.pairwise(children(ancestor_id)):
                if child2 == id_:
                    new_next_sib = child1 if is_last_child else next_sibling
                    df.at[child1, "search next_sibling_id"] = new_next_sib
                    break
            else:
                assert False

        df.at[id_, "search ancestor_id"] = id_
        df.at[id_, "search next_sibling_id"] = id_

    def create_offspring(
        parent_id: int,
        differentia: int = 0,
        rank: int = fill_value,
        label: str = "",
    ) -> int:
        nonlocal df, size
        if size == len(df.index) - 1:
            # double the size of the dataframe
            # adapted from https://stackoverflow.com/a/50788670/17332200
            df = (
                df.loc[
                    np.clip(np.arange(size * 2), 0, size),
                ]
                .copy()
                .reset_index(drop=True)
            )

        id_ = size
        size += 1
        for col in id_cols:
            df.at[id_, col] = id_
        df.at[id_, "ancestor_id"] = parent_id
        df.at[id_, "taxon_label"] = label
        df.at[id_, "differentia"] = differentia
        df.at[id_, "rank"] = rank

        attach_search_parent(id_, parent_id)

        return id_

    def insert_artifact(
        ranks: typing.Sequence[int],
        differentiae: typing.Sequence[int],
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
                for inner_child in inner_children(cur_node)
                if rank(inner_child) < next_rank
            ]
            if node_stack:
                while node_stack:
                    pop_node = node_stack.pop()
                    detach_search_parent(pop_node)
                    # must grab a copy of inner children to prevent iterator
                    # invalidation
                    for grandchild in [*inner_children(pop_node)]:
                        # reattach dropped's children
                        if rank(grandchild) >= next_rank:
                            detach_search_parent(grandchild)
                            attach_search_parent(grandchild, cur_node)
                        else:
                            node_stack.append(grandchild)

                # group nodes made indistinguishable by collapsed precursors...
                groups = collections.defaultdict(list)
                for child in inner_children(cur_node):
                    groups[(rank(child), differentia(child))].append(child)
                # ... in order to keep only the tiebreak winner
                for group in groups.values():
                    group = sorted(group)
                    winner, losers = group[0], group[1:]
                    for loser in losers:  # keep only the 0th tiebreak winner
                        # reassign loser's children to winner
                        # must grab a copy of inner children to prevent
                        # iterator invalidation
                        for loser_child in [*inner_children(loser)]:
                            detach_search_parent(loser_child)
                            attach_search_parent(loser_child, winner)
                        # detach loser from search trie
                        detach_search_parent(loser)

            # DONE HANDLING SEARCH TREE CONSOLIDATION #########################
            ###################################################################

            for child in inner_children(cur_node):
                # check immediate children for next allele
                #
                # common allele origination trace is for special condition
                # optimization where GetDeepestCongruousAlleleOrigination
                # isn't needed
                if (
                    rank(child) == next_rank
                    and differentia(child) == next_differentia
                ):
                    cur_node = child
                    break
            else:
                # if no congruent node exists, create a new TrieInnerNode
                cur_node = create_offspring(
                    parent_id=cur_node,
                    differentia=next_differentia,
                    rank=next_rank,
                    label=f"inner_{size}",
                )

        create_offspring(  # leaf node
            parent_id=cur_node,
            label=label,
            rank=num_strata_deposited - 1,
        )

    for label, artifact in progress_wrap(
        give_len(zip(sorted_labels, sorted_population), len(population)),
    ):
        insert_artifact(
            [*artifact.IterRetainedRanks()],
            [*artifact.IterRetainedDifferentia()],
            label,
            artifact.GetNumStrataDeposited(),
        )

    df = alifestd_try_add_ancestor_list_col(df[:size].copy(), mutate=True)
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
