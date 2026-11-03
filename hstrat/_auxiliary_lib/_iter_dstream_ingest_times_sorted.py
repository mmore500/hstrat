import logging
import types
import typing

import numpy as np

from ._log_context_duration import log_context_duration


def iter_dstream_ingest_times_sorted(
    dstream_algo: types.ModuleType,
    dstream_S: int,
    T: np.ndarray,
    chunk_size: int,
    progress_wrap: typing.Callable,
) -> typing.Iterator[typing.Tuple[np.ndarray, np.ndarray]]:
    """Yield chunks of row indices, and the ingest times retained by
    `dstream_algo` at each row's `T`, sorted ascending, as floats.

    Rows are chunked in order of `T`, so that rows with equal `T` share
    chunks, and lookups are made once per unique `T` within each chunk, in
    parallel. So, chunks and the rows within them are not in row order; use
    each chunk's yielded row indices to place results. Chunks together
    cover all rows once; the last chunk is shorter if `chunk_size` does not
    evenly divide `len(T)`.

    Pass tqdm or equivalent as `progress_wrap` to report progress over
    chunks.
    """
    order = np.argsort(T, kind="stable")
    for begin in progress_wrap(range(0, len(T), chunk_size)):
        chunk = order[begin : begin + chunk_size]  # clipped at end of T
        unique_T, inverse = np.unique(T[chunk], return_inverse=True)
        with log_context_duration(
            f"{dstream_algo.__name__}.lookup_ingest_times_batched "
            f"({len(unique_T)} unique T)",
            logging.info,
        ):
            ingest_times = dstream_algo.lookup_ingest_times_batched(
                dstream_S, unique_T.astype(np.uint64), parallel=True
            ).astype(np.float64)[inverse]
        yield chunk, np.sort(ingest_times, axis=1)
