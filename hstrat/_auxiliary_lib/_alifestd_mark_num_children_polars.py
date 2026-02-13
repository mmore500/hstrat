import logging

import polars as pl

from ._alifestd_has_contiguous_ids_polars import (
    alifestd_has_contiguous_ids_polars,
)
from ._alifestd_mark_num_children_asexual import (
    _alifestd_mark_num_children_asexual_fast_path,
)
from ._alifestd_is_topologically_sorted_polars import (
    alifestd_is_topologically_sorted_polars,
)
from ._alifestd_mark_roots_polars import alifestd_mark_roots_polars


def alifestd_mark_num_children_polars(
    phylogeny_df: pl.DataFrame,
) -> pl.DataFrame:
    """Add column `num_children`, counting for each node the number of nodes it
    is parent to.
    """

    logging.info(
        "- alifestd_mark_num_children_polars: " "checking contiguous ids...",
    )
    if not alifestd_has_contiguous_ids_polars(phylogeny_df):
        raise NotImplementedError("non-contiguous ids not yet supported")

    logging.info(
        "- alifestd_mark_num_children_polars: " "checking topological sort...",
    )
    if not alifestd_is_topologically_sorted_polars(phylogeny_df):
        raise NotImplementedError(
            "topologically unsorted rows not yet supported",
        )

    if "is_root" not in phylogeny_df.lazy().collect_schema().names():
        logging.info(
            "- alifestd_mark_num_children_polars: marking roots...",
        )
        phylogeny_df = alifestd_mark_roots_polars(phylogeny_df)

    child_counts = _alifestd_mark_num_children_asexual_fast_path(
        phylogeny_df.lazy()
        .select("ancestor_id")
        .collect()
        .to_series()
        .to_numpy(),
    )

    return phylogeny_df.with_columns(
        num_children=child_counts,
    )
