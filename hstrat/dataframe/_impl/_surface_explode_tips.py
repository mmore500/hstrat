import dataclasses
import logging
import typing

import numpy as np
import polars as pl

from ..._auxiliary_lib import (
    get_sole_scalar_value_polars,
    iter_slices,
    log_context_duration,
    log_memory_usage,
)
from ._surface_unpack_reconstruct import (
    _make_exploded_slice,
    _prepare_df_for_explosion,
)


@dataclasses.dataclass
class SurfaceTips:
    """Retained ranks and differentiae of each genome, in CSR layout.

    Ranks are dstream ranks (i.e., `dstream_Tbar`), ascending within each
    tip.
    """

    data_id: np.ndarray  # uint64, dstream_data_id of each tip
    T: np.ndarray  # int64, dstream_T of each tip
    off: np.ndarray  # int64, CSR offsets into ranks/diffs, len(T) + 1
    ranks: np.ndarray  # int64, retained dstream ranks
    diffs: np.ndarray  # uint64, differentia at those ranks
    dstream_S: int
    differentia_bitwidth: int

    def __len__(self: "SurfaceTips") -> int:
        return len(self.T)

    @property
    def p_differentia_collision(self: "SurfaceTips") -> float:
        return 2.0**-self.differentia_bitwidth

    def leaf_origin_times(self: "SurfaceTips") -> np.ndarray:
        """Origin time of each tip, in generations since founding ancestor
        (i.e., `dstream_T - 1 - dstream_S`)."""
        return (self.T - 1 - self.dstream_S).astype(np.float64)

    def tip_of_node(
        self: "SurfaceTips", node_data_id: pl.Series
    ) -> np.ndarray:
        """Index of tip for each node by `dstream_data_id`, -1 if null."""
        order = np.argsort(self.data_id, kind="stable")
        sorted_ids = self.data_id[order]
        has_tip = node_data_id.is_not_null().to_numpy()
        ids = node_data_id.fill_null(0).cast(pl.UInt64).to_numpy()
        pos = np.searchsorted(sorted_ids, ids)
        pos = np.minimum(pos, len(sorted_ids) - 1)
        found = has_tip & (sorted_ids[pos] == ids)
        if not np.array_equal(found, has_tip):
            raise ValueError("node dstream_data_id not among tips")
        return np.where(found, order[pos], -1).astype(np.int64)


def empty_surface_tips() -> SurfaceTips:
    """Tip data for zero genomes."""
    return SurfaceTips(
        data_id=np.zeros(0, dtype=np.uint64),
        T=np.zeros(0, dtype=np.int64),
        off=np.zeros(1, dtype=np.int64),
        ranks=np.zeros(0, dtype=np.int64),
        diffs=np.zeros(0, dtype=np.uint64),
        dstream_S=0,
        differentia_bitwidth=1,
    )


def coalesce_dstream_data_id(df: pl.DataFrame) -> pl.DataFrame:
    """Ensure uint64 `dstream_data_id`, using row number if not provided.

    Matches the identifiers `surface_unpack_reconstruct` assigns.
    """
    return df.with_columns(
        dstream_data_id=pl.coalesce(
            pl.col("^dstream_data_id$"),
            pl.int_range(pl.len(), dtype=pl.UInt64),
        ).cast(pl.UInt64),
    )


def surface_explode_tips(
    df: pl.DataFrame,
    *,
    exploded_slice_size: int = 1_000_000,
    mp_context: str = "spawn",
    mp_pool_size: int = 1,
) -> SurfaceTips:
    """Unpack and explode dstream buffers of genome data, collecting each
    genome's retained ranks and differentiae.

    Parameters
    ----------
    df : pl.DataFrame
        Packed genome data, with schema as for `surface_unpack_reconstruct`
        and a `dstream_data_id` column (see `coalesce_dstream_data_id`).
    exploded_slice_size : int, default 1_000_000
        Number of genomes to explode at once.
    mp_context : str, default 'spawn'
        Multiprocessing context to use for unpacking.
    mp_pool_size : int, default 1
        Number of worker processes for unpacking.

    Returns
    -------
    SurfaceTips
        Tips in ascending `dstream_T` order.
    """
    logging.info("beginning surface_explode_tips")
    dstream_storage_bitwidth = get_sole_scalar_value_polars(
        df, "dstream_storage_bitwidth"
    )
    dstream_S = get_sole_scalar_value_polars(df, "dstream_S")
    if not dstream_storage_bitwidth % dstream_S == 0:
        raise ValueError(
            "dstream_storage_bitwidth must be a multiple of dstream_S, "
            "cannot calculate differentia_bitwidth",
        )
    differentia_bitwidth = dstream_storage_bitwidth // dstream_S

    logging.info(f" - dstream S: {dstream_S}")
    logging.info(f" - differentia bitwidth: {differentia_bitwidth}")

    df = _prepare_df_for_explosion(df, mp_context, mp_pool_size)
    cols = ("dstream_data_id", "dstream_T", "dstream_Tbar", "dstream_value")
    parts = {col: [] for col in cols}
    slices = [*iter_slices(len(df), exploded_slice_size)]
    for i, row_slice in enumerate(slices):
        logging.info(f"exploding slice {i + 1} / {len(slices)}...")
        long_df = _make_exploded_slice(
            df_slice=df[row_slice], row_slice_log=row_slice
        )
        for col in cols:
            parts[col].append(long_df[col].to_numpy())
        del long_df
        log_memory_usage(logging.info)

    with log_context_duration("assembling tip arrays", logging.info):
        data_id, T, Tbar, value = (
            np.concatenate(parts[col]) if parts[col] else np.zeros(0)
            for col in cols
        )
        # explosion keeps each genome's differentia contiguous
        starts = np.flatnonzero(
            np.concatenate([[True], data_id[1:] != data_id[:-1]])
            if len(data_id)
            else np.zeros(0, dtype=bool),
        )
        if len(starts) != len(df):
            raise ValueError(
                "exploded data must group each genome contiguously"
            )
        off = np.append(starts, len(data_id)).astype(np.int64)

    logging.info(
        f"surface_explode_tips complete, {len(starts)} tips "
        f"with {len(data_id)} retained strata",
    )
    return SurfaceTips(
        data_id=data_id[starts].astype(np.uint64),
        T=T[starts].astype(np.int64),
        off=off,
        ranks=Tbar.astype(np.int64),
        diffs=value.astype(np.uint64),
        dstream_S=int(dstream_S),
        differentia_bitwidth=int(differentia_bitwidth),
    )


def tips_cpp_args(tips: SurfaceTips) -> typing.Tuple:
    """Positional tip arguments for `_origin_time_cpp_impl` functions."""
    return (
        tips.T,
        tips.off,
        tips.ranks,
        tips.diffs,
        tips.p_differentia_collision,
        float(tips.dstream_S),
    )
