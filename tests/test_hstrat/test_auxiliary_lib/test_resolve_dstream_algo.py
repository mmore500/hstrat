from downstream import dstream

from hstrat._auxiliary_lib import resolve_dstream_algo


def test_resolve_dstream_algo():
    assert resolve_dstream_algo("dstream.steady_algo") is dstream.steady_algo
    assert resolve_dstream_algo("dstream.tilted_algo") is dstream.tilted_algo
    assert resolve_dstream_algo(dstream.steady_algo) is dstream.steady_algo
