import pytest

from hstrat2.hstrat import fixed_resolution_policy


@pytest.mark.parametrize(
    'fixed_resolution',
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
    spec = fixed_resolution_policy.PolicySpec(fixed_resolution)
    assert spec == spec
    assert spec == fixed_resolution_policy.PolicySpec(fixed_resolution)
    assert not spec == fixed_resolution_policy.PolicySpec(fixed_resolution + 1)

@pytest.mark.parametrize(
    'fixed_resolution',
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_init(fixed_resolution):
    spec = fixed_resolution_policy.PolicySpec(fixed_resolution)
    assert spec._fixed_resolution == fixed_resolution

def test_GetPolicyName():
    fixed_resolution = 1
    spec = fixed_resolution_policy.PolicySpec(fixed_resolution)
    assert spec.GetPolicyName()

def test_GetPolicyTitle():
    fixed_resolution = 1
    spec = fixed_resolution_policy.PolicySpec(fixed_resolution)
    assert spec.GetPolicyTitle()

def test_repr():
    fixed_resolution = 1
    spec = fixed_resolution_policy.PolicySpec(fixed_resolution)
    assert str(fixed_resolution) in repr(spec)
    assert spec.GetPolicyName() in repr(spec)

def test_str():
    fixed_resolution = 1
    spec = fixed_resolution_policy.PolicySpec(fixed_resolution)
    assert str(fixed_resolution) in str(spec)
    assert spec.GetPolicyTitle() in str(spec)
