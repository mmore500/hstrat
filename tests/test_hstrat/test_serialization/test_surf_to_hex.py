import types

from downstream import dstream, dsurf
import numpy as np
import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "algo", [dstream.steady_algo, dstream.stretched_algo, dstream.tilted_algo]
)
@pytest.mark.parametrize("S", [8, 16, 32, np.empty(32, dtype=np.uint64)])
@pytest.mark.parametrize("n", [1, 5, 25, 100])
def test_surf_to_hex_then_from_hex(algo: types.ModuleType, S: int, n: int):
    surf = hstrat.HereditaryStratigraphicSurface(dsurf.Surface(algo, S))
    surf.DepositStrata(n)
    assert (
        hstrat.surf_from_hex(
            hstrat.surf_to_hex(surf),
            dstream_algo=algo,
            dstream_T_bitoffset=0,
            dstream_T_bitwidth=32,
            dstream_storage_bitoffset=32,
            dstream_storage_bitwidth=surf.S
            * surf.GetStratumDifferentiaBitWidth(),
            dstream_S=surf.S,
        )
        == surf
    )
