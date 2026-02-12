import logging

import numpy as np
import polars as pl


def alifestd_mark_leaves_asexual_polars(
    phylogeny_df: pl.DataFrame,
) -> pl.DataFrame:
    """Add column `is_leaf` marking rows that are ancestor to no other row.

    Parameters
    ----------
    phylogeny_df : polars.DataFrame
        The phylogeny as a dataframe in alife standard format.

        Must represent an asexual phylogeny.

    Raises
    ------
    NotImplementedError
        If `phylogeny_df` has no "ancestor_id" column.
    NotImplementedError
        If `phylogeny_df` has non-contiguous ids.
    NotImplementedError
        If `phylogeny_df` is not topologically sorted.

    Returns
    -------
    polars.DataFrame
        The phylogeny with an added `is_leaf` boolean column.
    """
    if "ancestor_id" not in phylogeny_df.columns:
        raise NotImplementedError(
            "ancestor_id column required; ancestor_list not supported"
        )

    if phylogeny_df.is_empty():
        return phylogeny_df.with_columns(
            is_leaf=pl.Series([], dtype=pl.Boolean),
        )

    logging.info(
        "- alifestd_mark_leaves_asexual_polars: " "checking contiguous ids...",
    )
    has_contiguous_ids = phylogeny_df.select(
        pl.col("id").diff() == 1
    ).to_series().all() and (phylogeny_df["id"].first() == 0)
    if not has_contiguous_ids:
        raise NotImplementedError("non-contiguous ids not yet supported")

    logging.info(
        "- alifestd_mark_leaves_asexual_polars: "
        "checking topological sort...",
    )
    if (
        not phylogeny_df.select(pl.col("ancestor_id") <= pl.col("id"))
        .to_series()
        .all()
    ):
        raise NotImplementedError(
            "polars topological sort not yet implemented"
        )

    logging.info(
        "- alifestd_mark_leaves_asexual_polars: finding leaves...",
    )
    # internal nodes are those that appear as ancestor_id of some other node
    # (exclude root self-references: ancestor_id == id)
    internal_node_ids = (
        phylogeny_df.filter(pl.col("ancestor_id") != pl.col("id"))
        .select("ancestor_id")
        .to_series()
    )

    leaf_mask = np.ones(len(phylogeny_df), dtype=np.bool_)
    leaf_mask[internal_node_ids.to_numpy()] = False

    return phylogeny_df.with_columns(
        is_leaf=pl.Series(leaf_mask),
    )
