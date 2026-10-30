import itertools
import typing

from downstream import dstream
import numpy as np
import polars as pl
import pytest

from hstrat import hstrat
from hstrat._auxiliary_lib import seed_random
from hstrat.dataframe import (
    surface_postprocess_trie,
    surface_test_drive,
    surface_unpack_reconstruct,
)
import hstrat.phylogenetic_inference.tree._impl as impl
import hstrat.phylogenetic_inference.tree.trie_postprocess._detail as detail


def _lookup_retained_ranks(algo: str, S: int, T: int) -> np.ndarray:
    algo = getattr(dstream, algo.removeprefix("dstream."))
    return np.sort([*algo.lookup_ingest_times(S, T)]).astype(np.int64)


def _make_two_tip_trie(
    S: int, lca_rank: int, T_a: int, T_b: int, root_rank: int = 0
) -> pl.DataFrame:
    # 0 (root) <- 1 (lca) <- 2, 3 (leaves, rank T - 1)
    return pl.DataFrame(
        {
            "id": [0, 1, 2, 3],
            "ancestor_id": [0, 0, 1, 1],
            "rank": [root_rank, lca_rank, T_a - 1, T_b - 1],
            "dstream_S": [S] * 4,
        },
    )


def _calc_estimate(
    algo: str, S: int, lca_rank: int, T_a: int, T_b: int, p: float
) -> float:
    df = hstrat.AssignOriginTimeGeometricTriePostprocessor(algo)(
        _make_two_tip_trie(S, lca_rank, T_a, T_b), p_differentia_collision=p
    )
    return df["origin_time"][1]


def _calc_global_root_estimate(
    algo: str, S: int, T_a: int, T_b: int, p: float
) -> float:
    # 0 (global root, rank S) <- 1, 2 (leaves, rank T - 1)
    df = pl.DataFrame(
        {
            "id": [0, 1, 2],
            "ancestor_id": [0, 0, 0],
            "rank": [S, T_a - 1, T_b - 1],
            "dstream_S": [S] * 3,
        },
    )
    df = hstrat.AssignOriginTimeGeometricTriePostprocessor(algo)(
        df, p_differentia_collision=p
    )
    return df["origin_time"][0]


def test_base_class():
    assert issubclass(
        hstrat.AssignOriginTimeGeometricTriePostprocessor,
        detail.TriePostprocessorBase,
    )


def test_anytree_not_implemented():
    root = impl.TrieInnerNode(rank=None, differentia=None, parent=None)
    impl.TrieInnerNode(rank=0, differentia=0, parent=root)
    with pytest.raises(NotImplementedError):
        hstrat.AssignOriginTimeGeometricTriePostprocessor("steady_algo")(
            root, p_differentia_collision=0.5
        )


def test_pandas_not_implemented():
    with pytest.raises(NotImplementedError):
        hstrat.AssignOriginTimeGeometricTriePostprocessor("steady_algo")(
            _make_two_tip_trie(8, 16, 100, 100).to_pandas(),
            p_differentia_collision=0.5,
        )


@pytest.mark.parametrize(
    "dstream_algo",
    ["dstream.steady_algo", "steady_algo", dstream.steady_algo],
)
def test_dstream_algo_spec(dstream_algo: typing.Any):
    df = hstrat.AssignOriginTimeGeometricTriePostprocessor(dstream_algo)(
        _make_two_tip_trie(8, 16, 100, 100), p_differentia_collision=0.5
    )
    assert df["origin_time"].null_count() == 0


@pytest.mark.parametrize(
    "algo", ["steady_algo", "tilted_algo", "hybrid_0_steady_1_tilted_2_algo"]
)
@pytest.mark.parametrize("S", [8, 16, 32])
@pytest.mark.parametrize("T_a, T_b", [(200, 200), (200, 150), (130, 200)])
def test_no_collision_probability_gives_interval_midpoint(
    algo: str, S: int, T_a: int, T_b: int
):
    retained_a = _lookup_retained_ranks(algo, S, T_a)
    retained_b = _lookup_retained_ranks(algo, S, T_b)
    common = np.intersect1d(retained_a, retained_b)
    common = common[common >= S]
    for lo, hi in zip(common, [*common[1:], min(T_a, T_b)]):
        # interval between node rank and next shared rank, offset by t0 = S
        expected = (lo + hi - 1) / 2 - S
        assert _calc_estimate(algo, S, lo, T_a, T_b, 0.0) == expected


@pytest.mark.parametrize(
    "algo", ["steady_algo", "tilted_algo", "hybrid_0_steady_1_tilted_2_algo"]
)
@pytest.mark.parametrize("S", [8, 16, 32])
@pytest.mark.parametrize("T_a, T_b", [(200, 200), (200, 150), (130, 200)])
@pytest.mark.parametrize("p", [0.5, 0.25])
def test_exactly_unbiased(algo: str, S: int, T_a: int, T_b: int, p: float):
    # shared retained ranks; spurious matches occur at these
    retained_a = _lookup_retained_ranks(algo, S, T_a)
    retained_b = _lookup_retained_ranks(algo, S, T_b)
    common = np.intersect1d(retained_a, retained_b)
    common = common[common >= S]
    assert len(common)

    # cache estimates by trie lca rank; splits before first shared rank
    # give separate roots, scored as global root at S (index -1)
    def calc_estimates(p: float) -> typing.Dict[int, float]:
        return {
            -1: _calc_global_root_estimate(algo, S, T_a, T_b, p),
            **{
                i: _calc_estimate(algo, S, rank, T_a, T_b, p)
                for i, rank in enumerate(common)
            },
        }

    estimates, collision_free = calc_estimates(p), calc_estimates(0.0)

    # true divergence times
    for T in range(S, min(T_a, T_b) - 1):
        # i'th shared rank is last at or before true split
        i = np.searchsorted(common, T, side="right") - 1
        n = len(common) - 1 - i  # number of later shared ranks
        # trie lca at (i + K)'th shared rank, w/ K spurious matches
        expected_value = sum(
            (p**K * (1 - p) if K < n else p**n) * estimates[i + K]
            for K in range(n + 1)
        )
        assert expected_value == pytest.approx(collision_free[i])


@pytest.mark.parametrize(
    "algo", ["steady_algo", "tilted_algo", "hybrid_0_steady_1_tilted_2_algo"]
)
def test_terminal_node(algo: str):
    S, T = 16, 200
    retained = _lookup_retained_ranks(algo, S, T)
    last_shared = retained.max()
    for p in 0.0, 0.5:
        # no shared rank remains after node, so no extrapolation
        assert _calc_estimate(algo, S, last_shared, T, T, p) == (
            (last_shared + T - 1) / 2 - S
        )


def test_collisions_give_earlier_estimate():
    S, T = 16, 200
    common = _lookup_retained_ranks("steady_algo", S, T)
    rank = common[common >= S][1]
    assert _calc_estimate("steady_algo", S, rank, T, T, 0.5) < (
        _calc_estimate("steady_algo", S, rank, T, T, 0.0)
    )


def test_estimates_clamped_at_t0():
    S, T = 16, 200
    retained = _lookup_retained_ranks("steady_algo", S, T)
    rank = retained[retained < S][-1]
    estimate = _calc_estimate("steady_algo", S, rank, T, T, 0.0)
    next_shared = retained[retained > rank][0]
    assert estimate == (next_shared - S - 1) / 2


def test_global_root_estimated():
    S, T = 16, 200
    retained = _lookup_retained_ranks("steady_algo", S, T)
    next_shared = retained[retained > S][0]
    estimate = _calc_global_root_estimate("steady_algo", S, T, T, 0.0)
    assert estimate == (next_shared - S - 1) / 2


def test_roots_and_leaves_assigned_rank():
    S = 16
    df = hstrat.AssignOriginTimeGeometricTriePostprocessor("steady_algo")(
        _make_two_tip_trie(S, 40, 200, 150, root_rank=S),
        p_differentia_collision=0.5,
    )
    assert df["origin_time"].to_list()[0] == 0
    assert df["origin_time"].to_list()[2:] == [199 - S, 149 - S]


def test_int_t0():
    S, T = 16, 200
    df = _make_two_tip_trie(S, 40, T, T)
    res_col = hstrat.AssignOriginTimeGeometricTriePostprocessor("steady_algo")(
        df, p_differentia_collision=0.5
    )
    res_int = hstrat.AssignOriginTimeGeometricTriePostprocessor(
        "steady_algo", t0=S
    )(df, p_differentia_collision=0.5)
    assert res_col["origin_time"].equals(res_int["origin_time"])

    res_zero = hstrat.AssignOriginTimeGeometricTriePostprocessor(
        "steady_algo", t0=0
    )(df, p_differentia_collision=0.5)
    assert res_zero["origin_time"][2] == T - 1


def test_polytomy():
    # 0 (root) <- 1 (rank 40) <- 2, 3, 4 (leaves)
    S, Ts = 16, [200, 150, 180]
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4],
            "ancestor_id": [0, 0, 1, 1, 1],
            "rank": [0, 40, *(T - 1 for T in Ts)],
            "dstream_S": [S] * 5,
        },
    )
    res = hstrat.AssignOriginTimeGeometricTriePostprocessor("steady_algo")(
        df, p_differentia_collision=0.0
    )
    common = list(
        itertools.accumulate(
            (_lookup_retained_ranks("steady_algo", S, T) for T in Ts),
            np.intersect1d,
        ),
    )[-1]
    next_shared = common[common > 40][0]
    assert res["origin_time"][1] == (40 + next_shared - 1) / 2 - S


def test_nested_inner_nodes():
    # 0 (root) <- 1 (rank 20) <- 2 (rank 60) <- 3, 4 (leaves)
    #                         <- 5 (leaf)
    S, T = 16, 200
    df = pl.DataFrame(
        {
            "id": [0, 1, 2, 3, 4, 5],
            "ancestor_id": [0, 0, 1, 2, 2, 1],
            "rank": [0, 20, 60, T - 1, T - 1, T - 61],
            "dstream_S": [S] * 6,
        },
    )
    res = hstrat.AssignOriginTimeGeometricTriePostprocessor("steady_algo")(
        df, p_differentia_collision=0.0
    )
    # youngest tip under each of node 1's children has T - 60
    common = np.intersect1d(
        _lookup_retained_ranks("steady_algo", S, T),
        _lookup_retained_ranks("steady_algo", S, T - 60),
    )
    next_shared = common[common > 20][0]
    assert res["origin_time"][1] == (20 + next_shared - 1) / 2 - S
    retained = _lookup_retained_ranks("steady_algo", S, T)
    next_shared = retained[retained > 60][0]
    assert res["origin_time"][2] == (60 + next_shared - 1) / 2 - S


def test_empty():
    df = pl.DataFrame(
        {"id": [], "ancestor_id": [], "rank": [], "dstream_S": []},
        schema={
            "id": pl.UInt64,
            "ancestor_id": pl.UInt64,
            "rank": pl.Int64,
            "dstream_S": pl.Int64,
        },
    )
    res = hstrat.AssignOriginTimeGeometricTriePostprocessor(
        "steady_algo", t0=0
    )(df, p_differentia_collision=0.5)
    assert len(res) == 0
    assert "origin_time" in res.columns


def test_assigned_property():
    res = hstrat.AssignOriginTimeGeometricTriePostprocessor(
        "steady_algo", assigned_property="foo"
    )(_make_two_tip_trie(8, 16, 100, 100), p_differentia_collision=0.5)
    assert "foo" in res.columns
    assert "origin_time" not in res.columns


def test_mutate():
    df = _make_two_tip_trie(8, 16, 100, 100)
    original = df.clone()
    hstrat.AssignOriginTimeGeometricTriePostprocessor("steady_algo")(
        df, p_differentia_collision=0.5, mutate=False
    )
    assert df.equals(original)


def test_noncontiguous_ids():
    df = _make_two_tip_trie(8, 16, 100, 100).with_columns(
        pl.col("id") * 2, pl.col("ancestor_id") * 2
    )
    with pytest.raises(NotImplementedError):
        hstrat.AssignOriginTimeGeometricTriePostprocessor("steady_algo")(
            df, p_differentia_collision=0.5
        )


def _calc_cherry_errors(
    reconstructed_df: pl.DataFrame, true_split_times: typing.List[int]
) -> np.ndarray:
    """Estimated minus true divergence time, for each cherry's tip pair."""
    ancestor_ids = reconstructed_df["ancestor_id"].to_numpy()
    origin_times = reconstructed_df["origin_time"].to_numpy()
    leaf_ids = {
        source_id: id_
        for id_, source_id in enumerate(reconstructed_df["td_source_id"])
        if source_id is not None
    }

    def lineage(id_: int) -> typing.List[int]:
        lineage = [id_]
        while ancestor_ids[lineage[-1]] != lineage[-1]:
            lineage.append(ancestor_ids[lineage[-1]])
        return lineage

    errors = []
    for k, true_split_time in enumerate(true_split_times):
        lineage_a = lineage(leaf_ids[3 * k + 2])
        lineage_b = {*lineage(leaf_ids[3 * k + 3])}
        mrca_id = next((id_ for id_ in lineage_a if id_ in lineage_b), None)
        if mrca_id is not None:  # split before first shared rank otherwise
            errors.append(origin_times[mrca_id] - true_split_time)
    return np.array(errors)


@pytest.mark.parametrize(
    "algo", ["steady_algo", "tilted_algo", "hybrid_0_steady_1_tilted_2_algo"]
)
def test_reconstructed_origin_times_unbiased(algo: str):
    # many independent cherries under a common root: root (generation 0)
    # <- split (generation T) <- two tips (generation G)
    seed_random(1)
    S, G, num_cherries = 16, 200, 400
    # test drive deposits S items before founding, so ranks are offset by S
    retained = _lookup_retained_ranks(algo, S, G + S)
    first_shared = retained[retained >= S][0] - S
    split_times = np.random.randint(first_shared, G - 1, size=num_cherries)
    true_df = pl.DataFrame(
        {
            "id": np.arange(3 * num_cherries + 1),
            "ancestor_id": [
                0,
                *itertools.chain(
                    *((0, k, k) for k in range(1, 3 * num_cherries, 3))
                ),
            ],
            "origin_time": [
                0,
                *itertools.chain(*((T, G, G) for T in split_times)),
            ],
        },
    ).cast(pl.UInt64)
    tips_df = surface_test_drive(
        true_df.lazy(),
        dstream_algo=f"dstream.{algo}",
        dstream_S=S,
        stratum_differentia_bit_width=1,
    )
    raw_df = surface_unpack_reconstruct(tips_df)

    errors = {
        name: _calc_cherry_errors(
            surface_postprocess_trie(raw_df, trie_postprocessor=postprocessor),
            split_times.tolist(),
        )
        for name, postprocessor in (
            (
                "corrected",
                hstrat.AssignOriginTimeGeometricTriePostprocessor(algo),
            ),
            (
                "uncorrected",
                hstrat.AssignOriginTimeNodeRankTriePostprocessor(
                    t0="dstream_S",
                ),
            ),
        )
    }

    corrected = errors["corrected"]
    standard_error = corrected.std() / np.sqrt(len(corrected))
    assert len(corrected) >= 0.99 * num_cherries
    assert abs(corrected.mean()) < 3 * standard_error
    # without correction, estimates are biased toward being too recent
    assert errors["uncorrected"].mean() - corrected.mean() > 3 * standard_error
