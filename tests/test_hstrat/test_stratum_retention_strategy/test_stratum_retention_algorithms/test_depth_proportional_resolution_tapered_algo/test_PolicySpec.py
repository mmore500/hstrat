import pickle
import tempfile

import pytest

from hstrat import hstrat
from hstrat.hstrat import depth_proportional_resolution_tapered_algo


@pytest.mark.parametrize(
    "impl", depth_proportional_resolution_tapered_algo._PolicySpec_.impls
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
    spec = impl(depth_proportional_resolution)
    assert spec == spec
    assert spec == impl(depth_proportional_resolution)
    assert not spec == impl(depth_proportional_resolution + 1)


@pytest.mark.parametrize(
    "impl", depth_proportional_resolution_tapered_algo._PolicySpec_.impls
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
    # hstrat. is needed for eval()
    from hstrat import hstrat  # noqa

    spec = impl(depth_proportional_resolution)
    eval_ctor = spec.GetEvalCtor()
    assert eval_ctor.startswith(
        "hstrat.depth_proportional_resolution_tapered_algo.PolicySpec("
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
                for impl in depth_proportional_resolution_tapered_algo._PolicySpec_.impls
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
    original = depth_proportional_resolution_tapered_algo.PolicySpec(
        depth_proportional_resolution
    )
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


@pytest.mark.parametrize(
    "impl", depth_proportional_resolution_tapered_algo._PolicySpec_.impls
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
def test_GetFixedResolution(impl, depth_proportional_resolution):
    spec = impl(depth_proportional_resolution)
    assert (
        spec.GetDepthProportionalResolution() == depth_proportional_resolution
    )


@pytest.mark.parametrize(
    "impl", depth_proportional_resolution_tapered_algo._PolicySpec_.impls
)
def test_GetAlgoIdentifier(impl):
    depth_proportional_resolution = 1
    spec = impl(depth_proportional_resolution)
    assert spec.GetAlgoIdentifier()


@pytest.mark.parametrize(
    "impl", depth_proportional_resolution_tapered_algo._PolicySpec_.impls
)
def test_GetAlgoTitle(impl):
    depth_proportional_resolution = 1
    spec = impl(
        depth_proportional_resolution,
    )
    assert spec.GetAlgoTitle()


@pytest.mark.parametrize(
    "impl", depth_proportional_resolution_tapered_algo._PolicySpec_.impls
)
def test_repr(impl):
    depth_proportional_resolution = 1
    spec = impl(
        depth_proportional_resolution,
    )
    assert str(depth_proportional_resolution) in repr(spec)
    assert spec.GetAlgoIdentifier() in repr(spec)


@pytest.mark.parametrize(
    "impl", depth_proportional_resolution_tapered_algo._PolicySpec_.impls
)
def test_str(impl):
    depth_proportional_resolution = 1
    spec = impl(
        depth_proportional_resolution,
    )
    assert str(depth_proportional_resolution) in str(spec)
    assert spec.GetAlgoTitle() in str(spec)


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
        lambda x: x.GetDepthProportionalResolution(),
        lambda x: x.GetAlgoIdentifier(),
        lambda x: x.GetAlgoTitle(),
        lambda x: str(x),
    ],
)
def test_consistency(depth_proportional_resolution, what):
    assert (
        len(
            {
                what(impl(depth_proportional_resolution))
                for impl in depth_proportional_resolution_tapered_algo._PolicySpec_.impls
            }
        )
        == 1
    )
