import logging
import math
import multiprocessing
import os
import uuid

from downstream import dataframe as dstream_dataframe
import pandas as pd
import polars as pl
import pyarrow as pa
import tqdm

from .._auxiliary_lib import (
    alifestd_make_empty,
    get_sole_scalar_value_polars,
    log_context_duration,
    log_memory_usage,
    render_polars_snapshot,
)
from ..phylogenetic_inference.tree._impl._build_tree_searchtable_cpp_impl_stub import (
    Records,
    collapse_dropped_unifurcations,
    extend_tree_searchtable_cpp_from_exploded,
    extract_records_to_dict,
)


def _produce_exploded_slices(
    queue: multiprocessing.JoinableQueue,
    df: pl.DataFrame,
    exploded_slice_size: int,
) -> None:
    """Produce exploded DataFrame in chunks."""
    num_slices = math.ceil(len(df) / exploded_slice_size)
    logging.info(f"{len(df)=} {exploded_slice_size=} {num_slices=}")

    for i, df_slice in enumerate(df.iter_slices(exploded_slice_size)):
        with log_context_duration(
            f"dstream.dataframe.explode_lookup_unpacked ({i + 1}/{num_slices})",
            logging.info,
        ):
            long_df = dstream_dataframe.explode_lookup_unpacked(
                df_slice, calc_Tbar_argv=True, value_type="uint64"
            )

        if "dstream_Tbar_argv" in long_df.columns:
            with log_context_duration(
                f"group_offsets ({i + 1}/{num_slices})",
                logging.info,
            ):
                logging.info(" - marking group boundaries")
                gather_indices = (
                    long_df.select(
                        gather_indices=pl.when(
                            pl.col("dstream_data_id").shift(
                                fill_value=long_df["dstream_data_id"].first()
                                + 1,
                            )
                            != pl.col("dstream_data_id")
                        )
                        .then(pl.int_range(len(long_df)))
                        .otherwise(None)
                        .forward_fill()
                        .add(pl.col("dstream_Tbar_argv")),
                    )
                    .to_series()
                    .to_numpy()
                )

            with log_context_duration(
                f".gather(gather_indices) ({i + 1}/{num_slices})",
                logging.info,
            ):
                long_df = long_df.select(
                    pl.col(
                        "dstream_data_id",
                        "dstream_T",
                        "dstream_Tbar",
                        "dstream_value",
                    ).gather(gather_indices),
                )
        else:
            with log_context_duration(
                '.sort_by("dstream_Tbar").over(partition_by="dstream_data_id") '
                f"({i + 1}/{num_slices})",
                logging.info,
            ):
                long_df = long_df.select(
                    pl.col(
                        "dstream_data_id",
                        "dstream_T",
                        "dstream_Tbar",
                        "dstream_value",
                    )
                    .sort_by("dstream_Tbar")
                    .over(partition_by="dstream_data_id"),
                )

        if i == 0:
            render_polars_snapshot(long_df, "exploded", logging.info)

        logging.info("worker putting exploded data")
        outpath = f"/tmp/{uuid.uuid4()}.arrow"
        long_df.select(pl.all().shrink_dtype()).write_ipc(
            outpath, compression="uncompressed"
        )
        del long_df
        queue.put(outpath)
        logging.info("worker waiting for consumption")
        queue.join()  # wait produced item to be consumed

    logging.info("worker putting sentinel value")
    queue.put(None)  # send sentinel value to signal completion
    logging.info("worker complete")


def _build_records_chunked(
    df: pl.DataFrame,
    collapse_unif_freq: int,
    exploded_slice_size: int,
    mp_context: str,
) -> Records:
    """Build tree searchtable from DataFrame, exploding in chunks to reduce
    memory usage."""
    num_slices = math.ceil(len(df) / exploded_slice_size)
    logging.info(f"{len(df)=} {exploded_slice_size=} {num_slices=}")

    init_size = exploded_slice_size * df["dstream_S"].max() * 2
    logging.info(f"{init_size=}")
    records = Records(init_size)

    try:  # RE https://docs.pola.rs/user-guide/misc/multiprocessing/
        logging.info(f"attempting to use multiprocessing {mp_context} context")
        mp_context = multiprocessing.get_context(mp_context)
    except ValueError:  # forkserver available on unix only
        logging.info("attempting to use multiprocessing spawn context")
        mp_context = multiprocessing.get_context("spawn")

    logging.info("creating work queue")
    queue = mp_context.JoinableQueue()
    logging.info("spawning exploded df worker")
    producer = mp_context.Process(
        target=_produce_exploded_slices,
        args=(queue, df, exploded_slice_size),
    )
    logging.info("starting exploded df worker")
    producer.start()
    del df

    logging.info("consuming from exploded df worker")
    for i, inpath in enumerate(iter(queue.get, None)):
        logging.info(f"taking exploded df off queue {i + 1}/{num_slices}...")
        queue.task_done()  # release producer to prepare next exploded df

        logging.info(f"opening slice {i + 1}/{num_slices} from {inpath}...")
        with pa.memory_map(inpath, "rb") as source:
            pa_array = pa.ipc.open_file(source).read_all()

            logging.info(f"incorporating slice {i + 1}/{num_slices}...")
            with log_context_duration(
                f"extend_tree_searchtable_cpp_from_exploded ({i + 1}/{num_slices})",
                logging.info,
            ):
                extend_tree_searchtable_cpp_from_exploded(
                    records,
                    pa_array["dstream_data_id"].to_numpy(),
                    pa_array["dstream_T"].to_numpy(),
                    pa_array["dstream_Tbar"].to_numpy(),
                    pa_array["dstream_value"].to_numpy(),
                    tqdm.tqdm,
                )

        logging.info(f"unlinking slice {i + 1}/{num_slices}...")
        os.unlink(inpath)

        if collapse_unif_freq and (i + 1) % collapse_unif_freq == 0:
            with log_context_duration(
                f"collapse_dropped_unifurcations ({i + 1}/{num_slices})",
                logging.info,
            ):
                records = collapse_dropped_unifurcations(records)

        log_memory_usage(logging.info)

    logging.info("consumer got sentinel value from queue")
    logging.info("joining producer")
    producer.join()
    logging.info("produce joined")

    return records


def _join_user_defined_columns(
    df: pl.DataFrame, phylo_df: pl.DataFrame
) -> pl.DataFrame:
    """Join user-defined columns from input data onto reconstructed tree
    dataframe."""
    df = df.select(
        pl.exclude("^dstream_.*$", "^downstream_.*$"),
        pl.col("dstream_data_id").cast(pl.UInt64),
    )
    joined_columns = set(df.columns) - set(phylo_df.columns)
    if joined_columns:
        logging.info(f" - {len(joined_columns)} column to join")
        logging.info(f" - joining columns: {[*joined_columns]}")
        phylo_df = phylo_df.join(df, on="dstream_data_id", how="left")
    else:
        logging.info(" - no columns to join, skipping")

    return phylo_df


def _construct_result_dataframe(
    records: Records,
    differentia_bitwidth: int,
    dstream_S: int,
) -> pl.DataFrame:
    """Convert tree searchtable records to DataFrame."""
    logging.info("converting records to dict...")
    records_dict = extract_records_to_dict(records)

    logging.info("converting dict to dataframe...")
    schema = {
        "dstream_data_id": pl.UInt64,
        "id": pl.UInt64,
        "ancestor_id": pl.UInt64,
        "rank": pl.UInt64,
    }
    records_dict = {k: records_dict[k] for k in schema}
    return (
        pl.from_dict(
            records_dict,  # type: ignore
            schema=schema,
        )
        .with_columns(
            pl.lit(differentia_bitwidth)
            .alias("hstrat_differentia_bitwidth")
            .cast(pl.UInt32),
            pl.lit(dstream_S).alias("dstream_S").cast(pl.UInt32),
        )
        .rename({"rank": "hstrat_rank"})
    )


def _surface_unpacked_reconstruct(
    df: pl.DataFrame,
    *,
    collapse_unif_freq: int,
    differentia_bitwidth: int,
    dstream_S: int,
    exploded_slice_size: int,
    mp_context: str,
) -> pl.DataFrame:
    """Reconstruct phylogenetic tree from unpacked dstream data."""
    render_polars_snapshot(df, "unpacked", logging.info)

    logging.info("building tree searchtable chunkwise...")
    records = _build_records_chunked(
        df,
        collapse_unif_freq=collapse_unif_freq,
        exploded_slice_size=exploded_slice_size,
        mp_context=mp_context,
    )

    with log_context_duration("_construct_result_dataframe", logging.info):
        phylo_df = _construct_result_dataframe(
            records,
            differentia_bitwidth=differentia_bitwidth,
            dstream_S=dstream_S,
        )

    del records
    render_polars_snapshot(phylo_df, "converted", logging.info)

    logging.info("joining user-defined columns...")
    with log_context_duration("_join_user_defined_columns", logging.info):
        phylo_df = _join_user_defined_columns(df, phylo_df)

    logging.info("surface_unpack_reconstruct complete")
    render_polars_snapshot(phylo_df, "reconstruction", logging.info)

    return phylo_df


def surface_unpack_reconstruct(
    df: pl.DataFrame,
    *,
    collapse_unif_freq: int = 1,
    exploded_slice_size: int = 1_000_000,
    mp_context: str = "spawn",
) -> pl.DataFrame:
    """Unpack dstream buffer and counter from genome data and construct an
    estimated phylogenetic tree for the genomes.

    Parameters
    ----------
    df : pl.DataFrame
        The input DataFrame containing packed data with required columns, one
        row per genome.

        Required schema:
            - 'data_hex' : pl.String
                - Raw genome data, with serialized dstream buffer and counter.
                - Represented as a hexadecimal string.
            - 'dstream_algo' : pl.Categorical
                - Name of downstream curation algorithm used.
                - e.g., 'dstream.steady_algo'
            - 'dstream_storage_bitoffset' : pl.UInt64
                - Position of dstream buffer field in 'data_hex'.
            - 'dstream_storage_bitwidth' : pl.UInt64
                - Size of dstream buffer field in 'data_hex'.
            - 'dstream_T_bitoffset' : pl.UInt64
                - Position of dstream counter field in 'data_hex'.
            - 'dstream_T_bitwidth' : pl.UInt64
                - Size of dstream counter field in 'data_hex'.
            - 'dstream_S' : pl.Uint32
                - Capacity of dstream buffer, in number of data items.

        Optional schema:
            - 'downstream_version' : pl.Categorical
                - Version of downstream library used to curate data items.
            - 'dstream_data_id' : pl.UInt64
                - Unique identifier for each data item.
                - If not provided, row number will be used as identifier.
            - 'downstream_exclude_exploded' : pl.Boolean
                - Should row be dropped after exploding unpacked data?
            - 'downstream_exclude_unpacked' : pl.Boolean
                - Should row be dropped after unpacking packed data?
            - 'downstream_validate_exploded' : pl.String, polars expression
                - Polars expression to validate exploded data.
            - 'downstream_validate_unpacked' : pl.String, polars expression
                - Polars expression to validate unpacked data.

    collapse_unif_freq : int, default 1
        Frequency of unifurcation collapse, in number of slices.

        Set to 0 to disable.

    exploded_slice_size : int, default 1_000_000
        Number of rows to process at once. Lower values reduce memory usage.

    mp_context : str, default 'spawn'
        Multiprocessing context to use for parallel processing.

    Returns
    -------
    pl.DataFrame
        The output DataFrame containing the estimated phylogenetic tree in
        alife standard format, with the following columns:

        - 'id' : pl.UInt64
            - Unique identifier for each taxon (RE alife standard format).
        - 'ancestor_id' : pl.UInt64
            - Unique identifier for ancestor taxon  (RE alife standard format).
        - 'hstrat_rank' : pl.UInt64
            - Num generations elapsed for ancestral differentia.
            - Corresponds to`dstream_Tbar` for inner nodes.
            - Corresponds `dstream_T` - 1 for leaf nodes
        - 'hstrat_differentia_bitwidth' : pl.UInt64
            - Size of annotation differentiae, in bits.
            - Corresponds to `dstream_value_bitwidth`.
        - 'dstream_S' : pl.UInt32
            - Capacity of dstream buffer, in number of data items.
        - 'dstream_data_id' : pl.UInt64
            - Unique identifier for each genome in source dataframe
            - Set to source dataframe row index if not provided.

        User-defined columns, except some prefixed with 'downstream_' or
        'dstream_', will be forwarded from the input DataFrame.

        Note that the alife-standard `ancestor_list` column is not included in
        the output.

    See Also
    --------
    surface_postprocess_trie :
        Post-processes raw phylogeny data, including collapsing superfluous
        internal nodes and estimating taxon origin times.
    alifestd_try_add_ancestor_list_col :
        Adds alife-standard `ancestor_list` column to phylogeny data.
    """
    logging.info("beginning surface_unpack_reconstruct")
    log_memory_usage(logging.info)

    render_polars_snapshot(df, "packed", logging.info)

    # for simplicity, return early for this special case
    if df.lazy().limit(1).collect().is_empty():
        logging.info("empty input dataframe, returning empty result")
        res = alifestd_make_empty()
        res["taxon_label"] = None
        res["hstrat_rank"] = pd.Series(dtype=int)
        res["hstrat_differentia_bitwidth"] = pd.Series(dtype=int)
        res["dstream_S"] = pd.Series(dtype=int)
        return pl.from_pandas(res)

    logging.info("extracting metadata...")
    dstream_storage_bitwidth = get_sole_scalar_value_polars(
        df, "dstream_storage_bitwidth"
    )
    logging.info(f" - dstream storage bitwidth: {dstream_storage_bitwidth}")

    dstream_S = get_sole_scalar_value_polars(df, "dstream_S")
    logging.info(f" - dstream S: {dstream_S}")

    if not dstream_storage_bitwidth % dstream_S == 0:
        raise ValueError(
            "dstream_storage_bitwidth must be a multiple of dstream_S, "
            "cannot calculate differentia_bitwidth",
        )
    differentia_bitwidth = dstream_storage_bitwidth // dstream_S
    logging.info(f" - differentia bitwidth: {differentia_bitwidth}")

    with log_context_duration(
        "dstream.dataframe.unpack_data_packed", logging.info
    ):
        df = dstream_dataframe.unpack_data_packed(df)

    return _surface_unpacked_reconstruct(
        df,
        collapse_unif_freq=collapse_unif_freq,
        differentia_bitwidth=differentia_bitwidth,
        dstream_S=dstream_S,
        exploded_slice_size=exploded_slice_size,
        mp_context=mp_context,
    )
