import contextlib
import logging
import math
import multiprocessing
import os
import pathlib
import typing
import uuid

from downstream import dataframe as dstream_dataframe
import pandas as pd
import polars as pl
import pyarrow as pa
import tqdm

from .._auxiliary_lib import (
    alifestd_make_empty,
    get_sole_scalar_value_polars,
    give_len,
    log_context_duration,
    log_memory_usage,
    render_polars_snapshot,
)
from ..phylogenetic_inference.tree._impl._build_tree_searchtable_cpp_impl_stub import (
    Records,
    check_trie_invariant_ancestor_bounds,
    check_trie_invariant_chronologically_sorted,
    check_trie_invariant_contiguous_ids,
    check_trie_invariant_data_nodes_are_leaves,
    check_trie_invariant_no_indistinguishable_nodes,
    check_trie_invariant_ranks_nonnegative,
    check_trie_invariant_root_at_zero,
    check_trie_invariant_search_children_sorted,
    check_trie_invariant_search_children_valid,
    check_trie_invariant_search_lineage_compatible,
    check_trie_invariant_single_root,
    check_trie_invariant_topologically_sorted,
    collapse_unifurcations,
    copy_records_to_dict,
    diagnose_trie_invariant_ancestor_bounds,
    diagnose_trie_invariant_chronologically_sorted,
    diagnose_trie_invariant_contiguous_ids,
    diagnose_trie_invariant_data_nodes_are_leaves,
    diagnose_trie_invariant_no_indistinguishable_nodes,
    diagnose_trie_invariant_ranks_nonnegative,
    diagnose_trie_invariant_root_at_zero,
    diagnose_trie_invariant_search_children_sorted,
    diagnose_trie_invariant_search_children_valid,
    diagnose_trie_invariant_search_lineage_compatible,
    diagnose_trie_invariant_single_root,
    diagnose_trie_invariant_topologically_sorted,
    extend_tree_searchtable_cpp_from_exploded,
    extract_records_to_dict,
)


def _sort_Tbar_argv(
    long_df: pl.DataFrame,
    num_slices: int,
    slice_index: int,
) -> pl.DataFrame:
    """Fast chronological sort within dstream data id groups, when Tbar_argv
    is available."""
    with log_context_duration(
        f"gather_indices ({slice_index + 1}/{num_slices})",
        logging.info,
    ):
        gather_indices = (  # argsort: what index should this row be sorted to?
            long_df.select(
                gather_indices=pl.when(  # where do data id's transition?
                    pl.col("dstream_data_id").shift(
                        fill_value=long_df["dstream_data_id"].first() + 1,
                    )
                    != pl.col("dstream_data_id")
                )
                .then(pl.int_range(len(long_df)))  # mark transition indices
                .otherwise(None)
                .forward_fill()  # fill first index across entire data id group
                .add(pl.col("dstream_Tbar_argv")),  # add Tbar_argv offset
            )
            .to_series()
            .to_numpy()
        )

    with log_context_duration(
        f".gather(gather_indices) ({slice_index + 1}/{num_slices})",
        logging.info,
    ):
        long_df = long_df.select(  # apply argsort
            pl.col(
                "dstream_data_id",
                "dstream_T",
                "dstream_Tbar",
                "dstream_value",
            ).gather(gather_indices),
        )

    return long_df


def _sort_Tbar(
    long_df: pl.DataFrame,
    num_slices: int,
    slice_index: int,
) -> pl.DataFrame:
    """Fallback chronological sort within dstream data id groups, when
    Tbar_argv is not available."""
    with log_context_duration(
        '.sort_by("dstream_Tbar").over(partition_by="dstream_data_id") '
        f"({slice_index + 1}/{num_slices})",
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

    return long_df


def _make_exploded_slice(
    df_slice: pl.DataFrame,
    num_slices: int,
    slice_index: int,
) -> pl.DataFrame:
    """Explode dstream buffers to 1 differentia per row, calculating Tbar for
    each and ensuring strata are chronological within data id groups."""

    # explode dstream buffer to 1 differentia per row, calculating Tbar for each
    with log_context_duration(
        "dstream.dataframe.explode_lookup_unpacked "
        f"({slice_index + 1}/{num_slices})",
        logging.info,
    ):
        long_df = dstream_dataframe.explode_lookup_unpacked(
            df_slice, calc_Tbar_argv=True, value_type="uint64"
        )

    # ensure strata are chronological within data id groups
    # (i.e., within groups of differentia from same buffer)
    long_df = [  # dispatch to sort method based on available columns
        _sort_Tbar,
        _sort_Tbar_argv,
    ]["dstream_Tbar_argv" in long_df.columns](
        long_df=long_df,
        num_slices=num_slices,
        slice_index=slice_index,
    )

    if slice_index == 0:
        render_polars_snapshot(long_df, "exploded", logging.info)

    return long_df


def _prepare_df_for_explosion(
    df: typing.Union[pl.DataFrame, pl.LazyFrame],
    exploded_slice_size: int,
) -> typing.Tuple[pl.DataFrame, int]:
    """Unpack, sort, and prepare DataFrame for slice-wise explosion.

    Returns prepared DataFrame and the number of slices.
    """
    with log_context_duration(
        "dstream.dataframe.unpack_data_packed", logging.info
    ):
        df = dstream_dataframe.unpack_data_packed(df)

    render_polars_snapshot(df, "unpacked", logging.info)

    # ensure genomes sorted by generations elapsed in ascending order
    # AFTER dstream_T has been unpacked, but before exploded
    with log_context_duration('.sort("dstream_T")', logging.info):
        df = df.sort("dstream_T", descending=False, maintain_order=True)

    render_polars_snapshot(df, "sorted", logging.info)

    if "dstream_data_id" not in df.columns:
        logging.info(" - adding dstream_data_id column")
        # ensure chunking doesn't affect data ids
        df = df.with_row_index("dstream_data_id")

    num_slices = math.ceil(len(df) / exploded_slice_size)
    logging.info(f"{len(df)=} {exploded_slice_size=} {num_slices=}")

    return df, num_slices


_pool_worker_df: typing.Optional[pl.DataFrame] = None


def _pool_worker_initializer(df_path: str) -> None:
    """Pool worker initializer: read prepared df from Arrow file once."""
    global _pool_worker_df
    _pool_worker_df = pl.read_ipc(df_path, memory_map=False)


def _explode_and_write_slice(
    args: typing.Tuple[slice, int, int],
) -> str:
    """Explode a single slice and write result to a temporary Arrow file.

    Receives a ``slice`` object and metadata as a lightweight task
    descriptor.  The prepared DataFrame is accessed via the module-level
    global set by ``_pool_worker_initializer``, avoiding repeated
    serialisation of the full frame.
    """
    row_slice, num_slices, slice_index = args
    logging.info(f"- worker exploding slice {slice_index + 1} / {num_slices}")
    df_slice = _pool_worker_df[row_slice]
    # apply explode transformation
    long_df = _make_exploded_slice(
        df_slice=df_slice,
        num_slices=num_slices,
        slice_index=slice_index,
    )

    # pass exploded data to consumer through queue via tmpfile
    # (better performing for fast read than passing directly through queue)
    logging.info("- worker putting exploded data")
    outpath = f"/tmp/{uuid.uuid4()}.arrow"  # nosec B108
    long_df.select(pl.all().shrink_dtype()).write_ipc(
        outpath, compression="uncompressed"
    )
    del long_df  # clear memory
    return outpath


def _produce_exploded_slices(
    queue: multiprocessing.JoinableQueue,
    df: typing.Union[pl.DataFrame, pl.LazyFrame],
    exploded_slice_size: int,
) -> None:
    """Exploded DataFrame in chunks, passed to queue for consumption."""
    df, num_slices = _prepare_df_for_explosion(df, exploded_slice_size)

    for slice_idx, df_slice in enumerate(df.iter_slices(exploded_slice_size)):
        logging.info(
            f"- worker exploding slice {slice_idx + 1} / {num_slices}"
        )
        long_df = _make_exploded_slice(
            df_slice=df_slice,
            num_slices=num_slices,
            slice_index=slice_idx,
        )

        logging.info("- worker putting exploded data")
        outpath = f"/tmp/{uuid.uuid4()}.arrow"  # nosec B108
        long_df.select(pl.all().shrink_dtype()).write_ipc(
            outpath, compression="uncompressed"
        )
        del long_df
        queue.put(outpath)
        logging.info("- worker waiting for consumption")
        queue.join()  # wait for produced item to be consumed
        logging.info("- worker wait complete")

    logging.info("- worker putting sentinel value to signal completion")
    queue.put(None)  # send sentinel value to signal completion
    logging.info(" - worker complete")


def _dump_records(records: Records) -> str:
    """Dump records to a parquet file and return the file path."""
    records_df = pl.DataFrame(copy_records_to_dict(records))
    render_polars_snapshot(records_df, "dumped records", display=logging.error)
    for dump_path in (
        pathlib.Path.home() / f"hstrat_trie_records_{uuid.uuid4()}.pqt",
        f"/tmp/hstrat_trie_records_{uuid.uuid4()}.pqt",  # nosec B108
    ):
        try:
            records_df.write_parquet(dump_path)
            logging.error(f"records dumped to {dump_path}")
            return str(dump_path)
        except Exception as e:
            logging.error(f"failed to dump records to {dump_path}: {e}")


def _run_trie_invariant_checks(records: Records, context: str) -> None:
    """Run all trie invariant checks, raising AssertionError on failure.

    On failure, logs diagnostic information from the corresponding
    ``diagnose_trie_invariant_*`` function, dumps the records to a file,
    and raises ``AssertionError``.

    Uses explicit ``raise AssertionError(...)`` rather than ``assert`` so
    checks are not stripped in optimized mode (``python -O``).
    """
    _checks = [
        (
            "contiguous_ids",
            check_trie_invariant_contiguous_ids,
            diagnose_trie_invariant_contiguous_ids,
        ),
        (
            "topologically_sorted",
            check_trie_invariant_topologically_sorted,
            diagnose_trie_invariant_topologically_sorted,
        ),
        (
            "chronologically_sorted",
            check_trie_invariant_chronologically_sorted,
            diagnose_trie_invariant_chronologically_sorted,
        ),
        (
            "single_root",
            check_trie_invariant_single_root,
            diagnose_trie_invariant_single_root,
        ),
        (
            "search_children_valid",
            check_trie_invariant_search_children_valid,
            diagnose_trie_invariant_search_children_valid,
        ),
        (
            "search_children_sorted",
            check_trie_invariant_search_children_sorted,
            diagnose_trie_invariant_search_children_sorted,
        ),
        (
            "no_indistinguishable_nodes",
            check_trie_invariant_no_indistinguishable_nodes,
            diagnose_trie_invariant_no_indistinguishable_nodes,
        ),
        (
            "data_nodes_are_leaves",
            check_trie_invariant_data_nodes_are_leaves,
            diagnose_trie_invariant_data_nodes_are_leaves,
        ),
        (
            "search_lineage_compatible",
            check_trie_invariant_search_lineage_compatible,
            diagnose_trie_invariant_search_lineage_compatible,
        ),
        (
            "ancestor_bounds",
            check_trie_invariant_ancestor_bounds,
            diagnose_trie_invariant_ancestor_bounds,
        ),
        (
            "root_at_zero",
            check_trie_invariant_root_at_zero,
            diagnose_trie_invariant_root_at_zero,
        ),
        (
            "nonroot_ranks_positive",
            check_trie_invariant_ranks_nonnegative,
            diagnose_trie_invariant_ranks_nonnegative,
        ),
    ]
    for i, (name, check_fn, diagnose_fn) in enumerate(_checks, 1):
        logging.info(
            f"checking trie invariant {i} of {len(_checks)}: "
            f"{name} ({context})...",
        )
        if not check_fn(records):
            diagnostic = diagnose_fn(records)
            logging.error(
                f"trie invariant check failed: {name} ({context})\n"
                f"{diagnostic}",
            )
            dump_path = _dump_records(records)
            raise AssertionError(
                f"Trie invariant check failed: {name} ({context})\n"
                f"{diagnostic}\n"
                f"Records dumped to: {dump_path}"
            )
    logging.info(f"all trie invariant checks passed ({context})")


def _build_records_chunked(
    slices: typing.Iterator[str],
    collapse_unif_freq: int,
    check_trie_invariant_freq: int,
    check_trie_invariant_after_collapse_unif: bool,
    dstream_S: int,
    exploded_slice_size: int,
    pa_source_type: str,
) -> Records:
    """Build tree searchtable from DataFrame, exploding in chunks to reduce
    memory usage."""
    init_size = exploded_slice_size * dstream_S * 2
    logging.info(f"{init_size=}")
    records = Records(init_size)  # handle for C++ tree-building data

    logging.info("consuming from exploded df worker")
    for i, inpath in enumerate(slices):
        logging.info(
            f"taking exploded df off queue ({i + 1} / {len(slices)})...",
        )

        logging.info(
            f"opening slice ({i + 1} / {len(slices)}) from {inpath} "
            f" using {pa_source_type=}...",
        )
        with getattr(pa, pa_source_type)(inpath, "rb") as source:
            with log_context_duration(
                "pa.ipc.open_file(source).read_all()",
                logging.info,
            ):
                pa_array = pa.ipc.open_file(source).read_all()

            np_array = {
                "dstream_data_id": None,
                "dstream_T": None,
                "dstream_Tbar": None,
                "dstream_value": None,
            }
            for col in np_array:
                with log_context_duration(
                    f"pa_array['{col}'].to_numpy()",
                    logging.info,
                ):
                    np_array[col] = pa_array[col].to_numpy()

            logging.info(f"incorporating slice ({i + 1} / {len(slices)})...")

            with log_context_duration(
                "extend_tree_searchtable_cpp_from_exploded "
                f"({i + 1} / {len(slices)})",
                logging.info,
            ):
                # dispatch to C++ tree-building implementation
                extend_tree_searchtable_cpp_from_exploded(
                    records,
                    np_array["dstream_data_id"],
                    np_array["dstream_T"],
                    np_array["dstream_Tbar"],
                    np_array["dstream_value"],
                    tqdm.tqdm,
                )

        logging.info(f"unlinking slice {i + 1} / {len(slices)}...")
        os.unlink(inpath)

        if (
            check_trie_invariant_freq > 0
            and (i + 1) % check_trie_invariant_freq == 0
        ):
            with log_context_duration(
                "_run_trie_invariant_checks "
                f"(before collapse, slice {i + 1} / {len(slices)})",
                logging.info,
            ):
                _run_trie_invariant_checks(
                    records,
                    f"before collapse, after slice {i + 1} / {len(slices)}",
                )

        if collapse_unif_freq > 0 and (i + 1) % collapse_unif_freq == 0:
            with log_context_duration(
                "collapse_unifurcations(dropped_only=True) "
                f"({i + 1} / {len(slices)})",
                logging.info,
            ):
                records = collapse_unifurcations(records, dropped_only=True)

        if (
            check_trie_invariant_after_collapse_unif
            and check_trie_invariant_freq > 0
            and (i + 1) % check_trie_invariant_freq == 0
        ):
            with log_context_duration(
                "_run_trie_invariant_checks "
                f"(after collapse, slice {i + 1} / {len(slices)})",
                logging.info,
            ):
                _run_trie_invariant_checks(
                    records,
                    f"after collapse, after slice {i + 1} / {len(slices)}",
                )

        log_memory_usage(logging.info)

    logging.info("slices complete")

    # redundant w/ below (just here for testing)
    if collapse_unif_freq == -1:
        with log_context_duration(
            "collapse_unifurcations(dropped_only=True) (finalize)",
            logging.info,
        ):
            records = collapse_unifurcations(records, dropped_only=True)

    # collapse all unifs, to reduce subsequent memory pressure
    with log_context_duration(
        "collapse_unifurcations(dropped_only=False)",
        logging.info,
    ):
        records = collapse_unifurcations(records, dropped_only=False)

    log_memory_usage(logging.info)

    return records


def _join_user_defined_columns(
    df: pl.DataFrame,
    phylo_df: pl.DataFrame,
    drop_dstream_metadata: typing.Optional[bool],
) -> pl.DataFrame:
    """Join user-defined columns from input data onto reconstructed tree
    dataframe."""
    if drop_dstream_metadata is None:  # default behavior
        df = df.select(
            pl.exclude("^dstream_.*$", "^downstream_.*$"),
            pl.col("dstream_data_id").cast(pl.UInt64),
        )
    elif bool(drop_dstream_metadata):
        raise NotImplementedError(
            "explicit --drop-dstream-metadata is not yet supported"
        )
    else:
        df = df.with_columns(
            pl.col("dstream_data_id").cast(pl.UInt64),
        )
    joined_columns = {*df.lazy().collect_schema().names()} - {
        *phylo_df.lazy().collect_schema().names()
    }
    if joined_columns:
        logging.info(f" - {len(joined_columns)} column(s) to join")
        logging.info(f" - joining columns: {[*joined_columns]}")
        phylo_df = phylo_df.join(
            df.lazy().collect(), on="dstream_data_id", how="left"
        )
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
        .rename({"rank": "dstream_rank"})
    )


def _surface_unpacked_reconstruct(
    slices: typing.Iterator[str],
    *,
    collapse_unif_freq: int,
    check_trie_invariant_freq: int,
    check_trie_invariant_after_collapse_unif: bool,
    differentia_bitwidth: int,
    dstream_S: int,
    exploded_slice_size: int,
    pa_source_type: str,
) -> pl.DataFrame:
    """Reconstruct phylogenetic tree from unpacked dstream data."""
    logging.info("building tree searchtable chunkwise...")
    records = _build_records_chunked(
        slices,
        collapse_unif_freq=collapse_unif_freq,
        check_trie_invariant_freq=check_trie_invariant_freq,
        check_trie_invariant_after_collapse_unif=check_trie_invariant_after_collapse_unif,
        dstream_S=dstream_S,
        exploded_slice_size=exploded_slice_size,
        pa_source_type=pa_source_type,
    )

    with log_context_duration("_construct_result_dataframe", logging.info):
        phylo_df = _construct_result_dataframe(
            records,
            differentia_bitwidth=differentia_bitwidth,
            dstream_S=dstream_S,
        )

    del records  # clear memory
    render_polars_snapshot(phylo_df, "converted", logging.info)

    logging.info("surface_unpack_reconstruct complete")
    render_polars_snapshot(phylo_df, "reconstruction", logging.info)

    return phylo_df


@contextlib.contextmanager
def _generate_exploded_slices_mp(
    df: typing.Union[pl.LazyFrame, pl.DataFrame],
    exploded_slice_size: int,
    mp_context: str,
    mp_pool_size: int = 1,
) -> typing.Iterator[typing.Iterator[str]]:
    """Generator wrapping generation of exploded data frame slices via
    parallel multiprocess producer(s)."""
    try:  # RE https://docs.pola.rs/user-guide/misc/multiprocessing/
        logging.info(f"attempting to use multiprocessing {mp_context} context")
        mp_context = multiprocessing.get_context(mp_context)
    except ValueError:  # forkserver available on unix only
        logging.info("attempting to use multiprocessing spawn context")
        mp_context = multiprocessing.get_context("spawn")

    if mp_pool_size <= 1:
        logging.info("creating work queue")
        queue = mp_context.JoinableQueue()

        logging.info("spawning exploded df worker")
        producer = mp_context.Process(
            target=_produce_exploded_slices,
            args=(
                queue,
                df,
                exploded_slice_size,
            ),  # lazyframe is cheap to send
        )
        logging.info("starting exploded df worker")
        producer.start()

        num_slices = (
            df.lazy().select(pl.len()).collect().item()
            + (exploded_slice_size - 1)
        ) // exploded_slice_size

        yield give_len(  # enable len() on generator for nice logging
            # yield generated slices until sentinel value None is received,
            # immediately marking items as consumed (`task_done`) to trigger
            # the next item to be produced if queue has been emptied
            iter(lambda: (queue.get(), queue.task_done())[0], None),
            num_slices,
        )

        producer.join()  # wait for producer to finish (no effect, but good form)
    else:
        logging.info(f"using multiprocessing pool with {mp_pool_size} workers")
        df, num_slices = _prepare_df_for_explosion(df, exploded_slice_size)

        # write prepared df to temp file so workers can read it
        # without pickling the dataframe through initargs
        df_path = f"/tmp/{uuid.uuid4()}_prepared.arrow"  # nosec B108
        df.write_ipc(df_path, compression="uncompressed")
        n = len(df)
        del df

        def _slice_tasks():
            for i in range(num_slices):
                start = i * exploded_slice_size
                end = min(start + exploded_slice_size, n)
                yield (slice(start, end), num_slices, i)

        pool = mp_context.Pool(
            processes=mp_pool_size,
            initializer=_pool_worker_initializer,
            initargs=(df_path,),
        )
        try:
            yield give_len(
                pool.imap(_explode_and_write_slice, _slice_tasks()),
                num_slices,
            )
        finally:
            pool.close()
            pool.join()
            os.unlink(df_path)


def surface_unpack_reconstruct(
    df: typing.Union[pl.DataFrame, pl.LazyFrame],
    *,
    collapse_unif_freq: int = 1,
    check_trie_invariant_freq: int = 0,
    check_trie_invariant_after_collapse_unif: bool = False,
    drop_dstream_metadata: typing.Optional[bool] = None,
    exploded_slice_size: int = 1_000_000,
    mp_context: str = "spawn",
    mp_pool_size: int = 1,
    pa_source_type: str = "memory_map",
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

    check_trie_invariant_freq : int, default 0
        Frequency of trie invariant checks, in number of slices.

        Set to 0 to disable (default).
        Set to n > 0 to check every n slices.

    drop_dstream_metadata : bool or None, default None
        Should dstream/downstream columns be dropped from the output?

        - If None, some dstream/downstream columns are dropped
          (default behavior).
        - If False, dstream/downstream columns are retained in the output.
        - If True, raises NotImplementedError (not yet supported).

    exploded_slice_size : int, default 1_000_000
        Number of rows to process at once. Lower values reduce memory usage.

    mp_context : str, default 'spawn'
        Multiprocessing context to use for parallel processing.

    mp_pool_size : int, default 1
        Number of worker processes for exploding slices in parallel.

        When 1, a single producer process is used (original behavior).
        When greater than 1, a multiprocessing pool is used with ordered
        results via ``Pool.imap``.

    pa_source_type : str, default 'memory_map'
        PyArrow type to use for exploded chunks (i.e., "memory_map" or
        "OSFile").

    Returns
    -------
    pl.DataFrame
        The output DataFrame containing the estimated phylogenetic tree in
        alife standard format, with the following columns:

        - 'id' : pl.UInt64
            - Unique identifier for each taxon (RE alife standard format).
        - 'ancestor_id' : pl.UInt64
            - Unique identifier for ancestor taxon  (RE alife standard format).
        - 'dstream_rank' : pl.UInt64
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
    logging.info(f"packed {type(df)=}")

    # for simplicity, return early for this special case
    if df.lazy().limit(1).collect().is_empty():
        logging.info("empty input dataframe, returning empty result")
        res = alifestd_make_empty()
        res["taxon_label"] = None
        res["dstream_rank"] = pd.Series(dtype=int)
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

    logging.info("dispatching to surface_unpacked_reconstruct")
    with _generate_exploded_slices_mp(
        df, exploded_slice_size, mp_context, mp_pool_size
    ) as slices:
        phylo_df = _surface_unpacked_reconstruct(
            slices,
            collapse_unif_freq=collapse_unif_freq,
            check_trie_invariant_freq=check_trie_invariant_freq,
            check_trie_invariant_after_collapse_unif=check_trie_invariant_after_collapse_unif,
            differentia_bitwidth=differentia_bitwidth,
            dstream_S=dstream_S,
            exploded_slice_size=exploded_slice_size,
            pa_source_type=pa_source_type,
        )

    logging.info("joining user-defined columns...")
    with log_context_duration("_join_user_defined_columns", logging.info):
        try:
            phylo_df = _join_user_defined_columns(
                df, phylo_df, drop_dstream_metadata
            )
        except pl.exceptions.ColumnNotFoundError:
            phylo_df = _join_user_defined_columns(
                df.with_row_index("dstream_data_id"),
                phylo_df,
                drop_dstream_metadata,
            )

    return phylo_df
