import polars as pl


def alifestd_try_add_ancestor_id_col_polars(
    phylogeny_df: pl.DataFrame,
) -> pl.DataFrame:
    """Add an ancestor_id column to the input DataFrame if the phylogeny is
    asexual and the column does not already exist.
    """

    if "ancestor_id" in phylogeny_df.lazy().collect_schema().names() or (
        phylogeny_df.lazy()
        .select(
            pl.col("ancestor_list").str.contains(",").any(),
        )
        .collect()
        .item()
    ):
        return phylogeny_df

    return phylogeny_df.with_columns(
        ancestor_id=pl.col("ancestor_list")
        .str.extract(r"(\d+)", 1)
        .cast(pl.UInt64, strict=False)
        .fill_null(pl.col("id"))
    )
