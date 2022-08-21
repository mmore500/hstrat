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
def test_init(depth_proportional_resolution):
    spec = depth_proportional_resolution_algo.PolicySpec(
        depth_proportional_resolution
    )
    assert (
        spec._guaranteed_depth_proportional_resolution
        == depth_proportional_resolution
    )


def test_GetPolicyName():
    depth_proportional_resolution = 1
    spec = depth_proportional_resolution_algo.PolicySpec(
        depth_proportional_resolution,
    )
    assert spec.GetPolicyName()


def test_GetPolicyTitle():
    depth_proportional_resolution = 1
    spec = depth_proportional_resolution_algo.PolicySpec(
        depth_proportional_resolution,
    )
    assert spec.GetPolicyTitle()


def test_repr():
    depth_proportional_resolution = 1
    spec = depth_proportional_resolution_algo.PolicySpec(
        depth_proportional_resolution,
    )
    assert str(depth_proportional_resolution) in repr(spec)
    assert spec.GetPolicyName() in repr(spec)


def test_str():
    depth_proportional_resolution = 1
    spec = depth_proportional_resolution_algo.PolicySpec(
        depth_proportional_resolution,
    )
    assert str(depth_proportional_resolution) in str(spec)
    assert spec.GetPolicyTitle() in str(spec)
