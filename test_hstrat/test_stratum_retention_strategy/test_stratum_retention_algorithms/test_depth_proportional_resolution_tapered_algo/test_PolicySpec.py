import pytest

from hstrat.hstrat import depth_proportional_resolution_tapered_algo


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
    spec = depth_proportional_resolution_tapered_algo.PolicySpec(
        depth_proportional_resolution
    )
    assert spec == spec
    assert spec == depth_proportional_resolution_tapered_algo.PolicySpec(
        depth_proportional_resolution
    )
    assert not spec == depth_proportional_resolution_tapered_algo.PolicySpec(
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
        100,
    ],
)
def test_GetFixedResolution(depth_proportional_resolution):
    spec = depth_proportional_resolution_tapered_algo.PolicySpec(
        depth_proportional_resolution
    )
    assert (
        spec.GetDepthProportionalResolution() == depth_proportional_resolution
    )


def test_GetAlgoIdentifier():
    depth_proportional_resolution = 1
    spec = depth_proportional_resolution_tapered_algo.PolicySpec(
        depth_proportional_resolution,
    )
    assert spec.GetAlgoIdentifier()


def test_GetAlgoTitle():
    depth_proportional_resolution = 1
    spec = depth_proportional_resolution_tapered_algo.PolicySpec(
        depth_proportional_resolution,
    )
    assert spec.GetAlgoTitle()


def test_repr():
    depth_proportional_resolution = 1
    spec = depth_proportional_resolution_tapered_algo.PolicySpec(
        depth_proportional_resolution,
    )
    assert str(depth_proportional_resolution) in repr(spec)
    assert spec.GetAlgoIdentifier() in repr(spec)


def test_str():
    depth_proportional_resolution = 1
    spec = depth_proportional_resolution_tapered_algo.PolicySpec(
        depth_proportional_resolution,
    )
    assert str(depth_proportional_resolution) in str(spec)
    assert spec.GetAlgoTitle() in str(spec)
