import pickle
import tempfile

import pytest

from hstrat import hstrat
from hstrat.hstrat import depth_proportional_resolution_algo


@pytest.mark.parametrize(
    "impl",
    depth_proportional_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "depth_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_init(impl, depth_proportional_resolution):
    spec = impl(depth_proportional_resolution).GetSpec()
    assert (
        spec
        == impl(
            policy_spec=depth_proportional_resolution_algo.PolicySpec(
                depth_proportional_resolution
            ),
        ).GetSpec()
    )
    assert spec == impl(policy_spec=spec).GetSpec()

    policy = impl(depth_proportional_resolution)

    # invariants
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBound)
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank)
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBoundPessimalRank)
    assert callable(policy.CalcMrcaUncertaintyRelUpperBound)
    assert callable(policy.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank)
    assert callable(policy.CalcMrcaUncertaintyRelUpperBoundPessimalRank)
    assert callable(policy.CalcNumStrataRetainedUpperBound)
    # scrying
    assert callable(policy.CalcMrcaUncertaintyAbsExact)
    assert callable(policy.CalcMrcaUncertaintyRelExact)
    assert callable(policy.CalcNumStrataRetainedExact)
    assert callable(policy.CalcRankAtColumnIndex)
    assert callable(policy.IterRetainedRanks)
    # enactment
    assert callable(policy.GenDropRanks)


@pytest.mark.parametrize(
    "impl", depth_proportional_resolution_algo._Policy_.impls
)
@pytest.mark.parametrize(
    "depth_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_GetEvalCtor(impl, depth_proportional_resolution):
    spec = impl(depth_proportional_resolution)
    eval_ctor = spec.GetEvalCtor()
    assert eval_ctor.startswith(
        "hstrat.depth_proportional_resolution_algo.Policy("
    )
    assert eval_ctor.endswith(")")
    reconstituted = eval(eval_ctor)
    assert str(spec) == str(reconstituted)


@pytest.mark.parametrize(
    "depth_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_GetEvalCtor_consistency(depth_proportional_resolution):
    assert (
        len(
            set(
                impl(depth_proportional_resolution).GetEvalCtor()
                for impl in depth_proportional_resolution_algo._Policy_.impls
            )
        )
        == 1
    )


@pytest.mark.parametrize(
    "depth_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_pickle(depth_proportional_resolution):
    original = depth_proportional_resolution_algo.Policy(
        depth_proportional_resolution
    )
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


@pytest.mark.parametrize(
    "impl",
    depth_proportional_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "depth_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_eq(impl, depth_proportional_resolution):
    policy = impl(depth_proportional_resolution)
    assert policy == policy
    assert policy == impl(depth_proportional_resolution)
    assert not policy == policy.WithoutCalcRankAtColumnIndex()
    assert (
        policy.WithoutCalcRankAtColumnIndex()
        == policy.WithoutCalcRankAtColumnIndex()
    )
    assert not policy == impl(depth_proportional_resolution + 1)


@pytest.mark.parametrize(
    "impl",
    depth_proportional_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "depth_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_GetSpec(impl, depth_proportional_resolution):
    spec = impl(depth_proportional_resolution).GetSpec()
    assert spec == type(spec)(depth_proportional_resolution)


@pytest.mark.parametrize(
    "impl",
    depth_proportional_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "depth_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_WithoutCalcRankAtColumnIndex(impl, depth_proportional_resolution):

    original = impl(depth_proportional_resolution)
    stripped = original.WithoutCalcRankAtColumnIndex()

    assert stripped.CalcRankAtColumnIndex is None

    assert (
        original.CalcMrcaUncertaintyAbsUpperBound
        == stripped.CalcMrcaUncertaintyAbsUpperBound
    )
    assert (
        original.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank
        == stripped.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank
    )
    assert (
        original.CalcMrcaUncertaintyAbsUpperBoundPessimalRank
        == stripped.CalcMrcaUncertaintyAbsUpperBoundPessimalRank
    )
    assert (
        original.CalcMrcaUncertaintyRelUpperBound
        == stripped.CalcMrcaUncertaintyRelUpperBound
    )
    assert (
        original.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank
        == stripped.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank
    )
    assert (
        original.CalcMrcaUncertaintyRelUpperBoundPessimalRank
        == stripped.CalcMrcaUncertaintyRelUpperBoundPessimalRank
    )
    assert (
        original.CalcNumStrataRetainedUpperBound
        == stripped.CalcNumStrataRetainedUpperBound
    )
    # scrying
    assert (
        original.CalcMrcaUncertaintyAbsExact
        == stripped.CalcMrcaUncertaintyAbsExact
    )
    assert (
        original.CalcMrcaUncertaintyRelExact
        == stripped.CalcMrcaUncertaintyRelExact
    )
    assert (
        original.CalcNumStrataRetainedExact
        == stripped.CalcNumStrataRetainedExact
    )
    assert original.IterRetainedRanks == stripped.IterRetainedRanks
    # enactment
    assert original.GenDropRanks == stripped.GenDropRanks

    # test chaining
    assert (
        impl(
            depth_proportional_resolution,
        ).WithoutCalcRankAtColumnIndex()
        == stripped
    )


@pytest.mark.parametrize(
    "impl",
    depth_proportional_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "depth_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_repr(impl, depth_proportional_resolution):
    policy = impl(
        depth_proportional_resolution,
    )
    assert str(depth_proportional_resolution) in repr(policy)
    assert policy.GetSpec().GetAlgoIdentifier() in repr(policy)


@pytest.mark.parametrize(
    "impl",
    depth_proportional_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "depth_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_str(impl, depth_proportional_resolution):
    policy = impl(
        depth_proportional_resolution,
    )
    assert str(depth_proportional_resolution) in str(policy)
    assert policy.GetSpec().GetAlgoTitle() in str(policy)


@pytest.mark.parametrize(
    "depth_proportional_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
@pytest.mark.parametrize(
    "what",
    [
        lambda x: str(x),
    ],
)
def test_consistency(depth_proportional_resolution, what):
    assert (
        len(
            {
                what(impl(depth_proportional_resolution))
                for impl in depth_proportional_resolution_algo._Policy_.impls
            }
        )
        == 1
    )
