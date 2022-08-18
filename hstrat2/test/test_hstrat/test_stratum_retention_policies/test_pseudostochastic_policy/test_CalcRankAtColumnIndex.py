import pytest

from hstrat2.hstrat import pseudostochastic_policy


@pytest.mark.parametrize(
    "random_seed",
    [
        1,
        2,
        3,
        7,
        42,
        100,
    ],
)
def test_policy_consistency(random_seed):
    policy = pseudostochastic_policy.Policy(random_seed)
    spec = policy.GetSpec()
    assert pseudostochastic_policy.CalcRankAtColumnIndex is None
