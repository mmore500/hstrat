import itertools as it

import pytest

from hstrat import hstrat


def test_CalcDefinitiveMinRanksSinceLastRetainedCommonalityWith_specimen():
    column = hstrat.HereditaryStratigraphicColumn()
    column2 = hstrat.HereditaryStratigraphicColumn()
    column.DepositStrata(100)

    child1 = column.CloneDescendant()
    child2 = column.CloneDescendant()

    assert hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
        hstrat.col_to_specimen(column), hstrat.col_to_specimen(column2)
    ) == hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
        column, column2
    )

    assert hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
        hstrat.col_to_specimen(column), hstrat.col_to_specimen(column)
    ) == hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
        column, column
    )

    assert hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
        hstrat.col_to_specimen(column), hstrat.col_to_specimen(child1)
    ) == hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
        column, child1
    )

    assert hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
        hstrat.col_to_specimen(child1), hstrat.col_to_specimen(child2)
    ) == hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
        child1, child2
    )

    child1.DepositStrata(10)
    assert hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
        hstrat.col_to_specimen(child1), hstrat.col_to_specimen(child2)
    ) == hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
        child1, child2
    )


@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 2, 8],
)
def test_CalcDefinitiveMinRanksSinceLastRetainedCommonalityWith1(
    ordered_store,
    differentia_width,
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=differentia_width,
        stratum_ordered_store=ordered_store,
    )

    column.DepositStrata(100)

    offspring1 = column.CloneDescendant()
    offspring2 = column.CloneDescendant()

    for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
        if differentia_width == 64:
            assert (
                hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
                    c1,
                    c2,
                )
                == c1.GetNumStrataDeposited() - column.GetNumStrataDeposited()
            )
            assert (
                hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
                    c2,
                    c1,
                )
                == c2.GetNumStrataDeposited() - column.GetNumStrataDeposited()
            )
        else:
            assert hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
                c1,
                c2,
            ) in (
                c1.GetNumStrataDeposited() - column.GetNumStrataDeposited(),
                0,
            )
            assert hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
                c2,
                c1,
            ) in (
                c2.GetNumStrataDeposited() - column.GetNumStrataDeposited(),
                0,
            )

    for c in [column, offspring1, offspring2]:
        assert (
            hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
                c, c
            )
            == 0
        )

    offspring1.DepositStrata(100)
    offspring2.DepositStrata(100)

    for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
        if differentia_width == 64:
            assert (
                hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
                    c1,
                    c2,
                )
                == c1.GetNumStrataDeposited() - column.GetNumStrataDeposited()
            )
            assert (
                hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
                    c2,
                    c1,
                )
                == c2.GetNumStrataDeposited() - column.GetNumStrataDeposited()
            )
        else:
            res = hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
                c1,
                c2,
            )
            assert (
                res
                <= c1.GetNumStrataDeposited() - column.GetNumStrataDeposited()
            )

    for c in [column, offspring1, offspring2]:
        assert (
            hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
                c, c
            )
            == 0
        )


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
        assert hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
            hstrat.col_to_specimen(a),
            hstrat.col_to_specimen(b),
        ) == hstrat.calc_definitive_min_ranks_since_last_retained_commonality_with(
            a, b
        )
