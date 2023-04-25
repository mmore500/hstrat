import itertools as it

import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=2
        ),
    ],
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 2, 8, 64],
)
@pytest.mark.parametrize(
    "confidence_level",
    [0.95, 0.88],
)
def test_does_have_any_common_ancestor_specimen(
    retention_policy, differentia_width, confidence_level
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=retention_policy,
        stratum_differentia_bit_width=differentia_width,
    )
    column2 = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=retention_policy,
        stratum_differentia_bit_width=differentia_width,
    )
    column.DepositStrata(100)

    child1 = column.CloneDescendant()
    child2 = column.CloneDescendant()

    assert hstrat.does_have_any_common_ancestor(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(column2),
        confidence_level=confidence_level,
    ) == hstrat.does_have_any_common_ancestor(
        column, column2, confidence_level=confidence_level
    )

    assert hstrat.does_have_any_common_ancestor(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(column),
        confidence_level=confidence_level,
    ) == hstrat.does_have_any_common_ancestor(
        column, column, confidence_level=confidence_level
    )

    assert hstrat.does_have_any_common_ancestor(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(child1),
        confidence_level=confidence_level,
    ) == hstrat.does_have_any_common_ancestor(
        column, child1, confidence_level=confidence_level
    )

    assert hstrat.does_have_any_common_ancestor(
        hstrat.col_to_specimen(child1),
        hstrat.col_to_specimen(child2),
        confidence_level=confidence_level,
    ) == hstrat.does_have_any_common_ancestor(
        child1, child2, confidence_level=confidence_level
    )

    child1.DepositStrata(10)
    assert hstrat.does_have_any_common_ancestor(
        hstrat.col_to_specimen(child1),
        hstrat.col_to_specimen(child2),
        confidence_level=confidence_level,
    ) == hstrat.does_have_any_common_ancestor(
        child1, child2, confidence_level=confidence_level
    )


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
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy,
    )
    first_copy = first.Clone()
    second = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store=ordered_store,
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


@pytest.mark.parametrize(
    "differentia_width",
    [1, 8, 64],
)
@pytest.mark.parametrize(
    "policy",
    [
        hstrat.fixed_resolution_algo.Policy(3),
        hstrat.recency_proportional_resolution_algo.Policy(1),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.perfect_resolution_algo.Policy(),
    ],
)
def test_artifact_types_equiv(differentia_width, policy):
    common_ancestor = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_differentia_bit_width=differentia_width,
    ).CloneNthDescendant(7)
    c1 = common_ancestor.CloneNthDescendant(4)
    c2 = common_ancestor.CloneNthDescendant(9)
    c_x = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_differentia_bit_width=differentia_width,
    ).CloneNthDescendant(7)
    c_y = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=policy,
        stratum_differentia_bit_width=differentia_width,
    )

    for a, b in it.product(
        [common_ancestor, c1, c2, c_x, c_y],
        [common_ancestor, c1, c2, c_x, c_y],
    ):
        assert hstrat.does_have_any_common_ancestor(
            hstrat.col_to_specimen(a),
            hstrat.col_to_specimen(b),
        ) == hstrat.does_have_any_common_ancestor(a, b)
