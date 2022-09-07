from copy import deepcopy
import itertools as it
import random

from iterify import cyclify, iterify
import opytional as opyt
import pytest
from scipy import stats

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
def test_CalcDefinitiveMaxRankOfFirstRetainedDisparityWith1(
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
                hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                    c1,
                    c2,
                )
                == column.GetNumStrataDeposited()
            )
            assert (
                hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                    c2,
                    c1,
                )
                == column.GetNumStrataDeposited()
            )
        else:
            assert hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                c1,
                c2,
            ) in (
                column.GetNumStrataDeposited(),
                None,
            )
            assert hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                c2,
                c1,
            ) in (
                column.GetNumStrataDeposited(),
                None,
            )

    for c in [column, offspring1, offspring2]:
        assert (
            hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                c, c
            )
            is None
        )

    for generation in range(100):
        offspring1.DepositStratum()
        offspring2.DepositStratum()

    for c1, c2 in it.combinations([column, offspring1, offspring2], 2):
        if differentia_width == 64:
            assert (
                hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                    c1,
                    c2,
                )
                == column.GetNumStrataDeposited()
            )
            assert (
                hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                    c2,
                    c1,
                )
                == column.GetNumStrataDeposited()
            )
        else:
            res = hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                c1,
                c2,
            )
            assert res >= column.GetNumStrataDeposited()
            assert (
                hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                    c2,
                    c1,
                )
                == res
            )

    for c in [column, offspring1, offspring2]:
        assert (
            hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                c, c
            )
            is None
        )


@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def _do_test_CalcDefinitiveMaxRankOfFirstRetainedDisparityWith2(ordered_store):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )

    while True:
        offspring1 = column.CloneDescendant()
        offspring2 = column.CloneDescendant()
        res = hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
            offspring1,
            offspring2,
        )
        if res is not None and res == column.GetNumStrataDeposited():
            assert (
                hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
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
def test_CalcDefinitiveMaxRankOfFirstRetainedDisparityWith3(ordered_store):
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

    assert (
        offspring1.GetNumStrataDeposited()
        == offspring2.GetNumStrataDeposited()
    )
    assert (
        hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
            offspring1,
            offspring2,
        )
        == offspring1.GetNumStrataDeposited() - 1
    )
    assert (
        hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
            offspring2,
            offspring1,
        )
        == offspring1.GetNumStrataDeposited() - 1
    )

    for c in [offspring1, offspring2]:
        assert (
            hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                c,
                column,
            )
            == column.GetNumStrataDeposited()
        )
        assert (
            hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                column,
                c,
            )
            == column.GetNumStrataDeposited()
        )


@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_CalcDefinitiveMaxRankOfFirstRetainedDisparityWith4(ordered_store):
    def do_once():
        c1 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
        )
        c2 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
        )

        res = hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
            c1,
            c2,
        )
        assert (
            hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                c2,
                c1,
            )
            == res
        )
        assert res in (0, None)

        if res == 0:
            for generation in range(100):
                c1.DepositStratum()
                c2.DepositStratum()
            res = hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                c1, c2
            )
            assert res == 0
            assert (
                hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                    c2,
                    c1,
                )
                == 0
            )
        elif res is None:
            while True:
                c1_ = c1.CloneDescendant()
                c2_ = c2.CloneDescendant()
                if (
                    hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                        c1_, c2_
                    )
                    is not None
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
def test_CalcDefinitiveMaxRankOfFirstRetainedDisparityWith5(ordered_store):
    def do_once():
        c1 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
            stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(2),
        )
        c2 = hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=1,
            stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(2),
        )

        res = hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
            c1,
            c2,
        )
        assert (
            hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                c2,
                c1,
            )
            == res
        )
        assert res in (0, None)

        if res == 0:
            for generation in range(100):
                c1.DepositStratum()
                c2.DepositStratum()
            res = hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                c1, c2
            )
            assert res == 0
            assert (
                hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                    c2,
                    c1,
                )
                == 0
            )
        elif res is None:
            while True:
                c1_ = c1.CloneDescendant()
                c2_ = c2.CloneDescendant()
                if (
                    hstrat.calc_definitive_max_rank_of_first_retained_disparity_between(
                        c1_, c2_
                    )
                    is not None
                ):
                    break

        return res

    while do_once() is not None:
        pass

    while do_once() != 0:
        pass
