import contextlib
import logging
import math
import random
import typing

from downstream import dstream
import more_itertools as mit
import numpy as np
import opytional as opyt
import polars as pl

from .._auxiliary_lib import (
    RngStateContext,
    alifestd_has_contiguous_ids_polars,
    alifestd_is_topologically_sorted_polars,
    get_sole_scalar_value_polars,
)
from .._auxiliary_lib._alifestd_find_leaf_ids import (
    _alifestd_find_leaf_ids_asexual_fast_path,
)
from .._auxiliary_lib._alifestd_find_pair_mrca_id_asexual import (
    _alifestd_find_pair_mrca_id_asexual_fast_path,
)
from ..genome_instrumentation import HereditaryStratigraphicSurface
from ..juxtaposition import calc_rank_of_first_retained_disparity_between
from ..serialization import surf_from_hex

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


def _load_surface(
    phylo_df: pl.DataFrame,
    leaf_id: int,
) -> HereditaryStratigraphicSurface:
    row = (
        phylo_df.lazy()
        .filter(pl.col("id") == leaf_id)
        .collect()
        .row(0, named=True)
    )
    return surf_from_hex(
        hex_string=row["data_hex"],
        dstream_algo=eval(row["dstream_algo"], {"dstream": dstream}),
        dstream_S=row["dstream_S"],
        dstream_storage_bitoffset=row["dstream_storage_bitoffset"],
        dstream_storage_bitwidth=row["dstream_storage_bitwidth"],
        dstream_T_bitoffset=row["dstream_T_bitoffset"],
        dstream_T_bitwidth=row["dstream_T_bitwidth"],
    )


def surface_validate_trie(
    df: pl.DataFrame,
    max_num_checks: int = 1_000,
    max_violations: int = 0,
    progress_wrap: typing.Callable = lambda x: x,
    seed: typing.Optional[int] = None,
) -> int:
    """Validate trie reconstruction output data.

    Performs structural checks and pairwise leaf-node validation to confirm
    that reconstructed trie correctly reflects common differentia among source
    hereditary stratigraphic surfaces.

    Checks performed:

    1. Required dstream/downstream columns for surface deserialization from
       ``data_hex`` are present.
    2. The ``id`` and ``ancestor_id`` columns are present.
    3. Taxon ids are contiguous (i.e., match row indices 0, 1, ..., n-1).
    4. Data is topologically sorted (each ancestor appears before all its
       descendants).
    5. Samples random leaf-node pairs and compares each pair's first retained
       disparity rank (computed from deserialized surfaces) to the MRCA
       node's ``dstream_rank - dstream_S`` in the trie (converting from raw
       dstream T space to hstrat rank space). A violation occurs when
       ``first_disparity_rank < mrca_rank``: the surfaces prove divergence
       earlier than the trie records.

    Parameters
    ----------
    df : pl.DataFrame
        Trie reconstruction output, as produced by
        ``surface_unpack_reconstruct`` with ``--no-drop-dstream-metadata``.

        Required schema:
            - 'id' : integer
                Unique identifier for each taxon (RE alife standard).
            - 'ancestor_id' : integer
                Unique identifier for ancestor taxon (RE alife standard).
            - 'dstream_rank' : integer
                Rank stored at this node (generation count).
            - 'data_hex' : string
                Raw genome data as a hexadecimal string.
            - 'dstream_algo' : string or categorical
                Name of downstream curation algorithm
                (e.g., ``'dstream.steady_algo'``).
            - 'dstream_storage_bitoffset' : integer
                Bit offset of the dstream buffer field in ``data_hex``.
            - 'dstream_storage_bitwidth' : integer
                Bit width of the dstream buffer field in ``data_hex``.
            - 'dstream_T_bitoffset' : integer
                Bit offset of the dstream counter ("rank") field in
                ``data_hex``.
            - 'dstream_T_bitwidth' : integer
                Bit width of the dstream counter field in ``data_hex``.
            - 'dstream_S' : integer
                Capacity of the dstream buffer (number of differentia stored
                per annotation).

    max_num_checks : int (default 1_000)
        Maximum number of leaf-pair comparisons to perform. Pairs are sampled
        randomly without replacement from all possible pairs.
    max_violations : int (default 1)
        Maximum number of MRCA-rank violations tolerated before returning
        early. Callers should treat a return value exceeding this
        threshold as a validation failure.
    progress_wrap : callable, optional
        Wrapper applied to the pair-check iterator, e.g., ``tqdm.tqdm`` for a
        progress bar. Must accept and return an iterable. Default is the
        identity function (no wrapping).
    seed : int, default None
        Random seed used when sampling leaf pairs.

    Returns
    -------
    int
        Number of leaf-pair violations detected. Returns early (possibly
        before all ``max_num_checks`` pairs have been checked) once
        ``max_violations`` is exceeded.

    Raises
    ------
    ValueError
        If any required column is missing, ids are not contiguous, or data is
        not topologically sorted.

    See Also
    --------
    surface_unpack_reconstruct :
        Produces trie reconstruction data to be validated here.
    """
    columns = set(df.lazy().collect_schema().names())

    logging.info("surface_validate_trie: checking required columns...")
    missing = sorted(set(_deserialization_columns) - columns)
    if missing:
        raise ValueError(
            "surface_validate_trie: missing downstream metadata columns "
            f"{missing}; use --no-drop-dstream-metadata to retain",
        )

    for col in ("id", "ancestor_id"):
        if col not in columns:
            raise ValueError(
                f"surface_validate_trie: missing required column '{col}'",
            )

    logging.info("surface_validate_trie: checking contiguous ids...")
    # required by _alifestd_find_leaf_ids_asexual_fast_path
    # and _alifestd_find_pair_mrca_id_asexual_fast_path
    if not alifestd_has_contiguous_ids_polars(df):
        raise ValueError(
            "surface_validate_trie: ids are not contiguous",
        )

    logging.info("surface_validate_trie: checking topological sort...")
    # required by _alifestd_find_leaf_ids_asexual_fast_path
    # and _alifestd_find_pair_mrca_id_asexual_fast_path
    if not alifestd_is_topologically_sorted_polars(df):
        raise ValueError(
            "surface_validate_trie: data is not topologically sorted",
        )

    logging.info("surface_validate_trie: collecting ancestor ids...")
    ancestor_ids = (
        df.lazy()
        .select(pl.col("ancestor_id"))
        .collect()
        .to_series()
        .to_numpy()
        .astype(np.int64)
    )
    logging.info(
        f"surface_validate_trie: collected {len(ancestor_ids)=}",
    )

    logging.info("surface_validate_trie: finding leaf ids...")
    leaf_ids = _alifestd_find_leaf_ids_asexual_fast_path(ancestor_ids)
    logging.info(f"surface_validate_trie: found {len(leaf_ids)=}")

    num_combinations = math.comb(len(leaf_ids), 2)
    num_checks = min(max_num_checks, num_combinations)
    logging.info(
        "surface_validate_trie: "
        f"shuffling target order for {num_checks=} of "
        f"{num_combinations=} leaf-pair checks...",
    )
    with opyt.apply_if_or_else(seed, RngStateContext, contextlib.nullcontext):
        combo_indices = random.sample(range(num_combinations), num_checks)

    logging.info("surface_validate_trie: collecting dstream_S value...")
    dstream_S = get_sole_scalar_value_polars(df, "dstream_S")

    logging.info("surface_validate_trie: checking for violations...")
    num_violations = 0
    for leaf_a, leaf_b in progress_wrap(
        mit.nth_combination(leaf_ids, 2, i) for i in combo_indices
    ):
        surface_a = _load_surface(df, leaf_a)
        surface_b = _load_surface(df, leaf_b)
        first_disparity_rank = calc_rank_of_first_retained_disparity_between(
            surface_a,
            surface_b,
            confidence_level=0.49,  # threshold for single-bit mismatch
        )

        # if None, no disparity was found --- surfaces are compatible up
        # to min(leaf_a, leaf_b) dstream_rank; use that as the bound
        mrca_rank_bound = opyt.or_else(
            first_disparity_rank,
            lambda: min(
                df.lazy()
                .filter(pl.col("id") == leaf_a)
                .select(pl.col("dstream_rank"))
                .collect()
                .item(),
                df.lazy()
                .filter(pl.col("id") == leaf_b)
                .select(pl.col("dstream_rank"))
                .collect()
                .item(),
            )
            - dstream_S,  # dstream rank --> hstrat rank
        )
        assert mrca_rank_bound >= 0

        mrca_id = _alifestd_find_pair_mrca_id_asexual_fast_path(
            ancestor_ids, leaf_a, leaf_b
        )

        trie_mrca_rank = (
            max(
                df.lazy()
                .filter(pl.col("id") == mrca_id)
                .select(pl.col("dstream_rank"))
                .collect()
                .item(),
                dstream_S,
            )
            - dstream_S
        )  # dstream rank --> hstrat rank
        assert trie_mrca_rank >= 0

        # violation: surfaces prove divergence no later than
        # first_disparity_rank, which precedes mrca_rank — trie places
        # MRCA more recently than the surface data allows
        is_violation = trie_mrca_rank >= mrca_rank_bound + (
            mrca_rank_bound == 0  # @mmore500: uncertain about this edge case
        )
        if is_violation:
            leaf_a_rank = (
                df.lazy()
                .filter(pl.col("id") == leaf_a)
                .select(pl.col("dstream_rank"))
                .collect()
                .item()
            ) - dstream_S
            leaf_b_rank = (
                df.lazy()
                .filter(pl.col("id") == leaf_b)
                .select(pl.col("dstream_rank"))
                .collect()
                .item()
            ) - dstream_S
            logging.info(
                "\n"
                "===========================================================\n"
                f"surface_validate_trie: violation found for leaf pair "
                f"({leaf_a}, {leaf_b}):\n"
                "-----------------------------------------------------------\n"
                f"    delta={mrca_rank_bound - trie_mrca_rank}\n"
                f"    {trie_mrca_rank=}\n"
                f"    {mrca_rank_bound=}\n"
                f"    {first_disparity_rank=}\n"
                f"    {leaf_a_rank=} {leaf_b_rank=}\n"
                "===========================================================",
            )
        num_violations += is_violation
        if num_violations > max_violations:
            logging.info(
                "surface_validate_trie: "
                f"stopping with more than {max_violations=} found",
            )
            return num_violations

    logging.info(
        "surface_validate_trie: "
        f"{num_checks=} completed with {num_violations=} found",
    )
    return num_violations
