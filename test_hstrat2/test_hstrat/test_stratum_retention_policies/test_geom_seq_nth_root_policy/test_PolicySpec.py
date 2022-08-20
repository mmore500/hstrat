import pytest

from hstrat2.hstrat import geom_seq_nth_root_policy


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
    spec = geom_seq_nth_root_policy.PolicySpec(degree, interspersal)
    assert spec == spec
    assert spec == geom_seq_nth_root_policy.PolicySpec(degree, interspersal)
    assert not spec == geom_seq_nth_root_policy.PolicySpec(
        degree, interspersal + 1
    )
    assert not spec == geom_seq_nth_root_policy.PolicySpec(
        degree + 1, interspersal
    )
    assert not spec == geom_seq_nth_root_policy.PolicySpec(
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
def test_init(degree, interspersal):
    spec = geom_seq_nth_root_policy.PolicySpec(degree, interspersal)
    assert spec._degree == degree
    assert spec._interspersal == interspersal


def test_GetPolicyName():
    degree = 1
    interspersal = 2
    spec = geom_seq_nth_root_policy.PolicySpec(degree, interspersal)
    assert spec.GetPolicyName()


def test_GetPolicyTitle():
    degree = 1
    interspersal = 2
    spec = geom_seq_nth_root_policy.PolicySpec(degree, interspersal)
    assert spec.GetPolicyTitle()


def test_repr():
    degree = 1
    interspersal = 2
    spec = geom_seq_nth_root_policy.PolicySpec(degree, interspersal)
    assert str(degree) in repr(spec)
    assert str(interspersal) in repr(spec)
    assert spec.GetPolicyName() in repr(spec)


def test_str():
    degree = 1
    interspersal = 2
    spec = geom_seq_nth_root_policy.PolicySpec(degree, interspersal)
    assert str(degree) in str(spec)
    assert str(interspersal) in str(spec)
    assert spec.GetPolicyTitle() in str(spec)
