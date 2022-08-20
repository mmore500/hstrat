import pytest

from hstrat.hstrat import recency_proportional_resolution_policy


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
def test_eq(recency_proportional_resolution):
    spec = recency_proportional_resolution_policy.PolicySpec(
        recency_proportional_resolution
    )
    assert spec == spec
    assert spec == recency_proportional_resolution_policy.PolicySpec(
        recency_proportional_resolution
    )
    assert not spec == recency_proportional_resolution_policy.PolicySpec(
        recency_proportional_resolution + 1
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
def test_init(recency_proportional_resolution):
    spec = recency_proportional_resolution_policy.PolicySpec(
        recency_proportional_resolution
    )
    assert (
        spec._guaranteed_mrca_recency_proportional_resolution
        == recency_proportional_resolution
    )


def test_GetPolicyName():
    recency_proportional_resolution = 1
    spec = recency_proportional_resolution_policy.PolicySpec(
        recency_proportional_resolution
    )
    assert spec.GetPolicyName()


def test_GetPolicyTitle():
    recency_proportional_resolution = 1
    spec = recency_proportional_resolution_policy.PolicySpec(
        recency_proportional_resolution
    )
    assert spec.GetPolicyTitle()


def test_repr():
    recency_proportional_resolution = 1
    spec = recency_proportional_resolution_policy.PolicySpec(
        recency_proportional_resolution
    )
    assert str(recency_proportional_resolution) in repr(spec)
    assert spec.GetPolicyName() in repr(spec)


def test_str():
    recency_proportional_resolution = 1
    spec = recency_proportional_resolution_policy.PolicySpec(
        recency_proportional_resolution
    )
    assert str(recency_proportional_resolution) in str(spec)
    assert spec.GetPolicyTitle() in str(spec)
