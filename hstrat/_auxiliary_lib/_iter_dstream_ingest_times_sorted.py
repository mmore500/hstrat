import types
import typing

import numpy as np


def iter_dstream_ingest_times_sorted(
    dstream_algo: types.ModuleType,
    dstream_S: int,
    T: np.ndarray,
    chunk_size: int,
) -> typing.Iterator[typing.Tuple[slice, np.ndarray]]:
    """Yield chunks of rows, and the ingest times retained by `dstream_algo`
    at each row's `T`, sorted ascending, as floats.

    The last chunk is shorter if `chunk_size` does not evenly divide
    `len(T)`. Lookups are made once per unique `T` within each chunk, in
    parallel.
    """
    for begin in range(0, len(T), chunk_size):
        chunk = slice(begin, begin + chunk_size)  # clipped at end of T
        unique_T, inverse = np.unique(T[chunk], return_inverse=True)
        ingest_times = dstream_algo.lookup_ingest_times_batched(
            dstream_S, unique_T.astype(np.uint64), parallel=True
        ).astype(np.float64)[inverse]
        yield chunk, np.sort(ingest_times, axis=1)
