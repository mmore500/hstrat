import itertools as it

import pytest

from hstrat import hstrat


def test_CalcDefinitiveMinRanksSinceLastRetainedCommonalityWith_specimen():
    column = hstrat.HereditaryStratigraphicColumn()
    for generation in range(100):
        column.DepositStratum()

    child1 = column.CloneDescendant()
    child2 = column.CloneDescendant()

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

    for generation in range(100):
        column.DepositStratum()

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

    for generation in range(100):
        offspring1.DepositStratum()
        offspring2.DepositStratum()

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
