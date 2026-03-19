import polars as pl

from ._alifestd_assign_contiguous_ids import _reassign_ids_asexual


def alifestd_assign_contiguous_ids_polars(
    phylogeny_df: pl.DataFrame,
) -> pl.DataFrame:
    """Reassign so each organism's id corresponds to its row number.

    Organisms retain the same row location; only id numbers change. Input
    dataframe is not mutated by this operation unless `mutate` True.
    """
    phylogeny_df = phylogeny_df.lazy().collect()  # lazy not yet implemented

    if "ancestor_list" in phylogeny_df.columns:
        raise NotImplementedError

    new_ancestor_ids = _reassign_ids_asexual(
        phylogeny_df["id"].to_numpy(),
        phylogeny_df["ancestor_id"].to_numpy(),
    )

    return (
        phylogeny_df.drop("id")
        .with_row_index("id")
        .with_columns(
            ancestor_id=pl.Series(new_ancestor_ids),
        )
    )
