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
    spec = recency_proportional_resolution_curbed_algo.PolicySpec(size_curb)
    assert spec == spec
    assert spec == recency_proportional_resolution_curbed_algo.PolicySpec(
        size_curb
    )
    assert not spec == recency_proportional_resolution_curbed_algo.PolicySpec(
        size_curb + 1
    )


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
def test_init(size_curb):
    spec = recency_proportional_resolution_curbed_algo.PolicySpec(size_curb)
    assert spec._size_curb == size_curb


def test_GetAlgoIdentifier():
    size_curb = 42
    spec = recency_proportional_resolution_curbed_algo.PolicySpec(size_curb)
    assert spec.GetAlgoIdentifier()


def test_GetAlgoTitle():
    size_curb = 42
    spec = recency_proportional_resolution_curbed_algo.PolicySpec(size_curb)
    assert spec.GetAlgoTitle()


def test_repr():
    size_curb = 42
    spec = recency_proportional_resolution_curbed_algo.PolicySpec(size_curb)
    assert str(size_curb) in repr(spec)
    assert spec.GetAlgoIdentifier() in repr(spec)


def test_str():
    size_curb = 42
    spec = recency_proportional_resolution_curbed_algo.PolicySpec(size_curb)
    assert str(size_curb) in str(spec)
    assert spec.GetAlgoTitle() in str(spec)
