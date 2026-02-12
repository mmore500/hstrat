import polars as pl


def alifestd_has_contiguous_ids_polars(phylogeny_df: pl.DataFrame) -> bool:
    """Do organisms ids' correspond to their row number?"""
    return (
        phylogeny_df.lazy()
        .select((pl.col("id") == pl.int_range(0, pl.len())).all())
        .collect()
        .item()
    )
