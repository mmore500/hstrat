import pytest

from hstrat.hstrat import fixed_resolution_algo


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
def test_eq(fixed_resolution):
    spec = fixed_resolution_algo.PolicySpec(fixed_resolution)
    assert spec == spec
    assert spec == fixed_resolution_algo.PolicySpec(fixed_resolution)
    assert not spec == fixed_resolution_algo.PolicySpec(fixed_resolution + 1)


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
def test_GetFixedResolution(fixed_resolution):
    spec = fixed_resolution_algo.PolicySpec(fixed_resolution)
    assert spec.GetFixedResolution() == fixed_resolution


def test_GetAlgoIdentifier():
    fixed_resolution = 1
    spec = fixed_resolution_algo.PolicySpec(fixed_resolution)
    assert spec.GetAlgoIdentifier()


def test_GetAlgoTitle():
    fixed_resolution = 1
    spec = fixed_resolution_algo.PolicySpec(fixed_resolution)
    assert spec.GetAlgoTitle()


def test_repr():
    fixed_resolution = 1
    spec = fixed_resolution_algo.PolicySpec(fixed_resolution)
    assert str(fixed_resolution) in repr(spec)
    assert spec.GetAlgoIdentifier() in repr(spec)


def test_str():
    fixed_resolution = 1
    spec = fixed_resolution_algo.PolicySpec(fixed_resolution)
    assert str(fixed_resolution) in str(spec)
    assert spec.GetAlgoTitle() in str(spec)
