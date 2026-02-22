import logging

import polars as pl

from .._auxiliary_lib import (
    alifestd_has_contiguous_ids_polars,
    alifestd_is_topologically_sorted_polars,
)


# columns required to deserialize surfaces from data_hex
_deserialization_columns = (
    "data_hex",
    "dstream_algo",
    "dstream_storage_bitoffset",
    "dstream_storage_bitwidth",
    "dstream_T_bitoffset",
    "dstream_T_bitwidth",
    "dstream_S",
)


def alifestd_validate_trie(df: pl.DataFrame) -> pl.DataFrame:
    """Validate trie reconstruction output data, checking that required
    columns are present, ids are contiguous, and data is topologically sorted.

    Checks performed:
    - Required dstream/downstream columns for surface deserialization from
      ``data_hex`` are present.
    - Logs the number of tip (leaf) nodes.
    - Checks that ids are contiguous (i.e., match row numbers).
    - Checks that data is topologically sorted (ancestors before descendants).

    Parameters
    ----------
    df : pl.DataFrame
        Trie reconstruction output, as produced by
        ``surface_unpack_reconstruct`` with ``--no-drop-dstream-metadata``.

        Required schema:
            - 'id' : integer
            - 'ancestor_id' : integer
            - 'data_hex' : string
            - 'dstream_algo' : string or categorical
            - 'dstream_storage_bitoffset' : integer
            - 'dstream_storage_bitwidth' : integer
            - 'dstream_T_bitoffset' : integer
            - 'dstream_T_bitwidth' : integer
            - 'dstream_S' : integer

    Returns
    -------
    pl.DataFrame
        The input DataFrame, passed through unchanged.

    Raises
    ------
    ValueError
        If any required column is missing, ids are not contiguous, or data
        is not topologically sorted.

    See Also
    --------
    surface_unpack_reconstruct :
        Produces trie reconstruction data validated here.
    """
    columns = set(df.lazy().collect_schema().names())

    logging.info("alifestd_validate_trie: checking required columns...")
    missing = [c for c in _deserialization_columns if c not in columns]
    if missing:
        raise ValueError(
            "alifestd_validate_trie: missing deserialization columns "
            f"{missing}; use --no-drop-dstream-metadata to retain",
        )

    for col in ("id", "ancestor_id"):
        if col not in columns:
            raise ValueError(
                f"alifestd_validate_trie: missing required column '{col}'",
            )

    logging.info("alifestd_validate_trie: counting tips...")
    # a tip is a node whose id does not appear as ancestor_id of another node
    non_root_ancestor_ids = (
        df.lazy()
        .filter(pl.col("ancestor_id") != pl.col("id"))
        .select(pl.col("ancestor_id").alias("id"))
        .unique()
    )
    num_tips = (
        df.lazy()
        .join(non_root_ancestor_ids, on="id", how="anti")
        .select(pl.len())
        .collect()
        .item()
    )
    logging.info(f"alifestd_validate_trie: {num_tips} tips")

    logging.info("alifestd_validate_trie: checking contiguous ids...")
    if not alifestd_has_contiguous_ids_polars(df):
        raise ValueError(
            "alifestd_validate_trie: ids are not contiguous",
        )

    logging.info("alifestd_validate_trie: checking topological sort...")
    if not alifestd_is_topologically_sorted_polars(df):
        raise ValueError(
            "alifestd_validate_trie: data is not topologically sorted",
        )

    logging.info("alifestd_validate_trie: validation passed")
    return df
