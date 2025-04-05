import itertools as it
import typing

import numpy as np
import pandas as pd

from ._alifestd_find_leaf_ids import alifestd_find_leaf_ids
from ._alifestd_has_multiple_roots import alifestd_has_multiple_roots
from ._alifestd_is_strictly_bifurcating_asexual import (
    alifestd_is_strictly_bifurcating_asexual,
)
from ._alifestd_is_working_format_asexual import (
    alifestd_is_working_format_asexual,
)
from ._alifestd_mark_num_descendants_asexual import (
    alifestd_mark_num_descendants_asexual,
)
from ._alifestd_try_add_ancestor_id_col import alifestd_try_add_ancestor_id_col
from ._jit import jit


@jit(nopython=True)
def _alifestd_unfurl_traversal_inorder_asexual_fast_path(
    ancestor_ids: np.ndarray,
    num_descendants: np.ndarray,
    leaf_ids: np.ndarray,
) -> np.ndarray:
    """Implementation detail for phylogenies in working format."""
    dtype = ancestor_ids.dtype
    ancestor_lookup = ancestor_ids
    num_descendants_lookup = num_descendants

    site_assignments = np.zeros(len(ancestor_ids), dtype=dtype)
    visited = np.zeros(len(ancestor_ids), dtype=np.bool_)
    for leaf_id in leaf_ids:

        # find offset of closest visited ancestor, if any
        current_id = leaf_id
        while True:
            if visited[current_id]:
                offset = site_assignments[current_id] + 1
                break

            current_id, prev_id = ancestor_lookup[current_id], current_id
            if current_id == prev_id:
                offset = 0
                break

        site_assignments[leaf_id] = offset
        prev_id, current_id = leaf_id, ancestor_lookup[leaf_id]
        while current_id != prev_id:
            if visited[current_id]:
                break
            visited[current_id] = True

            assigned_site = offset + num_descendants_lookup[prev_id] + 1
            site_assignments[current_id] = assigned_site

            current_id, prev_id = ancestor_lookup[current_id], current_id

    result = np.empty(len(ancestor_ids), dtype=dtype)
    result[site_assignments] = np.arange(site_assignments.size)
    return result


def _alifestd_unfurl_traversal_inorder_asexual_slow_path(
    phylogeny_df: pd.DataFrame,
) -> np.ndarray:
    """Implementation detail for phylogenies not in working format."""
    phylogeny_df = alifestd_try_add_ancestor_id_col(phylogeny_df, mutate=True)

    phylogeny_df = alifestd_mark_num_descendants_asexual(
        phylogeny_df, mutate=True
    )

    ancestor_lookup = dict(
        zip(phylogeny_df["id"], phylogeny_df["ancestor_id"]),
    )
    num_descendants_lookup = dict(
        zip(phylogeny_df["id"], phylogeny_df["num_descendants"]),
    )
    leaves = alifestd_find_leaf_ids(phylogeny_df)

    def iter_lineage(leaf_id: int) -> typing.Iterator[int]:
        current_id = leaf_id
        while True:
            yield current_id
            current_id, prev_id = ancestor_lookup[current_id], current_id
            if current_id == prev_id:
                break

    site_assignments = dict()
    visited = set()
    for leaf_id in leaves:

        # find offset of closest visited ancestor, if any
        visited_ancestor = next(
            filter(visited.__contains__, iter_lineage(leaf_id)),
            None,
        )
        offset = (
            0
            if visited_ancestor is None
            else site_assignments[visited_ancestor] + 1
        )

        site_assignments[leaf_id] = offset
        for prev_id, current_id in it.pairwise(
            it.takewhile(
                lambda lineage_id: lineage_id not in visited,
                iter_lineage(leaf_id),
            ),
        ):
            visited.add(current_id)

            assigned_site = offset + num_descendants_lookup[prev_id] + 1
            assert 0 <= assigned_site < len(phylogeny_df)
            assert assigned_site not in site_assignments.values()

            assert current_id not in site_assignments
            site_assignments[current_id] = assigned_site

        visited.add(leaf_id)

    assert len(site_assignments) == len(phylogeny_df)
    assert len(site_assignments) == len(visited)
    assert len(site_assignments) == len(set(site_assignments.values()))

    result = np.empty(len(phylogeny_df), dtype=int)
    for id_, assigned_site in site_assignments.items():
        result[assigned_site] = id_
    return result


def alifestd_unfurl_traversal_inorder_asexual(
    phylogeny_df: pd.DataFrame,
    mutate: bool = False,
) -> np.ndarray:
    """List `id` values in inorder traversal order.

    The provided dataframe must be asexual and strictly bifurcating.
    """
    if not mutate:
        phylogeny_df = phylogeny_df.copy()

    if alifestd_has_multiple_roots(phylogeny_df):
        raise ValueError(
            "Phylogeny must have a single root for inorder traversal."
        )
    if not alifestd_is_strictly_bifurcating_asexual(phylogeny_df):
        raise ValueError(
            "Phylogeny must be strictly bifurcating for inorder traversal.",
        )

    if alifestd_is_working_format_asexual(phylogeny_df, mutate=True):
        phylogeny_df = alifestd_mark_num_descendants_asexual(
            phylogeny_df, mutate=True
        )
        return _alifestd_unfurl_traversal_inorder_asexual_fast_path(
            phylogeny_df["ancestor_id"].to_numpy(),
            phylogeny_df["num_descendants"].to_numpy(),
            alifestd_find_leaf_ids(phylogeny_df),
        )
    else:
        return _alifestd_unfurl_traversal_inorder_asexual_slow_path(
            phylogeny_df,
        )
