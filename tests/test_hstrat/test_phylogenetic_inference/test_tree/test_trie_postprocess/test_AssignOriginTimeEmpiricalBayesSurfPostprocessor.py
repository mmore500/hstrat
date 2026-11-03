import functools
import os

import numpy as np
import polars as pl
import pytest

from hstrat import hstrat
from hstrat.dataframe import surface_build_tree, surface_test_drive
from hstrat.phylogenetic_inference.tree.trie_postprocess._AssignOriginTimeEmpiricalBayesSurfPostprocessor import (
    _calc_mrca_pair_counts,
    _fit_alpha_ml,
)
from hstrat.phylogenetic_inference.tree.trie_postprocess._detail._backward_age_posterior import (
    BackwardAgePosterior,
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
    empirical_bayes = surface_build_tree(
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
    assert empirical_bayes.select("id", "ancestor_id").equals(
        geometric.select("id", "ancestor_id"),
    )
    weights = _calc_mrca_pair_counts(empirical_bayes)
    assert weights.sum() == len(pop) * (len(pop) - 1) / 2
    np.testing.assert_allclose(
        weights @ empirical_bayes["origin_time"].to_numpy(),
        weights @ geometric["origin_time"].to_numpy(),
        rtol=1e-6,
    )
    # leaves keep their rank
    leaves = weights == 0
    np.testing.assert_array_equal(
        empirical_bayes.filter(pl.Series(leaves))["origin_time"],
        geometric.filter(pl.Series(leaves))["origin_time"],
    )


@pytest.mark.parametrize("alpha", [-3.0, -1.0, 0.0, 0.5, 1.0, 2.5])
def test_prior_moments(alpha: float):
    a = np.array([[0.0, 3.0, 10.0, 5.0]])
    b = np.array([[1.0, 50.0, 135.0, 5.0]])
    c = np.array([[135.0]])
    masses, means = _calc_prior_moments(a, b, c, alpha)
    for ai, bi, mass, mean in zip(a[0], b[0], masses[0], means[0]):
        if bi <= ai:
            assert mass == 0
            continue
        # generations integrated over unit cells centered on them
        t = np.linspace(ai - 0.5, bi - 0.5, 400_001)
        density = ((c.item() - t) / (c.item() + 0.5)) ** -alpha
        expected_mass = np.trapezoid(density, t) / (c.item() + 0.5)
        expected_mean = np.trapezoid(t * density, t) / np.trapezoid(density, t)
        np.testing.assert_allclose(mass, expected_mass, rtol=1e-5)
        np.testing.assert_allclose(mean, expected_mean, rtol=1e-6, atol=1e-9)


@pytest.mark.parametrize("p", [0.5, 2**-8])
def test_uniform_prior_at_zero(p: float):
    # alpha = 0 gives interval midpoints weighted by length and collisions
    trie = _make_trie()
    origin_times = BackwardAgePosterior(
        trie, p, resolve_dstream_algo("dstream.steady_algo"), 64
    ).origin_times(0.0)
    assert origin_times[3:].tolist() == [135.0] * 3
    assert (np.diff([origin_times[1], 36.0]) > 0).all()  # below midpoint


@pytest.mark.parametrize(
    "dstream_algo", ["dstream.steady_algo", "dstream.tilted_algo"]
)
@pytest.mark.parametrize("bitwidth", [1, 8])
def test_ml_maximizes_likelihood(dstream_algo: str, bitwidth: int):
    pop = make_population(dstream_algo, bitwidth)
    captured = {}

    def capture(trie, p_differentia_collision, mutate, progress_wrap):
        if not isinstance(trie, pl.DataFrame):
            raise NotImplementedError
        captured["trie"] = trie.clone()
        captured["p"] = p_differentia_collision
        return trie

    surface_build_tree(pop, trie_postprocessor=capture)
    trie, p = captured["trie"], captured["p"]
    posterior = BackwardAgePosterior(
        trie, p, resolve_dstream_algo(dstream_algo), 64
    )
    alpha = _fit_alpha_ml(posterior, (-8.0, 8.0), 1e-4)
    best = posterior.log_likelihoods(alpha).sum()
    for other in np.linspace(-8, 8, 65):
        assert posterior.log_likelihoods(other).sum() <= best + 1e-6

    result = hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
        dstream_algo, fit="ml"
    )(trie, p_differentia_collision=p)
    np.testing.assert_allclose(
        result["origin_time"].to_numpy(), posterior.origin_times(alpha)
    )


def test_clamped_alpha_warns():
    postprocessor = hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
        "dstream.steady_algo", alpha_bounds=(-1e-9, 1e-9)
    )
    with pytest.warns(UserWarning, match="clamped"):
        result = postprocessor(_make_trie(), p_differentia_collision=0.5)
    assert result["origin_time"].is_finite().all()


def test_invalid_arguments():
    with pytest.raises(ValueError):
        hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
            "dstream.steady_algo", alpha_bounds=(1.0, -1.0)
        )
    with pytest.raises(ValueError):
        hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
            "dstream.steady_algo", fit="calibrated"
        )


def test_assigned_property():
    result = hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
        "dstream.steady_algo", assigned_property="foo"
    )(_make_trie(), p_differentia_collision=2**-8)
    assert "foo" in result.columns
    assert result["foo"][3:].to_list() == [135.0] * 3


def test_polars_only():
    with pytest.raises(NotImplementedError):
        hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
            "dstream.steady_algo",
        )(_make_trie().to_pandas(), p_differentia_collision=0.5)
