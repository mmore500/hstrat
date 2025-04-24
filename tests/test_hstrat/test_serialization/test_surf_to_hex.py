import types

from downstream import dstream, dsurf
import numpy as np
import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "algo",
    [
        dstream.steady_algo,
        dstream.stretched_algo,
        dstream.tilted_algo,
        dstream.stretchedxtc_algo,
        dstream.tiltedxtc_algo,
        dstream.primed_0pad0_steady_algo,
        dstream.primed_0pad0_stretchedxtc_algo,
        dstream.primed_0pad0_tiltedxtc_algo,
    ],
)
@pytest.mark.parametrize("S", [8, 16, 32, np.zeros(32, dtype=np.uint64)])
@pytest.mark.parametrize("n", [0, 1, 5, 25, 100])
@pytest.mark.parametrize("dstream_T_bitwidth", [32, 64])
@pytest.mark.parametrize(
    "stratum_differentia_bit_width", [1, 2, 4, 8, 16, 32, 64]
)
def test_surf_to_hex_then_from_hex(
    algo: types.ModuleType,
    S: int,
    n: int,
    dstream_T_bitwidth: int,
    stratum_differentia_bit_width: int,
):
    surf = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S),
        predeposit_strata=0,
        stratum_differentia_bit_width=stratum_differentia_bit_width,
    )
    surf.DepositStrata(n)
    assert (
        hstrat.surf_from_hex(
            hstrat.surf_to_hex(surf, dstream_T_bitwidth=dstream_T_bitwidth),
            dstream_algo=algo,
            dstream_T_bitwidth=dstream_T_bitwidth,
            dstream_storage_bitwidth=surf.S
            * surf.GetStratumDifferentiaBitWidth(),
            dstream_S=surf.S,
        )
        == surf
    )
