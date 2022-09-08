import pytest

from hstrat.hstrat import geom_seq_nth_root_tapered_algo


@pytest.mark.parametrize(
    "degree",
    [
        1,
        2,
        3,
        7,
        9,
        42,
        97,
        100,
    ],
)
@pytest.mark.parametrize(
    "interspersal",
    [
        1,
        2,
        5,
    ],
)
def test_eq(degree, interspersal):
    spec = geom_seq_nth_root_tapered_algo.PolicySpec(degree, interspersal)
    assert spec == spec
    assert spec == geom_seq_nth_root_tapered_algo.PolicySpec(
        degree, interspersal
    )
    assert not spec == geom_seq_nth_root_tapered_algo.PolicySpec(
        degree, interspersal + 1
    )
    assert not spec == geom_seq_nth_root_tapered_algo.PolicySpec(
        degree + 1, interspersal
    )
    assert not spec == geom_seq_nth_root_tapered_algo.PolicySpec(
        degree + 1, interspersal + 1
    )


@pytest.mark.parametrize(
    "degree",
    [
        1,
        2,
        3,
        7,
        9,
        42,
        97,
        100,
    ],
)
@pytest.mark.parametrize(
    "interspersal",
    [
        1,
        2,
        5,
    ],
)
def test_GetDegree(degree, interspersal):
    spec = geom_seq_nth_root_tapered_algo.PolicySpec(degree, interspersal)
    assert spec.GetDegree() == degree


@pytest.mark.parametrize(
    "degree",
    [
        1,
        2,
        3,
        7,
        9,
        42,
        97,
        100,
    ],
)
@pytest.mark.parametrize(
    "interspersal",
    [
        1,
        2,
        5,
    ],
)
def test_GetInterspersal(degree, interspersal):
    spec = geom_seq_nth_root_tapered_algo.PolicySpec(degree, interspersal)
    assert spec.GetInterspersal() == interspersal


def test_GetAlgoIdentifier():
    degree = 1
    interspersal = 2
    spec = geom_seq_nth_root_tapered_algo.PolicySpec(degree, interspersal)
    assert spec.GetAlgoIdentifier()


def test_GetAlgoTitle():
    degree = 1
    interspersal = 2
    spec = geom_seq_nth_root_tapered_algo.PolicySpec(degree, interspersal)
    assert spec.GetAlgoTitle()


def test_repr():
    degree = 1
    interspersal = 2
    spec = geom_seq_nth_root_tapered_algo.PolicySpec(degree, interspersal)
    assert str(degree) in repr(spec)
    assert str(interspersal) in repr(spec)
    assert spec.GetAlgoIdentifier() in repr(spec)


def test_str():
    degree = 1
    interspersal = 2
    spec = geom_seq_nth_root_tapered_algo.PolicySpec(degree, interspersal)
    assert str(degree) in str(spec)
    assert str(interspersal) in str(spec)
    assert spec.GetAlgoTitle() in str(spec)
