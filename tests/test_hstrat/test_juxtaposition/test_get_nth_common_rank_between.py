import itertools as it

import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "wrap",
    [
        lambda x: x,
        hstrat.col_to_specimen,
    ],
)
def test_GetNthCommonRankWith(wrap):
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
            ) == hstrat.get_nth_common_rank_between(wrap(col), wrap(col), i)
        assert (
            hstrat.get_nth_common_rank_between(
                wrap(col), wrap(col), col.GetNumStrataRetained()
            )
            is None
        )

    for x1, x2 in it.combinations([c1, c2, c3], 2):
        assert hstrat.get_nth_common_rank_between(wrap(x1), wrap(x2), 0) == 0

    assert (
        hstrat.get_nth_common_rank_between(wrap(c1), wrap(c2), 1)
        == c2.GetNumStrataDeposited() - 1
    )
    assert (
        hstrat.get_nth_common_rank_between(wrap(c2), wrap(c1), 1)
        == c2.GetNumStrataDeposited() - 1
    )

    assert hstrat.get_nth_common_rank_between(wrap(c1), wrap(c2), 2) is None
    assert hstrat.get_nth_common_rank_between(wrap(c2), wrap(c1), 2) is None

    assert hstrat.get_nth_common_rank_between(wrap(c1), wrap(c3), 1) == 2
    assert hstrat.get_nth_common_rank_between(wrap(c3), wrap(c1), 1) == 2

    assert hstrat.get_nth_common_rank_between(wrap(c1), wrap(c3), 2) == 4
    assert hstrat.get_nth_common_rank_between(wrap(c3), wrap(c1), 2) == 4


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
        for n in range(10):
            assert hstrat.get_nth_common_rank_between(
                hstrat.col_to_specimen(a),
                hstrat.col_to_specimen(b),
                n,
            ) == hstrat.get_nth_common_rank_between(a, b, n)
