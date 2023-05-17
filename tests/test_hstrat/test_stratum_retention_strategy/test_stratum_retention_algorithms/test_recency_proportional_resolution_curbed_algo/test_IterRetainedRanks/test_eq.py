import pytest

from hstrat.hstrat import recency_proportional_resolution_curbed_algo


@pytest.mark.parametrize(
    "size_curb",
    [
        2,
        3,
        7,
        42,
        97,
        100,
    ],
)
def test_eq(size_curb):
    policy = recency_proportional_resolution_curbed_algo.Policy(size_curb)
    spec = policy.GetSpec()
    instance = recency_proportional_resolution_curbed_algo.IterRetainedRanks(
        spec
    )

    assert instance == instance
    assert (
        instance
        == recency_proportional_resolution_curbed_algo.IterRetainedRanks(spec)
    )
    assert instance is not None
