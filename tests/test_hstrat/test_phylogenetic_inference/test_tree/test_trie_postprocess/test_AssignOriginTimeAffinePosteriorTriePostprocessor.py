import collections
import random
import typing

import numpy as np
import pandas as pd
from phyloframe import legacy as pfl
import polars as pl
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import coerce_to_pandas
from hstrat.dataframe import (
    surface_postprocess_trie,
    surface_test_drive,
    surface_unpack_reconstruct,
)
import hstrat.phylogenetic_inference.tree._impl as impl
import hstrat.phylogenetic_inference.tree.trie_postprocess._detail as detail
from hstrat.test_drive import evolve_fitness_trait_population


def _make_cherry_df(**kwargs) -> pl.DataFrame:
    # 0 (root) <- 1 (rank 10) <- 2, 3 (leaves, rank 40)
    return pl.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 1],
            "rank": [0, 10, 40, 40],
            **kwargs,
        },
    )


def test_base_class():
    assert issubclass(
        hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor,
        detail.TriePostprocessorBase,
    )


def test_anytree_not_implemented():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    with pytest.raises(NotImplementedError):
        hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor()(
            root, p_differentia_collision=0.5
        )


def test_pandas_not_implemented():
    with pytest.raises(NotImplementedError):
        hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor()(
            _make_cherry_df().to_pandas(), p_differentia_collision=0.5
        )


def test_no_collision_probability_gives_interval_mean():
    df = _make_cherry_df()
    df = hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor()(
        df, p_differentia_collision=0.0
    )
    df = coerce_to_pandas(df)
    assert df.loc[0, "origin_time"] == 0
    # mean of uniform prior over [10, 40)
    assert df.loc[1, "origin_time"] == pytest.approx(24.5)
    assert df.loc[2, "origin_time"] == 40
    assert df.loc[3, "origin_time"] == 40


def test_collisions_give_earlier_estimate():
    df = _make_cherry_df()
    ftor = hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor()
    estimates = [
        coerce_to_pandas(
            ftor(df, p_differentia_collision=p),
        ).loc[1, "origin_time"]
        for p in (0.0, 0.25, 0.5, 0.75)
    ]
    assert all(np.diff(estimates) < 0)
    assert all(0 <= e < 40 for e in estimates)


def test_collapsed_unifurcations_give_earlier_estimate():
    ftor = hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor()
    without = coerce_to_pandas(
        ftor(_make_cherry_df(), p_differentia_collision=0.5),
    )
    with_ = coerce_to_pandas(
        ftor(
            _make_cherry_df(hstrat_collapsed_unifurcations=[0, 3, 0, 0]),
            p_differentia_collision=0.5,
        ),
    )
    assert with_.loc[1, "origin_time"] != without.loc[1, "origin_time"]
    assert with_.loc[2, "origin_time"] == 40


def test_exact_posterior_mean():
    # 0 <- 1 (rank 4) <- 2 (rank 8) <- 3, 4 (leaves, rank 12)
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 1, 2, 2],
            "rank": [0, 4, 8, 12, 12],
        },
    )
    p = 0.5
    df = coerce_to_pandas(
        hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor()(
            df, p_differentia_collision=p
        ),
    )
    # intervals [0, 4), [4, 8), [8, 12), requiring 2, 1, 0 collisions
    weights = np.array([4 * p**2, 4 * p, 4])
    means = np.array([1.5, 5.5, 9.5])
    expected = np.average(means, weights=weights)
    assert df.loc[2, "origin_time"] == pytest.approx(expected)
    # node 1 is a unifurcation, interval [4, 8) requires no collisions
    expected1 = np.average([1.5, 5.5], weights=[4 * p, 4])
    assert df.loc[1, "origin_time"] == pytest.approx(expected1)


def test_exact_posterior_mean_collapsed():
    # equivalent to test_exact_posterior_mean, with rank 4 node collapsed
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 1],
            "rank": [0, 8, 12, 12],
            "hstrat_collapsed_unifurcations": [0, 1, 0, 0],
        },
    )
    p = 0.5
    df = coerce_to_pandas(
        hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor()(
            df, p_differentia_collision=p
        ),
    )
    weights = np.array([4 * p**2, 4 * p, 4])
    means = np.array([1.5, 5.5, 9.5])
    expected = np.average(means, weights=weights)
    assert df.loc[1, "origin_time"] == pytest.approx(expected)


def test_collapsed_unifurcation_below_bounds_mismatch():
    # 0 <- 1 (rank 8) <- 2, 3 (leaves, rank 16), 1 collapsed node each
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 1],
            "rank": [0, 8, 16, 16],
            "hstrat_collapsed_unifurcations": [0, 0, 1, 1],
        },
    )
    df = coerce_to_pandas(
        hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor()(
            df, p_differentia_collision=0.0
        ),
    )
    # children first differ at (evenly-spaced) collapsed rank 12
    assert df.loc[1, "origin_time"] == pytest.approx(9.5)


def test_t0():
    ftor = hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor()
    base = coerce_to_pandas(
        ftor(_make_cherry_df(), p_differentia_collision=0.5),
    )
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 1],
            "rank": [5, 15, 45, 45],
            "t0_": [5, 5, 5, 5],
        },
    )
    for t0 in (5, "t0_"):
        res = coerce_to_pandas(
            hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor(t0=t0)(
                df, p_differentia_collision=0.5
            ),
        )
        np.testing.assert_allclose(res["origin_time"], base["origin_time"])


def test_null_rank_root():
    # as produced by alifestd_prefix_roots in surface_postprocess_trie
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 1],
            "rank": [None, 10, 40, 40],
        },
    )
    df = coerce_to_pandas(
        hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor()(
            df, p_differentia_collision=0.5
        ),
    )
    assert pd.isna(df.loc[0, "origin_time"])
    assert 0 <= df.loc[1, "origin_time"] < 40
    assert df.loc[2, "origin_time"] == 40


def test_estimates_respect_ancestors_and_children():
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5, 6],
            "ancestor_id": [0, 0, 1, 1, 2, 2, 3],
            "rank": [0, 30, 36, 32, 40, 40, 40],
            "hstrat_collapsed_unifurcations": [0, 0, 5, 0, 0, 0, 0],
        },
    )
    df = coerce_to_pandas(
        hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor()(
            df, p_differentia_collision=0.5
        ),
    )
    ot = df["origin_time"].to_numpy()
    anc = df["ancestor_id"].to_numpy()
    assert (ot >= ot[anc]).all()
    assert (ot[anc] <= df["rank"].to_numpy()).all()


def test_empty():
    df = pl.DataFrame(
        {"id": [], "ancestor_id": [], "rank": []},
        schema={"id": pl.UInt64, "ancestor_id": pl.UInt64, "rank": pl.Int64},
    )
    df = hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor()(
        df, p_differentia_collision=0.5
    )
    assert "origin_time" in df.columns
    assert len(df) == 0


def test_assigned_property():
    df = hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor(
        assigned_property="blueberry",
    )(_make_cherry_df(), p_differentia_collision=0.5)
    assert "blueberry" in df.columns
    assert "origin_time" not in df.columns


def test_mutate():
    df = _make_cherry_df()
    df_ = hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor()(
        df, p_differentia_collision=0.5, mutate=False
    )
    assert "origin_time" in df_.columns
    assert "origin_time" not in df.columns


def test_noncontiguous_ids():
    df = pl.DataFrame(
        {"id": [0, 2], "ancestor_id": [0, 0], "rank": [0, 1]},
    )
    with pytest.raises(NotImplementedError):
        hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor()(
            df, p_differentia_collision=0.5
        )


def test_warns_for_wider_differentiae():
    with pytest.warns(UserWarning, match="binary"):
        hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor()(
            _make_cherry_df(), p_differentia_collision=0.25
        )


def test_non_uniform_prior_not_implemented():
    with pytest.raises(NotImplementedError):
        hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor(
            prior=hstrat.ArbitraryPrior(),
        )


def _calc_true_mrca_times(
    true_df: pd.DataFrame, reconstructed_df: pd.DataFrame
) -> typing.Dict[int, int]:
    """Map each reconstructed inner node with two or more children to the
    true origin time of the MRCA of its leaves."""
    ancestor_of = dict(zip(true_df["id"], true_df["ancestor_id"]))
    origin_time_of = dict(zip(true_df["id"], true_df["origin_time"]))

    def lineage(id_: int) -> typing.Set[int]:
        res = {id_}
        while ancestor_of[id_] != id_:
            id_ = ancestor_of[id_]
            res.add(id_)
        return res

    children_of = collections.defaultdict(list)
    for id_, ancestor_id in zip(
        reconstructed_df["id"], reconstructed_df["ancestor_id"]
    ):
        if id_ != ancestor_id:
            children_of[ancestor_id].append(id_)

    source_of = dict(
        zip(reconstructed_df["id"], reconstructed_df["td_source_id"])
    )
    leaves_of = {}
    for id_ in reversed(reconstructed_df["id"].tolist()):
        children = children_of[id_]
        leaves_of[id_] = (
            [int(source_of[id_])]
            if not children
            else [leaf for child in children for leaf in leaves_of[child]]
        )

    return {
        id_: max(
            origin_time_of[x]
            for x in set.intersection(*map(lineage, leaves_of[id_]))
        )
        for id_, children in children_of.items()
        if len(children) >= 2
    }


class _NoCollisionCorrection:
    """Wrap postprocessor to ignore spurious collisions."""

    def __init__(self, postprocessor: typing.Callable) -> None:
        self._postprocessor = postprocessor

    def __call__(self, trie, p_differentia_collision, **kwargs):
        return self._postprocessor(trie, p_differentia_collision=0.0, **kwargs)


def test_reconstructed_origin_times_unbiased():
    # simulate neutral evolution, then reconstruct from 1-bit surfaces
    random.seed(0)
    np.random.seed(0)
    true_df = pfl.alifestd_to_working_format(
        evolve_fitness_trait_population(
            population_size=128,
            num_generations=200,
            num_islands=4,
            num_niches=1,
            p_island_migration=1e-2,
            mut_distn=lambda size=None: np.zeros(size),
        ),
    )
    tips_df = surface_test_drive(
        pl.from_pandas(true_df[["id", "ancestor_id", "origin_time"]])
        .cast(pl.UInt64)
        .lazy(),
        dstream_algo="dstream.steady_algo",
        dstream_S=32,
        stratum_differentia_bit_width=1,
    )
    raw_df = surface_unpack_reconstruct(tips_df)

    postprocessor = hstrat.AssignOriginTimeAffinePosteriorTriePostprocessor(
        t0="dstream_S",
    )
    errors = {}
    for name, trie_postprocessor in (
        ("corrected", postprocessor),
        ("uncorrected", _NoCollisionCorrection(postprocessor)),
    ):
        reconstructed_df = surface_postprocess_trie(
            raw_df, trie_postprocessor=trie_postprocessor
        ).to_pandas()
        # align reconstructed and true time scales, using leaves
        is_leaf = reconstructed_df["td_source_id"].notna()
        true_origin_times = dict(zip(true_df["id"], true_df["origin_time"]))
        offset = np.median(
            reconstructed_df.loc[is_leaf, "td_source_id"]
            .astype(int)
            .map(true_origin_times)
            - reconstructed_df.loc[is_leaf, "origin_time"]
        )
        origin_times = dict(
            zip(reconstructed_df["id"], reconstructed_df["origin_time"])
        )
        errors[name] = np.array(
            [
                origin_times[id_] + offset - true_mrca_time
                for id_, true_mrca_time in _calc_true_mrca_times(
                    true_df, reconstructed_df
                ).items()
            ],
        )

    corrected = errors["corrected"]
    standard_error = corrected.std() / np.sqrt(len(corrected))
    assert len(corrected) > 20
    assert abs(corrected.mean()) < 3 * standard_error
    # without correction, estimates are biased toward being too recent
    assert errors["uncorrected"].mean() - corrected.mean() > 3 * standard_error
