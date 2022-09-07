import itertools as it

import pytest

from hstrat import hstrat


def test_GetNthCommonRankWith():
    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )
    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=hstrat.nominal_resolution_algo.Policy(),
    )
    c3 = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=hstrat.fixed_resolution_algo.Policy(2),
    )
    for __ in range(42):
        c1.DepositStratum()

    for __ in range(9):
        c2.DepositStratum()

    for __ in range(100):
        c3.DepositStratum()

    for col in c1, c2, c3:
        for i in range(col.GetNumStrataRetained()):
            assert col.GetRankAtColumnIndex(
                i
            ) == hstrat.get_nth_common_rank_between(col, col, i)
        assert (
            hstrat.get_nth_common_rank_between(
                col, col, col.GetNumStrataRetained()
            )
            is None
        )

    for x1, x2 in it.combinations([c1, c2, c3], 2):
        assert hstrat.get_nth_common_rank_between(x1, x2, 0) == 0

    assert (
        hstrat.get_nth_common_rank_between(c1, c2, 1)
        == c2.GetNumStrataDeposited() - 1
    )
    assert (
        hstrat.get_nth_common_rank_between(c2, c1, 1)
        == c2.GetNumStrataDeposited() - 1
    )

    assert hstrat.get_nth_common_rank_between(c1, c2, 2) is None
    assert hstrat.get_nth_common_rank_between(c2, c1, 2) is None

    assert hstrat.get_nth_common_rank_between(c1, c3, 1) == 2
    assert hstrat.get_nth_common_rank_between(c3, c1, 1) == 2

    assert hstrat.get_nth_common_rank_between(c1, c3, 2) == 4
    assert hstrat.get_nth_common_rank_between(c3, c1, 2) == 4
