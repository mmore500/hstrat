import functools
import os

import numpy as np
import polars as pl
import pytest

from hstrat import hstrat
from hstrat.dataframe import surface_build_tree, surface_test_drive
from hstrat.phylogenetic_inference.tree.trie_postprocess._AssignOriginTimeEmpiricalBayesSurfPostprocessor import (
    _calc_mrca_pair_counts,
)
from hstrat.phylogenetic_inference.tree.trie_postprocess._detail._exponential_posterior import (
    _calc_exponential_prior_moments,
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


@pytest.mark.parametrize("rate", [-1.0, -0.01, -1e-8, 0.0, 1e-8, 0.01, 1.0])
def test_prior_moments(rate: float):
    a = np.array([[0.0, 3.0, 10.0, 5.0]])
    b = np.array([[1.0, 50.0, 400.0, 5.0]])
    shift = np.array([[max(rate, 0) * 400.0]])
    masses, means = _calc_exponential_prior_moments(a, b, shift, rate)
    for ai, bi, mass, mean in zip(a[0], b[0], masses[0], means[0]):
        if bi <= ai:
            assert mass == 0
            continue
        t = np.linspace(ai, bi, 200_001)
        density = np.exp(rate * t - shift.item())
        expected_mass = np.trapezoid(density, t)
        expected_mean = np.trapezoid(t * density, t) / expected_mass - 0.5
        np.testing.assert_allclose(mass, expected_mass, rtol=1e-5)
        np.testing.assert_allclose(mean, expected_mean, rtol=1e-5, atol=1e-6)


def test_clamped_rate_warns():
    postprocessor = hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
        "dstream.steady_algo", rate_bounds=(-1e-9, 1e-9)
    )
    with pytest.warns(UserWarning, match="clamping"):
        result = postprocessor(_make_trie(), p_differentia_collision=0.5)
    assert result["origin_time"].is_finite().all()


def test_invalid_rate_bounds():
    with pytest.raises(ValueError):
        hstrat.AssignOriginTimeEmpiricalBayesSurfPostprocessor(
            "dstream.steady_algo", rate_bounds=(1.0, -1.0)
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
