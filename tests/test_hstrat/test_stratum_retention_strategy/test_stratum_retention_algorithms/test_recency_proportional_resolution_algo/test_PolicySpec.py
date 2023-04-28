import pickle
import tempfile

import pytest

from hstrat.hstrat import recency_proportional_resolution_algo


@pytest.mark.parametrize(
    "impl", recency_proportional_resolution_algo._PolicySpec_.impls
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
    spec = impl(recency_proportional_resolution)
    assert spec == spec
    assert spec == impl(recency_proportional_resolution)
    assert not spec == impl(recency_proportional_resolution + 1)


@pytest.mark.parametrize(
    "impl", recency_proportional_resolution_algo._PolicySpec_.impls
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
    # hstrat. is needed for eval()
    from hstrat import hstrat  # noqa

    spec = impl(recency_proportional_resolution)
    eval_ctor = spec.GetEvalCtor()
    assert eval_ctor.startswith(
        "hstrat.recency_proportional_resolution_algo.PolicySpec("
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
                for impl in recency_proportional_resolution_algo._PolicySpec_.impls
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
    original = recency_proportional_resolution_algo.PolicySpec(
        recency_proportional_resolution
    )
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


@pytest.mark.parametrize(
    "impl", recency_proportional_resolution_algo._PolicySpec_.impls
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
def test_GetRecencyProportionalResolution(
    impl, recency_proportional_resolution
):
    spec = impl(recency_proportional_resolution)
    assert (
        spec.GetRecencyProportionalResolution()
        == recency_proportional_resolution
    )


@pytest.mark.parametrize(
    "impl", recency_proportional_resolution_algo._PolicySpec_.impls
)
def test_GetAlgoIdentifier(impl):
    recency_proportional_resolution = 1
    spec = impl(recency_proportional_resolution)
    assert spec.GetAlgoIdentifier()


@pytest.mark.parametrize(
    "impl", recency_proportional_resolution_algo._PolicySpec_.impls
)
def test_GetAlgoTitle(impl):
    recency_proportional_resolution = 1
    spec = impl(recency_proportional_resolution)
    assert spec.GetAlgoTitle()


@pytest.mark.parametrize(
    "impl", recency_proportional_resolution_algo._PolicySpec_.impls
)
def test_repr(impl):
    recency_proportional_resolution = 1
    spec = impl(recency_proportional_resolution)
    assert str(recency_proportional_resolution) in repr(spec)
    assert spec.GetAlgoIdentifier() in repr(spec)


@pytest.mark.parametrize(
    "impl", recency_proportional_resolution_algo._PolicySpec_.impls
)
def test_str(impl):
    recency_proportional_resolution = 1
    spec = impl(recency_proportional_resolution)
    assert str(recency_proportional_resolution) in str(spec)
    assert spec.GetAlgoTitle() in str(spec)


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
        lambda x: x.GetRecencyProportionalResolution(),
        lambda x: x.GetAlgoIdentifier(),
        lambda x: x.GetAlgoTitle(),
        lambda x: str(x),
    ],
)
def test_consistency(recency_proportional_resolution, what):
    assert (
        len(
            {
                what(impl(recency_proportional_resolution))
                for impl in recency_proportional_resolution_algo._PolicySpec_.impls
            }
        )
        == 1
    )
