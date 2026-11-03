from downstream import dstream
import numpy as np
import pytest

from hstrat._auxiliary_lib import iter_dstream_ingest_times_sorted


@pytest.mark.parametrize("chunk_size", [1, 7, 100, 1000])
@pytest.mark.parametrize("algo", [dstream.steady_algo, dstream.tilted_algo])
def test_iter_dstream_ingest_times_sorted(algo, chunk_size: int):
    S = 16
    T = np.random.default_rng(1).integers(S, 500, size=100)
    chunks = [*iter_dstream_ingest_times_sorted(algo, S, T, chunk_size)]
    # chunks cover all rows, with last chunk shorter if uneven
    assert [*range(len(T))] == [
        i for chunk, __ in chunks for i in range(len(T))[chunk]
    ]
    for chunk, ingest_times in chunks:
        assert len(ingest_times) == len(T[chunk])
        for t, row in zip(T[chunk], ingest_times):
            expected = sorted(algo.lookup_ingest_times(S, int(t)))
            assert row.tolist() == expected
