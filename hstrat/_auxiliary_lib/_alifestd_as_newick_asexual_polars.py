import logging
import typing

import numpy as np
import polars as pl

from ._alifestd_as_newick_asexual import _build_newick_string
from ._alifestd_has_contiguous_ids_polars import (
    alifestd_has_contiguous_ids_polars,
)
from ._alifestd_is_topologically_sorted import (
    _is_topologically_sorted_contiguous,
)
from ._alifestd_mark_node_depth_asexual import (
    _alifestd_calc_node_depth_asexual_contiguous,
)
from ._alifestd_try_add_ancestor_id_col_polars import (
    alifestd_try_add_ancestor_id_col_polars,
)


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

    if not alifestd_has_contiguous_ids_polars(phylogeny_df):
        raise NotImplementedError("non-contiguous ids not yet supported")

    ids = phylogeny_df["id"].to_numpy()
    ancestor_ids = phylogeny_df["ancestor_id"].to_numpy()

    if not _is_topologically_sorted_contiguous(ancestor_ids):
        raise NotImplementedError(
            "polars topological sort not yet implemented",
        )

    logging.info("setting up `origin_time_delta`...")
    schema_names = phylogeny_df.lazy().collect_schema().names()
    if "origin_time_delta" in schema_names:
        logging.info("... already present!")
        origin_time_deltas = (
            phylogeny_df["origin_time_delta"].to_numpy().astype(float)
        )
    elif "origin_time" in schema_names:
        logging.info("... calculating from `origin_time`...")
        origin_times = phylogeny_df["origin_time"].to_numpy().astype(float)
        origin_time_deltas = (
            origin_times - origin_times[ancestor_ids.astype(int)]
        )
    else:
        logging.info("... marking null")
        origin_time_deltas = np.full(len(phylogeny_df), np.nan)

    logging.info("calculating node depth...")
    node_depths = _alifestd_calc_node_depth_asexual_contiguous(ancestor_ids)

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
