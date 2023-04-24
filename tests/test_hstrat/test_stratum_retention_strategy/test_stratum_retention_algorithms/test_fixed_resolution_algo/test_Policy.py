import pickle
import tempfile

import pytest

from hstrat import hstrat
from hstrat.hstrat import fixed_resolution_algo


@pytest.mark.parametrize(
    "impl",
    fixed_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_init(impl, fixed_resolution):
    spec = impl(fixed_resolution).GetSpec()
    assert (
        spec
        == impl(
            policy_spec=fixed_resolution_algo.PolicySpec(fixed_resolution),
        ).GetSpec()
    )
    assert spec == impl(policy_spec=spec).GetSpec()

    policy = impl(fixed_resolution)

    # invariants
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBound)
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBoundPessimalRank)
    assert callable(policy.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank)
    assert callable(policy.CalcMrcaUncertaintyRelUpperBound)
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


@pytest.mark.parametrize("impl", fixed_resolution_algo._Policy_.impls)
@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_GetEvalCtor(impl, fixed_resolution):
    spec = impl(fixed_resolution)
    eval_ctor = spec.GetEvalCtor()
    assert eval_ctor.startswith("hstrat.fixed_resolution_algo.Policy(")
    assert eval_ctor.endswith(")")
    reconstituted = eval(eval_ctor)
    assert str(spec) == str(reconstituted)


@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_GetEvalCtor_consistency(fixed_resolution):
    assert (
        len(
            set(
                impl(fixed_resolution).GetEvalCtor()
                for impl in fixed_resolution_algo._Policy_.impls
            )
        )
        == 1
    )


@pytest.mark.parametrize(
    "impl",
    fixed_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_eq(impl, fixed_resolution):
    policy = impl(fixed_resolution)
    assert policy == policy
    assert policy == impl(fixed_resolution)
    assert not policy == policy.WithoutCalcRankAtColumnIndex()
    assert (
        policy.WithoutCalcRankAtColumnIndex()
        == policy.WithoutCalcRankAtColumnIndex()
    )
    assert not policy == fixed_resolution_algo.Policy(fixed_resolution + 1)


@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_pickle(fixed_resolution):
    original = fixed_resolution_algo.Policy(fixed_resolution)
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


@pytest.mark.parametrize(
    "impl",
    fixed_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_GetSpec(impl, fixed_resolution):
    spec = impl(fixed_resolution).GetSpec()
    assert spec == type(spec)(fixed_resolution)


@pytest.mark.parametrize(
    "impl",
    fixed_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_WithoutCalcRankAtColumnIndex(impl, fixed_resolution):

    original = impl(fixed_resolution)
    stripped = original.WithoutCalcRankAtColumnIndex()

    assert stripped.CalcRankAtColumnIndex is None

    # test chaining
    assert (
        impl(
            fixed_resolution,
        ).WithoutCalcRankAtColumnIndex()
        == stripped
    )


@pytest.mark.parametrize(
    "impl",
    fixed_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_repr(impl, fixed_resolution):
    policy = impl(fixed_resolution)
    assert str(fixed_resolution) in repr(policy)
    assert policy.GetSpec().GetAlgoIdentifier() in repr(policy)


@pytest.mark.parametrize(
    "impl",
    fixed_resolution_algo._Policy_.impls,
)
@pytest.mark.parametrize(
    "fixed_resolution",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_str(impl, fixed_resolution):
    policy = impl(fixed_resolution)
    assert str(fixed_resolution) in str(policy)
    assert policy.GetSpec().GetAlgoTitle() in str(policy)


@pytest.mark.parametrize(
    "fixed_resolution",
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
def test_consistency(fixed_resolution, what):
    assert (
        len(
            {
                what(impl(fixed_resolution))
                for impl in fixed_resolution_algo._Policy_.impls
            }
        )
        == 1
    )
