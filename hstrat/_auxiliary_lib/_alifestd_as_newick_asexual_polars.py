import logging
import typing

import numpy as np
import polars as pl

from ._alifestd_as_newick_asexual import _build_newick_string
from ._alifestd_has_contiguous_ids_polars import (
    alifestd_has_contiguous_ids_polars,
)
from ._alifestd_is_topologically_sorted import (
    _is_topologically_sorted,
    _is_topologically_sorted_contiguous,
)
from ._alifestd_mark_node_depth_asexual import (
    _alifestd_calc_node_depth_asexual_contiguous,
)
from ._alifestd_try_add_ancestor_id_col_polars import (
    alifestd_try_add_ancestor_id_col_polars,
)


def _calc_node_depth_general(
    ids: np.ndarray,
    ancestor_ids: np.ndarray,
) -> np.ndarray:
    """Compute node depths for non-contiguous IDs in topological order."""
    n = len(ids)
    id_to_idx = {}
    for idx in range(n):
        id_to_idx[int(ids[idx])] = idx

    node_depths = np.empty(n, dtype=np.int64)
    for idx in range(n):
        ancestor_id = int(ancestor_ids[idx])
        ancestor_idx = id_to_idx[ancestor_id]
        node_depths[idx] = node_depths[ancestor_idx] + 1

    return node_depths


def _topological_sort_general(
    ids: np.ndarray,
    ancestor_ids: np.ndarray,
) -> np.ndarray:
    """Return row indices in topological order for non-contiguous IDs."""
    n = len(ids)
    id_to_idx = {}
    children = {}
    roots = []

    for idx in range(n):
        id_val = int(ids[idx])
        anc_val = int(ancestor_ids[idx])
        id_to_idx[id_val] = idx
        if id_val == anc_val:
            roots.append(idx)
        else:
            children.setdefault(anc_val, []).append(idx)

    sorted_indices = []
    queue = list(roots)
    head = 0
    while head < len(queue):
        idx = queue[head]
        head += 1
        sorted_indices.append(idx)
        id_val = int(ids[idx])
        if id_val in children:
            queue.extend(children[id_val])

    return np.array(sorted_indices, dtype=np.intp)


def alifestd_as_newick_asexual_polars(
    phylogeny_df: pl.DataFrame,
    *,
    taxon_label: typing.Optional[str] = None,
    progress_wrap: typing.Callable = lambda x: x,
) -> str:
    """Convert phylogeny dataframe to Newick format.

    Parameters
    ----------
    phylogeny_df : pl.DataFrame
        Phylogeny dataframe in Alife standard format.
    taxon_label : str, optional
        Column to use for taxon labels, by default None.
    progress_wrap : typing.Callable, optional
        Pass tqdm or equivalent to display a progress bar.

    See Also
    --------
    alifestd_as_newick_asexual :
        Pandas-based implementation.
    """
    logging.info(
        "creating newick string for alifestd polars df "
        f"with shape {phylogeny_df.shape}",
    )

    phylogeny_df = phylogeny_df.lazy().collect()

    if phylogeny_df.is_empty():
        return ";"

    logging.info("adding ancestor id column, if not present")
    phylogeny_df = alifestd_try_add_ancestor_id_col_polars(phylogeny_df)

    # ensure ancestor_id is integer typed for numpy indexing
    phylogeny_df = phylogeny_df.with_columns(
        pl.col("ancestor_id").cast(pl.Int64),
    )

    ids = phylogeny_df["id"].to_numpy()
    ancestor_ids = phylogeny_df["ancestor_id"].to_numpy()
    is_contiguous = alifestd_has_contiguous_ids_polars(phylogeny_df)

    logging.info("ensuring topological sort...")
    is_sorted = (
        _is_topologically_sorted_contiguous(ancestor_ids)
        if is_contiguous
        else _is_topologically_sorted(ids, ancestor_ids)
    )

    if not is_sorted:
        sorted_indices = _topological_sort_general(ids, ancestor_ids)
        phylogeny_df = phylogeny_df[sorted_indices]
        ids = phylogeny_df["id"].to_numpy()
        ancestor_ids = phylogeny_df["ancestor_id"].to_numpy()
        is_contiguous = alifestd_has_contiguous_ids_polars(phylogeny_df)

    logging.info("setting up `origin_time_delta`...")
    schema_names = phylogeny_df.lazy().collect_schema().names()
    if "origin_time_delta" in schema_names:
        logging.info("... already present!")
        origin_time_deltas = (
            phylogeny_df["origin_time_delta"].to_numpy().astype(float)
        )
    elif "origin_time" in schema_names:
        logging.info("... calculating from `origin_time`...")
        if is_contiguous:
            origin_times = (
                phylogeny_df["origin_time"].to_numpy().astype(float)
            )
            origin_time_deltas = (
                origin_times - origin_times[ancestor_ids.astype(int)]
            )
        else:
            id_to_idx = {}
            for idx in range(len(ids)):
                id_to_idx[int(ids[idx])] = idx
            origin_times = (
                phylogeny_df["origin_time"].to_numpy().astype(float)
            )
            ancestor_origin_times = np.array(
                [origin_times[id_to_idx[int(a)]] for a in ancestor_ids],
            )
            origin_time_deltas = origin_times - ancestor_origin_times
    else:
        logging.info("... marking null")
        origin_time_deltas = np.full(len(phylogeny_df), np.nan)

    logging.info("calculating node depth...")
    if is_contiguous:
        node_depths = _alifestd_calc_node_depth_asexual_contiguous(
            ancestor_ids,
        )
    else:
        node_depths = _calc_node_depth_general(ids, ancestor_ids)

    logging.info("calculating postorder traversal order...")
    postorder_index = np.lexsort((ancestor_ids, node_depths))[::-1]

    logging.info("preparing labels...")
    if taxon_label is not None:
        labels = phylogeny_df[taxon_label].cast(pl.Utf8).to_numpy()
    else:
        labels = np.full(len(phylogeny_df), "", dtype=object)

    logging.info("creating newick string...")
    result = _build_newick_string(
        ids[postorder_index],
        labels[postorder_index],
        origin_time_deltas[postorder_index],
        ancestor_ids[postorder_index],
        progress_wrap=progress_wrap,
    )

    logging.info(f"{len(result)=} {result[:20]=}")
    return result
