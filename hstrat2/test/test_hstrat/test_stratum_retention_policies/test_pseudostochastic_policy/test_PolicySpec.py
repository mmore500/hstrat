import pytest

from hstrat2.hstrat import pseudostochastic_policy


@pytest.mark.parametrize(
    'random_seed',
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_eq(random_seed):
    spec = pseudostochastic_policy.PolicySpec(random_seed)
    assert spec == spec
    assert spec == pseudostochastic_policy.PolicySpec(random_seed)
    assert not spec == pseudostochastic_policy.PolicySpec(random_seed + 1)

@pytest.mark.parametrize(
    'random_seed',
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_init(random_seed):
    spec = pseudostochastic_policy.PolicySpec(random_seed)
    assert spec._random_seed == random_seed

def test_GetPolicyName():
    random_seed = 1
    spec = pseudostochastic_policy.PolicySpec(random_seed)
    assert spec.GetPolicyName()

def test_GetPolicyTitle():
    random_seed = 1
    spec = pseudostochastic_policy.PolicySpec(random_seed)
    assert spec.GetPolicyTitle()

def test_repr():
    random_seed = 1
    spec = pseudostochastic_policy.PolicySpec(random_seed)
    assert str(random_seed) in repr(spec)
    assert spec.GetPolicyName() in repr(spec)

def test_str():
    random_seed = 1
    spec = pseudostochastic_policy.PolicySpec(random_seed)
    assert str(random_seed) in str(spec)
    assert spec.GetPolicyTitle() in str(spec)
