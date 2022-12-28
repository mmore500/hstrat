import pickle
import tempfile

import pytest

from hstrat import hstrat
from hstrat.hstrat import recency_proportional_resolution_algo


@pytest.mark.parametrize(
    "impl",
    recency_proportional_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "recency_proportional_resolution",
    [
        0,
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_init(impl, recency_proportional_resolution):
    spec = impl(recency_proportional_resolution).GetSpec()
    assert (
        spec
        == impl(
            policy_spec=recency_proportional_resolution_algo.PolicySpec(
                recency_proportional_resolution
            ),
        ).GetSpec()
    )
    assert spec == impl(policy_spec=spec).GetSpec()

    policy = impl(recency_proportional_resolution)

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
    "impl",
    recency_proportional_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "recency_proportional_resolution",
    [
        0,
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_eq(impl, recency_proportional_resolution):
    policy = impl(recency_proportional_resolution)
    assert policy == policy
    assert policy == impl(recency_proportional_resolution)
    assert not policy == policy.WithoutCalcRankAtColumnIndex()
    assert (
        policy.WithoutCalcRankAtColumnIndex()
        == policy.WithoutCalcRankAtColumnIndex()
    )
    assert not policy == impl(recency_proportional_resolution + 1)


@pytest.mark.parametrize(
    "impl", recency_proportional_resolution_algo._Policy_.impls
)
@pytest.mark.parametrize(
    "recency_proportional_resolution",
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
def test_GetEvalCtor(impl, recency_proportional_resolution):
    spec = impl(recency_proportional_resolution)
    eval_ctor = spec.GetEvalCtor()
    assert eval_ctor.startswith(
        "hstrat.recency_proportional_resolution_algo.Policy("
    )
    assert eval_ctor.endswith(")")
    reconstituted = eval(eval_ctor)
    assert str(spec) == str(reconstituted)


@pytest.mark.parametrize(
    "recency_proportional_resolution",
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
def test_GetEvalCtor_consistency(recency_proportional_resolution):
    assert (
        len(
            set(
                impl(recency_proportional_resolution).GetEvalCtor()
                for impl in recency_proportional_resolution_algo._Policy_.impls
            )
        )
        == 1
    )


@pytest.mark.parametrize(
    "recency_proportional_resolution",
    [
        0,
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_pickle(recency_proportional_resolution):
    original = recency_proportional_resolution_algo.Policy(
        recency_proportional_resolution
    )
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


@pytest.mark.parametrize(
    "impl",
    recency_proportional_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "recency_proportional_resolution",
    [
        0,
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_GetSpec(impl, recency_proportional_resolution):
    spec = impl(recency_proportional_resolution).GetSpec()
    assert spec == type(spec)(recency_proportional_resolution)


@pytest.mark.parametrize(
    "impl",
    recency_proportional_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "recency_proportional_resolution",
    [
        0,
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_WithoutCalcRankAtColumnIndex(impl, recency_proportional_resolution):

    original = impl(recency_proportional_resolution)
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
        impl(recency_proportional_resolution).WithoutCalcRankAtColumnIndex()
        == stripped
    )


@pytest.mark.parametrize(
    "impl",
    recency_proportional_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "recency_proportional_resolution",
    [
        0,
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_repr(
    impl,
    recency_proportional_resolution,
):
    policy = impl(recency_proportional_resolution)
    assert str(recency_proportional_resolution) in repr(policy)
    assert policy.GetSpec().GetAlgoIdentifier() in repr(policy)


@pytest.mark.parametrize(
    "impl",
    recency_proportional_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "recency_proportional_resolution",
    [
        0,
        1,
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_str(
    impl,
    recency_proportional_resolution,
):
    policy = impl(recency_proportional_resolution)
    assert str(recency_proportional_resolution) in str(policy)
    assert policy.GetSpec().GetAlgoTitle() in str(policy)


@pytest.mark.parametrize(
    "recency_proportional_resolution",
    [
        0,
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
def test_consistency(recency_proportional_resolution, what):
    assert (
        len(
            {
                what(impl(recency_proportional_resolution))
                for impl in recency_proportional_resolution_algo._Policy_.impls
            }
        )
        == 1
    )