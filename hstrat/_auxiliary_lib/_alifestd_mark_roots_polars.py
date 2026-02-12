import polars as pl


def alifestd_mark_roots_polars(phylogeny_df: pl.DataFrame) -> pl.DataFrame:
    """Create column `is_root` to mark rows with no ancestor."""

    if not "ancestor_id" in phylogeny_df.columns:
        raise NotImplementedError("ancestor_id column required")

    return phylogeny_df.with_columns(
        is_root=(pl.col("id") == pl.col("ancestor_id")),
    )
