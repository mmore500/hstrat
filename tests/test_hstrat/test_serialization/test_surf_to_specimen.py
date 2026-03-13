import types

from downstream import dstream, dsurf
import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "algo",
    [
        dstream.steady_algo,
        dstream.stretched_algo,
        dstream.tilted_algo,
    ],
)
@pytest.mark.parametrize("S", [8, 16])
@pytest.mark.parametrize("num_deposits", [0, 1, 5, 25, 100])
@pytest.mark.parametrize("stratum_differentia_bit_width", [1, 8, 64])
def test_surf_to_specimen(
    algo: types.ModuleType,
    S: int,
    num_deposits: int,
    stratum_differentia_bit_width: int,
):
    """Specimen should preserve retained ranks and differentia from surface."""
    surface = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S),
        predeposit_strata=0,
        stratum_differentia_bit_width=stratum_differentia_bit_width,
    )
    surface.DepositStrata(num_deposits)

    specimen = hstrat.surf_to_specimen(surface)

    assert list(specimen.GetRankIndex()) == list(surface.IterRetainedRanks())
    assert list(specimen.GetDifferentiaVals()) == list(
        surface.IterRetainedDifferentia()
    )


@pytest.mark.parametrize("stratum_differentia_bit_width", [1, 2, 8, 64])
def test_differentia_bit_width_preserved(stratum_differentia_bit_width):
    """Specimen should report the same differentia bit width as the surface."""
    algo = dstream.steady_algo
    S = 8
    surface = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S),
        predeposit_strata=0,
        stratum_differentia_bit_width=stratum_differentia_bit_width,
    )
    surface.DepositStrata(10)

    specimen = hstrat.surf_to_specimen(surface)
    assert (
        specimen.GetStratumDifferentiaBitWidth()
        == stratum_differentia_bit_width
    )
