import os
import types

from downstream import dstream, dsurf
import pandas as pd
import pytest

from hstrat import hstrat

assets_path = os.path.join(
    os.path.dirname(__file__), os.pardir, "test_dataframe", "assets"
)


def _make_dstream_df(
    surfaces,
    algo,
    stratum_differentia_bit_width,
    dstream_T_bitwidth=32,
):
    """Build a pandas DataFrame with dstream metadata from surfaces."""
    rows = []
    for surf in surfaces:
        hex_string = hstrat.surf_to_hex(
            surf, dstream_T_bitwidth=dstream_T_bitwidth
        )
        rows.append(
            {
                "data_hex": hex_string,
                "dstream_algo": f"dstream.{algo.__name__.split('.')[-1]}",
                "dstream_storage_bitoffset": dstream_T_bitwidth,
                "dstream_storage_bitwidth": surf.S
                * stratum_differentia_bit_width,
                "dstream_T_bitoffset": 0,
                "dstream_T_bitwidth": dstream_T_bitwidth,
                "dstream_S": surf.S,
            },
        )
    return pd.DataFrame(rows)


# -------------------------------------------------------------------
# Round-trip tests: create surfaces, serialize to df, deserialize
# -------------------------------------------------------------------


@pytest.mark.parametrize(
    "algo",
    [
        dstream.steady_algo,
        dstream.stretched_algo,
        dstream.tilted_algo,
    ],
)
@pytest.mark.parametrize("S", [8, 16])
@pytest.mark.parametrize("n", [0, 1, 5, 25, 100])
@pytest.mark.parametrize("stratum_differentia_bit_width", [1, 8, 64])
def test_round_trip(
    algo: types.ModuleType,
    S: int,
    n: int,
    stratum_differentia_bit_width: int,
):
    """Surfaces serialized to a dstream df and deserialized back into
    an assemblage should preserve retained ranks and differentia."""
    surfaces = [
        hstrat.HereditaryStratigraphicSurface(
            dsurf.Surface(algo, S),
            predeposit_strata=0,
            stratum_differentia_bit_width=stratum_differentia_bit_width,
        )
        for _ in range(3)
    ]
    for surf in surfaces:
        surf.DepositStrata(n)

    df = _make_dstream_df(surfaces, algo, stratum_differentia_bit_width)
    assemblage = hstrat.assemblage_from_dstream_df(df)

    for surf, specimen in zip(surfaces, assemblage.BuildSpecimens()):
        retained_ranks = list(surf.IterRetainedRanks())
        retained_diff = list(surf.IterRetainedDifferentia())

        specimen_ranks = list(specimen.IterRetainedRanks())
        specimen_diff = list(specimen.IterRetainedDifferentia())

        assert specimen_ranks == retained_ranks
        assert specimen_diff == retained_diff


def test_single_surface():
    """A single surface should produce a one-specimen assemblage."""
    algo = dstream.steady_algo
    S = 8
    bit_width = 8
    surf = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S),
        predeposit_strata=0,
        stratum_differentia_bit_width=bit_width,
    )
    surf.DepositStrata(10)

    df = _make_dstream_df([surf], algo, bit_width)
    assemblage = hstrat.assemblage_from_dstream_df(df)

    specimens = list(assemblage.BuildSpecimens())
    assert len(specimens) == 1
    assert list(specimens[0].IterRetainedRanks()) == list(
        surf.IterRetainedRanks()
    )
    assert list(specimens[0].IterRetainedDifferentia()) == list(
        surf.IterRetainedDifferentia()
    )


def test_multiple_surfaces():
    """Multiple surfaces should produce corresponding specimens."""
    algo = dstream.steady_algo
    S = 8
    bit_width = 8
    surfaces = []
    for i in range(5):
        surf = hstrat.HereditaryStratigraphicSurface(
            dsurf.Surface(algo, S),
            predeposit_strata=0,
            stratum_differentia_bit_width=bit_width,
        )
        surf.DepositStrata(10 + i * 5)
        surfaces.append(surf)

    df = _make_dstream_df(surfaces, algo, bit_width)
    assemblage = hstrat.assemblage_from_dstream_df(df)

    specimens = list(assemblage.BuildSpecimens())
    assert len(specimens) == len(surfaces)


# -------------------------------------------------------------------
# Error handling tests
# -------------------------------------------------------------------


def test_missing_column_raises():
    """Raises ValueError when a required column is absent."""
    algo = dstream.steady_algo
    S = 8
    bit_width = 8
    surf = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S),
        predeposit_strata=0,
        stratum_differentia_bit_width=bit_width,
    )
    surf.DepositStrata(10)

    df = _make_dstream_df([surf], algo, bit_width)
    stripped = df.drop(columns=["data_hex"])
    with pytest.raises(ValueError, match="missing required columns"):
        hstrat.assemblage_from_dstream_df(stripped)


def test_missing_multiple_columns_raises():
    """Raises ValueError listing all missing columns."""
    algo = dstream.steady_algo
    S = 8
    bit_width = 8
    surf = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S),
        predeposit_strata=0,
        stratum_differentia_bit_width=bit_width,
    )
    surf.DepositStrata(10)

    df = _make_dstream_df([surf], algo, bit_width)
    stripped = df.drop(columns=["data_hex", "dstream_algo"])
    with pytest.raises(ValueError, match="missing required columns"):
        hstrat.assemblage_from_dstream_df(stripped)


# -------------------------------------------------------------------
# Smoke test with CSV test asset
# -------------------------------------------------------------------


def test_from_packed_csv():
    """Smoke test: deserialize assemblage from packed_simple.csv asset."""
    df = pd.read_csv(f"{assets_path}/packed_simple.csv")
    assemblage = hstrat.assemblage_from_dstream_df(df)
    specimens = list(assemblage.BuildSpecimens())
    assert len(specimens) == 2  # packed_simple.csv has 2 rows


# -------------------------------------------------------------------
# progress_wrap parameter test
# -------------------------------------------------------------------


def test_progress_wrap():
    """The progress_wrap callable is applied to the row iterator."""
    algo = dstream.steady_algo
    S = 8
    bit_width = 8

    surfs = [
        hstrat.HereditaryStratigraphicSurface(
            dsurf.Surface(algo, S),
            predeposit_strata=0,
            stratum_differentia_bit_width=bit_width,
        )
        for _ in range(3)
    ]
    for s in surfs:
        s.DepositStrata(10)

    df = _make_dstream_df(surfs, algo, bit_width)

    call_count = 0

    def counting_wrap(it):
        nonlocal call_count
        call_count += 1
        return it

    hstrat.assemblage_from_dstream_df(df, progress_wrap=counting_wrap)
    assert call_count == 1


# -------------------------------------------------------------------
# Differentia bit width preserved test
# -------------------------------------------------------------------


@pytest.mark.parametrize("stratum_differentia_bit_width", [1, 2, 8, 64])
def test_differentia_bit_width_preserved(
    stratum_differentia_bit_width,
):
    """Assemblage specimens have correct differentia bit width."""
    algo = dstream.steady_algo
    S = 8
    surf = hstrat.HereditaryStratigraphicSurface(
        dsurf.Surface(algo, S),
        predeposit_strata=0,
        stratum_differentia_bit_width=stratum_differentia_bit_width,
    )
    surf.DepositStrata(10)

    df = _make_dstream_df([surf], algo, stratum_differentia_bit_width)
    assemblage = hstrat.assemblage_from_dstream_df(df)
    specimen = next(assemblage.BuildSpecimens())
    assert (
        specimen.GetStratumDifferentiaBitWidth()
        == stratum_differentia_bit_width
    )
