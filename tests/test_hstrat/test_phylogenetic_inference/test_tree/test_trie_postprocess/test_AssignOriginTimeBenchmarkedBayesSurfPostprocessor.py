import functools
import os

import numpy as np
import polars as pl
import pytest

from hstrat import hstrat
from hstrat.dataframe import surface_build_tree, surface_test_drive
from hstrat.phylogenetic_inference.tree.trie_postprocess._AssignOriginTimeBenchmarkedBayesSurfPostprocessor import (
    _calc_mrca_pair_counts,
)
from hstrat.phylogenetic_inference.tree.trie_postprocess._detail._backward_lag_posterior import (
    BackwardLagPosterior,
    _calc_prior_moments,
)
from hstrat.phylogenetic_inference.tree.trie_postprocess._detail._comparable_ranks import (
    resolve_dstream_algo,
)

assets = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../../../test_dataframe/assets",
)


@functools.lru_cache(maxsize=None)
def make_population(dstream_algo: str, bitwidth: int) -> pl.DataFrame:
    return surface_test_drive(
        pl.read_csv(f"{assets}/nk_ecoeaselection.csv"),
        dstream_algo=dstream_algo,
        dstream_S=64,
        stratum_differentia_bit_width=bitwidth,
    )


def _make_trie() -> pl.DataFrame:
    # root <- inner (rank 100) <- inner (rank 99) <- two leaves; and a leaf
    return pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_id": [0, 0, 1, 2, 2, 1],
            "rank": [64, 100, 99, 199, 199, 199],
            "dstream_S": [64] * 6,
        },
    )


@pytest.mark.parametrize(
    "dstream_algo", ["dstream.steady_algo", "dstream.tilted_algo"]
)
@pytest.mark.parametrize("bitwidth", [1, 8])
def test_matches_geometric_average(dstream_algo: str, bitwidth: int):
    pop = make_population(dstream_algo, bitwidth)
    benchmarked = surface_build_tree(
        pop,
        trie_postprocessor=(
            hstrat.AssignOriginTimeBenchmarkedBayesSurfPostprocessor(
                dstream_algo,
            )
        ),
    )
    geometric = surface_build_tree(
        pop,
        trie_postprocessor=hstrat.AssignOriginTimeGeometricSurfPostprocessor(
            dstream_algo,
        ),
    )
    assert benchmarked.select("id", "ancestor_id").equals(
        geometric.select("id", "ancestor_id"),
    )
    weights = _calc_mrca_pair_counts(benchmarked)
    assert weights.sum() == len(pop) * (len(pop) - 1) / 2
    np.testing.assert_allclose(
        weights @ benchmarked["origin_time"].to_numpy(),
        weights @ geometric["origin_time"].to_numpy(),
        rtol=1e-9,
    )
    # leaves keep their rank
    leaves = pl.Series(weights == 0)
    assert benchmarked.filter(leaves)["origin_time"].equals(
        geometric.filter(leaves)["origin_time"],
    )


@pytest.mark.parametrize("alpha", [-3.0, -1.0, 0.0, 0.5, 1.0, 2.0, 2.5])
def test_prior_moments(alpha: float):
    a = np.array([[0.0, 3.0, 10.0, 5.0]])
    b = np.array([[1.0, 50.0, 135.0, 5.0]])
    hi = np.array([[135.0]])
    masses, means = _calc_prior_moments(a, b, hi, alpha)
    for ai, bi, mass, mean in zip(a[0], b[0], masses[0], means[0]):
        if bi <= ai:
            assert mass == 0
            continue
        # backward lag from mismatch bound, u = hi - t + 1
        u = np.linspace(hi.item() - bi + 1, hi.item() - ai + 1, 400_001)
        density = u**-alpha
        expected_mass = np.trapezoid(density, u)
        expected_mean = np.clip(
            hi.item() + 0.5 - np.trapezoid(u * density, u) / expected_mass,
            ai,
            max(ai, bi - 1),
        )
        np.testing.assert_allclose(mass, expected_mass, rtol=1e-5)
        np.testing.assert_allclose(mean, expected_mean, rtol=1e-6, atol=1e-9)


@pytest.mark.parametrize(
    "p, expected",
    [
        # uniform posterior means of hand-built trie's inner nodes
        (0.5, [31.62419670298966, 30.893707205738508]),
        (2**-8, [35.99589461625753, 35.47653162432289]),
    ],
)
def test_uniform_prior_at_zero(p: float, expected: list):
    origin_times = BackwardLagPosterior(
        _make_trie(), p, resolve_dstream_algo("dstream.steady_algo"), 64
    ).origin_times(0.0)
    np.testing.assert_allclose(origin_times[1:3], expected)
    assert origin_times[[0, 3, 4, 5]].tolist() == [0.0, 135.0, 135.0, 135.0]


def test_grid_increasing_in_alpha():
    grid = BackwardLagPosterior(
        _make_trie(), 0.5, resolve_dstream_algo("dstream.steady_algo"), 64
    ).inner_means_grid(np.linspace(-3, 3, 25))
    assert (np.diff(grid, axis=1) >= -1e-9).all()
    assert (grid >= 0).all()


def test_clamped_warns():
    postprocessor = hstrat.AssignOriginTimeBenchmarkedBayesSurfPostprocessor(
        "dstream.steady_algo", alpha_grid=(-1e-3, 1e-3)
    )
    with pytest.warns(UserWarning, match="clamping"):
        result = postprocessor(_make_trie(), p_differentia_collision=0.5)
    assert result["origin_time"].is_finite().all()


def test_invalid_alpha_grid():
    for alpha_grid in [(0.0,), (1.0, -1.0)]:
        with pytest.raises(ValueError):
            hstrat.AssignOriginTimeBenchmarkedBayesSurfPostprocessor(
                "dstream.steady_algo", alpha_grid=alpha_grid
            )


def test_assigned_property():
    result = hstrat.AssignOriginTimeBenchmarkedBayesSurfPostprocessor(
        "dstream.steady_algo", assigned_property="foo"
    )(_make_trie(), p_differentia_collision=2**-8)
    assert "foo" in result.columns
    assert result["foo"][3:].to_list() == [135.0] * 3


def test_polars_only():
    with pytest.raises(NotImplementedError):
        hstrat.AssignOriginTimeBenchmarkedBayesSurfPostprocessor(
            "dstream.steady_algo",
        )(_make_trie().to_pandas(), p_differentia_collision=0.5)


@pytest.mark.parametrize("alpha", [-2.0, 0.0, 1.5])
def test_fixed_alpha(alpha: float):
    trie = _make_trie()
    result = hstrat.AssignOriginTimeBenchmarkedBayesSurfPostprocessor(
        "dstream.steady_algo", alpha=alpha
    )(trie, p_differentia_collision=0.5)
    expected = BackwardLagPosterior(
        trie, 0.5, resolve_dstream_algo("dstream.steady_algo"), 64
    ).origin_times(alpha)
    np.testing.assert_allclose(result["origin_time"].to_numpy(), expected)


@pytest.mark.parametrize(
    "dstream_algo", ["dstream.steady_algo", "dstream.tilted_algo"]
)
@pytest.mark.parametrize("bitwidth", [1, 8])
def test_fast_path_matches_reference(dstream_algo: str, bitwidth: int):
    from hstrat.phylogenetic_inference.tree.trie_postprocess._detail import (
        _backward_lag_posterior as blp,
    )
    from hstrat.phylogenetic_inference.tree.trie_postprocess._detail import (
        _comparable_ranks as cr,
    )

    captured = {}

    def capture(trie, p_differentia_collision, mutate, progress_wrap):
        if not isinstance(trie, pl.DataFrame):
            raise NotImplementedError
        captured["trie"] = trie.clone()
        captured["p"] = p_differentia_collision
        return trie

    surface_build_tree(
        make_population(dstream_algo, bitwidth), trie_postprocessor=capture
    )
    trie, p = captured["trie"], captured["p"]
    ranks, is_inner, compare_T, youngest_T = cr.mark_inner_node_bounds(trie)
    alphas = np.linspace(-3, 3, 25)
    for chunk, retained in cr.iter_retained_ranks(
        resolve_dstream_algo(dstream_algo), 64, compare_T
    ):
        args = (
            retained,
            ranks[is_inner].astype(np.float64)[chunk],
            youngest_T.astype(np.float64)[chunk],
            p,
            64,
            alphas,
        )
        np.testing.assert_allclose(
            blp._calc_means_grid_fast_path(*args),
            blp._calc_chunk_means_grid(*args),
            rtol=1e-12,
            atol=1e-9,
        )
