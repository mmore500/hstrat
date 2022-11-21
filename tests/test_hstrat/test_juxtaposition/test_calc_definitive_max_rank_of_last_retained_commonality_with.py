import itertools as it

import pytest

from hstrat import hstrat


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
def test_CalcDefinitiveMaxRankOfLastRetainedCommonalityWith1(
    ordered_store,
    differentia_width,
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=differentia_width,
        stratum_ordered_store_factory=ordered_store,
    )

    for generation in range(100):
        column.DepositStratum()

    offspring1 = column.CloneDescendant()
    offspring2 = column.CloneDescendant()

    for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
        if differentia_width == 64:
            assert (
                hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                    c1,
                    c2,
                )
                == column.GetNumStrataDeposited() - 1
            )
            assert (
                hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                    c2,
                    c1,
                )
                == column.GetNumStrataDeposited() - 1
            )
        else:
            assert (
                hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                    c1,
                    c2,
                )
                >= column.GetNumStrataDeposited() - 1
            )
            assert (
                hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                    c2,
                    c1,
                )
                >= column.GetNumStrataDeposited() - 1
            )

    for c in [column, offspring1, offspring2]:
        assert (
            hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                c, c
            )
            == c.GetNumStrataDeposited() - 1
        )

    for generation in range(100):
        offspring1.DepositStratum()
        offspring2.DepositStratum()

    for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
        if differentia_width == 64:
            assert (
                hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                    c1,
                    c2,
                )
                == column.GetNumStrataDeposited() - 1
            )
            assert (
                hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                    c2,
                    c1,
                )
                == column.GetNumStrataDeposited() - 1
            )
        else:
            assert (
                hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                    c1,
                    c2,
                )
                >= column.GetNumStrataDeposited() - 1
            )
            assert (
                hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                    c2,
                    c1,
                )
                >= column.GetNumStrataDeposited() - 1
            )

    for c in [column, offspring1, offspring2]:
        assert (
            hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                c, c
            )
            == c.GetNumStrataDeposited() - 1
        )


@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_CalcDefinitiveMaxRankOfLastRetainedCommonalityWith2(ordered_store):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )

    while True:
        offspring1 = column.CloneDescendant()
        offspring2 = column.CloneDescendant()
        res = hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
            offspring1,
            offspring2,
        )
        if res is not None and res > column.GetNumStrataDeposited() - 1:
            assert (
                hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                    offspring2,
                    offspring1,
                )
                == res
            )
            break


@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_CalcDefinitiveMaxRankOfLastRetainedCommonalityWith3(ordered_store):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
        stratum_retention_policy=hstrat.nominal_resolution_algo.Policy(),
    )

    for generation in range(100):
        column.DepositStratum()

    offspring1 = column.CloneDescendant()
    offspring2 = column.CloneDescendant()

    for generation in range(100):
        offspring1.DepositStratum()
        offspring2.DepositStratum()

    for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
        assert c1.GetNumStrataRetained() == 2
        assert c2.GetNumStrataRetained() == 2

        assert (
            hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                c1,
                c2,
            )
            == 0
        )
        assert (
            hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                c2,
                c1,
            )
            == 0
        )


@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_CalcDefinitiveMaxRankOfLastRetainedCommonalityWith4(ordered_store):
    def do_once():
        c1 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
        )
        c2 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
        )

        res = hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
            c1,
            c2,
        )
        assert (
            hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                c2,
                c1,
            )
            == res
        )
        assert res in (None, 0)

        if res is None:
            for generation in range(100):
                c1.DepositStratum()
                c2.DepositStratum()
            res = hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                c1, c2
            )
            assert res is None
            assert (
                hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                    c2,
                    c1,
                )
                is None
            )
        elif res == 0:
            while True:
                c1_ = c1.CloneDescendant()
                c2_ = c2.CloneDescendant()
                if (
                    hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                        c1_, c2_
                    )
                    == 1
                ):
                    break

        return res

    while do_once() is not None:
        pass

    while do_once() != 0:
        pass


@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_CalcDefinitiveMaxRankOfLastRetainedCommonalityWith5(ordered_store):
    def do_once():
        c1 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
            stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(2),
        )
        c2 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
            stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(2),
        )

        res = hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
            c1,
            c2,
        )
        assert (
            hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                c2,
                c1,
            )
            == res
        )
        assert res in (None, 0)

        if res is None:
            for generation in range(100):
                c1.DepositStratum()
                c2.DepositStratum()
            res = hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                c1, c2
            )
            assert res is None
            assert (
                hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                    c2,
                    c1,
                )
                is None
            )
        elif res == 0:
            while True:
                c1_ = c1.CloneDescendant()
                c2_ = c2.CloneDescendant()
                c1_.DepositStratum()
                c2_.DepositStratum()
                if (
                    hstrat.calc_definitive_max_rank_of_last_retained_commonality_between(
                        c1_, c2_
                    )
                    == 2
                ):
                    break

        return res

    while do_once() is not None:
        pass

    while do_once() != 0:
        pass
