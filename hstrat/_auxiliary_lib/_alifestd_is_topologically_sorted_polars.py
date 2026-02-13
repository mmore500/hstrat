import polars as pl


def alifestd_is_topologically_sorted_polars(
    phylogeny_df: pl.DataFrame,
) -> bool:
    """Are all organisms listed after members of their `ancestor_list`?"""

    if "ancestor_id" not in phylogeny_df.lazy().collect_schema().names():
        raise NotImplementedError("ancestor_id column required")

    if (
        not phylogeny_df.lazy()
        .select(
            pl.col("id").diff().drop_nulls().ge(0).all(),
        )
        .collect()
        .item()
    ):
        raise NotImplementedError("unsorted id values not yet supported")

    return (
        phylogeny_df.lazy()
        .select((pl.col("ancestor_id") <= pl.col("id")).all())
        .collect()
        .item()
    )
