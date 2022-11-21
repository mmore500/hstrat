import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_HasAnyCommonAncestorWith(retention_policy, ordered_store):
    first = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )
    first_copy = first.Clone()
    second = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store_factory=ordered_store,
        stratum_retention_policy=retention_policy,
    )

    def assert_validity():
        assert hstrat.does_have_any_common_ancestor(first, first)
        assert hstrat.does_have_any_common_ancestor(first_copy, first_copy)
        assert hstrat.does_have_any_common_ancestor(first, first_copy)
        assert hstrat.does_have_any_common_ancestor(first_copy, first)

        assert not hstrat.does_have_any_common_ancestor(second, first)
        assert not hstrat.does_have_any_common_ancestor(first, second)
        assert not hstrat.does_have_any_common_ancestor(second, first_copy)
        assert not hstrat.does_have_any_common_ancestor(first_copy, second)

    assert_validity()
    first.DepositStratum()
    assert_validity()
    second.DepositStratum()
    assert_validity()
    first.DepositStratum()
    assert_validity()

    for __ in range(100):
        first_copy.DepositStratum()
        assert_validity()


def test_HasAnyCommonAncestorWith_narrow():
    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    assert hstrat.does_have_any_common_ancestor(c1, c2) is None
    assert hstrat.does_have_any_common_ancestor(c2, c1) is None

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    assert hstrat.does_have_any_common_ancestor(c1, c2) is False
    assert hstrat.does_have_any_common_ancestor(c2, c1) is False

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    c2 = c1.Clone()
    assert hstrat.does_have_any_common_ancestor(c1, c2) is None
    assert hstrat.does_have_any_common_ancestor(c2, c1) is None

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    c2 = c1.Clone()
    assert hstrat.does_have_any_common_ancestor(c1, c2) is True
    assert hstrat.does_have_any_common_ancestor(c2, c1) is True

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    for __ in range(100):
        c1.DepositStratum()
    c2 = c1.CloneDescendant()
    assert hstrat.does_have_any_common_ancestor(c1, c2) is True
    assert hstrat.does_have_any_common_ancestor(c2, c1) is True

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    for __ in range(100):
        c1.DepositStratum()
    c2 = c1.CloneDescendant()
    assert hstrat.does_have_any_common_ancestor(c1, c2) is True
    assert hstrat.does_have_any_common_ancestor(c2, c1) is True
