import pickle
import tempfile

import pytest

from hstrat.hstrat import depth_proportional_resolution_algo


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
def test_eq(depth_proportional_resolution):
    spec = depth_proportional_resolution_algo.PolicySpec(
        depth_proportional_resolution
    )
    assert spec == spec
    assert spec == depth_proportional_resolution_algo.PolicySpec(
        depth_proportional_resolution
    )
    assert not spec == depth_proportional_resolution_algo.PolicySpec(
        depth_proportional_resolution + 1
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
def test_GetEvalCtor(depth_proportional_resolution):
    # hstrat. is needed for eval()
    from hstrat import hstrat  # noqa

    spec = depth_proportional_resolution_algo.PolicySpec(
        depth_proportional_resolution
    )
    eval_ctor = spec.GetEvalCtor()
    assert eval_ctor.startswith(
        "hstrat.depth_proportional_resolution_algo.PolicySpec("
    )
    assert eval_ctor.endswith(")")
    reconstituted = eval(eval_ctor)  # noqa
    assert spec == reconstituted


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
    original = depth_proportional_resolution_algo.PolicySpec(
        depth_proportional_resolution
    )
    with tempfile.TemporaryDirectory() as tmp_path:
        with open(f"{tmp_path}/data", "wb") as tmp_file:
            pickle.dump(original, tmp_file)

        with open(f"{tmp_path}/data", "rb") as tmp_file:
            reconstituted = pickle.load(tmp_file)
            assert reconstituted == original


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
def test_GetDepthProportionalResolution(depth_proportional_resolution):
    spec = depth_proportional_resolution_algo.PolicySpec(
        depth_proportional_resolution
    )
    assert (
        spec.GetDepthProportionalResolution() == depth_proportional_resolution
    )


def test_GetAlgoIdentifier():
    depth_proportional_resolution = 1
    spec = depth_proportional_resolution_algo.PolicySpec(
        depth_proportional_resolution,
    )
    assert spec.GetAlgoIdentifier()


def test_GetAlgoTitle():
    depth_proportional_resolution = 1
    spec = depth_proportional_resolution_algo.PolicySpec(
        depth_proportional_resolution,
    )
    assert spec.GetAlgoTitle()


def test_repr():
    depth_proportional_resolution = 1
    spec = depth_proportional_resolution_algo.PolicySpec(
        depth_proportional_resolution,
    )
    assert str(depth_proportional_resolution) in repr(spec)
    assert spec.GetAlgoIdentifier() in repr(spec)


def test_str():
    depth_proportional_resolution = 1
    spec = depth_proportional_resolution_algo.PolicySpec(
        depth_proportional_resolution,
    )
    assert str(depth_proportional_resolution) in str(spec)
    assert spec.GetAlgoTitle() in str(spec)
