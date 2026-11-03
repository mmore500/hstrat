import functools
import os

from downstream import dstream
import numpy as np
from phyloframe import legacy as pfl
import polars as pl
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import ExperimentalWarning
from hstrat.dataframe import surface_build_tree, surface_test_drive
from hstrat.phylogenetic_inference.tree.trie_postprocess._AssignOriginTimeEmpiricalBayesSurfPostprocessor import (
    _calc_posterior_origin_times,
    _calc_prior_moments,
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


def make_trie(dstream_algo: str, bitwidth: int) -> tuple:
    """Trie and collision probability, as seen by trie postprocessors."""
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
    return captured["trie"], captured["p"]


def _make_hand_trie() -> pl.DataFrame:
    # root <- inner (rank 100) <- inner (rank 99) <- two leaves; and a leaf
    return pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_id": [0, 0, 1, 2, 2, 1],
            "rank": [64, 100, 99, 199, 199, 199],
            "dstream_S": [64] * 6,
        },
    )


def _brute_force(trie: pl.DataFrame, algo: str, p: float, alpha: float):
    """Reference posterior mean origin times, computed node by node."""
    S = trie["dstream_S"][0]
    ids = trie["id"].to_list()
    ancestors = trie["ancestor_id"].to_list()
    ranks = trie["rank"].to_list()
    children = {i: [] for i in ids}
    for i, a in zip(ids, ancestors):
        if i != a:
            children[a].append(i)

    @functools.lru_cache(maxsize=None)
    def youngest_T(i: int) -> int:
        if not children[i]:
            return ranks[i] + 1
        return min(youngest_T(c) for c in children[i])

    result = []
    for i in ids:
        if not children[i] or (ancestors[i] == i and len(children[i]) < 2):
            result.append(ranks[i] - S)
            continue
        compare_T = max(youngest_T(c) for c in children[i])
        retained = getattr(dstream, algo.removeprefix("dstream."))
        retained = sorted(retained.lookup_ingest_times(S, compare_T))
        after = [r for r in retained if ranks[i] < r < youngest_T(i)]
        hi = max((after[0] if after else youngest_T(i)) - S, 0)
        bounds = [hi, max(ranks[i] - S, 0)]
        bounds += [max(r - S, 0) for r in reversed(retained) if r < ranks[i]]
        bounds += [0]
        terms = [
            (*_calc_prior_moments(lo_, hi_, max(hi, 1), alpha), j)
            for j, (hi_, lo_) in enumerate(zip(bounds, bounds[1:]))
        ]
        weights = np.array([mass * p**j for mass, __, j in terms])
        means = np.array([mean for __, mean, __ in terms])
        result.append((weights * means).sum() / weights.sum())
    return np.array(result, dtype=float)


@pytest.mark.parametrize("alpha", [-2.5, 0.0, 1.0, 2.0])
@pytest.mark.parametrize("p", [0.5, 2**-8])
def test_brute_force_hand_built(alpha: float, p: float):
    trie = _make_hand_trie()
    np.testing.assert_allclose(
        _calc_posterior_origin_times(
            trie, p, dstream.steady_algo, 64, [alpha], lambda x: x
        )[:, 0],
        _brute_force(trie, "dstream.steady_algo", p, alpha),
    )


@pytest.mark.parametrize(
    "dstream_algo", ["dstream.steady_algo", "dstream.tilted_algo"]
)
@pytest.mark.parametrize("bitwidth", [1, 8])
def test_brute_force_population(dstream_algo: str, bitwidth: int):
    trie, p = make_trie(dstream_algo, bitwidth)
    algo = getattr(dstream, dstream_algo.removeprefix("dstream."))
    alphas = [-3.0, 0.0, 1.5]
    result = _calc_posterior_origin_times(
        trie, p, algo, 64, alphas, lambda x: x
    )
    for k, alpha in enumerate(alphas):
        np.testing.assert_allclose(
            result[:, k], _brute_force(trie, dstream_algo, p, alpha)
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
            hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
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
    weights = pfl.alifestd_mark_to_array_polars(
        benchmarked.select(pl.col("id", "ancestor_id").cast(pl.Int64)),
        pfl.alifestd_mark_num_mrca_leaf_pairs_polars,
    )
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


@pytest.mark.parametrize(
    "dstream_algo", ["dstream.steady_algo", "dstream.tilted_algo"]
)
@pytest.mark.parametrize("bitwidth", [1, 8])
def test_monotonic_in_alpha(dstream_algo: str, bitwidth: int):
    trie, p = make_trie(dstream_algo, bitwidth)
    algo = getattr(dstream, dstream_algo.removeprefix("dstream."))
    grid = _calc_posterior_origin_times(
        trie, p, algo, 64, np.linspace(-6, 6, 49), lambda x: x
    )
    assert (np.diff(grid, axis=1) >= -1e-9).all()


@pytest.mark.parametrize("alpha", [-3.0, -1.0, 0.0, 0.5, 1.0, 2.0, 2.5])
def test_prior_moments(alpha: float):
    H = 135.0
    for a, b in [(0.0, 1.0), (3.0, 50.0), (10.0, 135.0), (5.0, 5.0)]:
        mass, mean = _calc_prior_moments(a, b, H, alpha)
        if b <= a:
            assert mass == 0
            continue
        # backward lag from mismatch bound, u = H - t + 1
        u = np.linspace(H - b + 1, H - a + 1, 400_001)
        density = u**-alpha
        expected_mass = np.trapezoid(density, u)
        expected_mean = np.clip(
            H + 0.5 - np.trapezoid(u * density, u) / expected_mass,
            a,
            max(a, b - 1),
        )
        np.testing.assert_allclose(mass, expected_mass, rtol=1e-5)
        np.testing.assert_allclose(mean, expected_mean, rtol=1e-6, atol=1e-9)


@pytest.mark.parametrize("alpha", [-2.0, 0.0, 1.5])
def test_single_value_grid(alpha: float):
    trie = _make_hand_trie()
    result = hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
        "dstream.steady_algo", alpha_grid=[alpha]
    )(trie, p_differentia_collision=0.5)
    np.testing.assert_allclose(
        result["origin_time"].to_numpy(),
        _brute_force(trie, "dstream.steady_algo", 0.5, alpha),
    )


def test_clamped_warns():
    postprocessor = hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
        "dstream.steady_algo", alpha_grid=(-1e-3, 1e-3)
    )
    with pytest.warns(UserWarning, match="clamping"):
        result = postprocessor(_make_hand_trie(), p_differentia_collision=0.5)
    assert result["origin_time"].is_finite().all()


def test_invalid_alpha_grid():
    for alpha_grid in [(), (1.0, -1.0), (0.0, 0.0), [[0.0, 1.0]]]:
        with pytest.raises(ValueError):
            hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
                "dstream.steady_algo", alpha_grid=alpha_grid
            )


def test_assigned_property():
    result = hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
        "dstream.steady_algo", assigned_property="foo"
    )(_make_hand_trie(), p_differentia_collision=2**-8)
    assert "foo" in result.columns
    assert result["foo"][3:].to_list() == [135.0] * 3


def test_polars_only():
    with pytest.raises(NotImplementedError):
        hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
            "dstream.steady_algo",
        )(_make_hand_trie().to_pandas(), p_differentia_collision=0.5)


def test_no_leaf_pairs_uses_uniform_prior():
    # root (rank 64) <- unifurcation (rank 100) <- leaf: no leaf pairs
    trie = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 1],
            "rank": [64, 100, 199],
            "dstream_S": [64] * 3,
        },
    )
    result = hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
        "dstream.steady_algo",
    )(trie, p_differentia_collision=0.5)
    np.testing.assert_allclose(
        result["origin_time"].to_numpy(),
        _brute_force(trie, "dstream.steady_algo", 0.5, 0.0),
    )


def test_experimental_warning(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("HSTRAT_WARN_EXPERIMENTAL_SUPPRESS", raising=False)
    with pytest.warns(ExperimentalWarning):
        hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
            "dstream.steady_algo",
        )
