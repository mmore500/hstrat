from deprecated.sphinx import deprecated
import polars as pl


@deprecated(
    version="1.23.0",
    reason="Use phyloframe.legacy.alifestd_has_contiguous_ids_polars instead.",
)
def alifestd_has_contiguous_ids_polars(phylogeny_df: pl.DataFrame) -> bool:
    """Do organisms ids' correspond to their row number?"""
    return (
        phylogeny_df.lazy()
        .select((pl.col("id") == pl.int_range(0, pl.len())).all())
        .collect()
        .item()
    )
