import polars as pl


def alifestd_mark_roots_polars(phylogeny_df: pl.DataFrame) -> pl.DataFrame:
    """Create column `is_root` to mark rows with no ancestor."""

    if "ancestor_id" not in phylogeny_df.lazy().collect_schema().names():
        raise NotImplementedError("ancestor_id column required")

    return phylogeny_df.with_columns(
        is_root=(pl.col("id") == pl.col("ancestor_id")),
    )
