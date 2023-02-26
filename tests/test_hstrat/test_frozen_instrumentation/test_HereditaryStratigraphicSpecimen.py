import copy

import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "differentia_bit_width", [1, 2, 7, 8, 16, 32, 64, 129]
)
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
def test_init_and_getters(differentia_bit_width, retention_policy):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=differentia_bit_width,
        stratum_retention_policy=retention_policy,
    )
    for i in range(100):

        specimen = hstrat.col_to_specimen(column)
        assert specimen.GetNumStrataDeposited() == i + 1
        assert (
            specimen.GetStratumDifferentiaBitWidth()
            == column.GetStratumDifferentiaBitWidth()
        )
        assert specimen.GetNumStrataRetained() == column.GetNumStrataRetained()
        assert [*specimen.GetDifferentiaVals()] == [
            *column.IterRetainedDifferentia()
        ]
        assert [*specimen.GetRankIndex()] == [*column.IterRetainedRanks()]

        assert [*specimen.GetData()] == [*column.IterRetainedDifferentia()]
        assert [*specimen.GetData().index] == [*column.IterRetainedRanks()]

        for index in range(column.GetNumStrataRetained()):
            assert specimen.GetRankAtColumnIndex(
                index
            ) == column.GetRankAtColumnIndex(index)

        assert [*specimen.IterRetainedRanks()] == [*column.IterRetainedRanks()]
        assert [*specimen.IterRetainedDifferentia()] == [
            *column.IterRetainedDifferentia()
        ]

        assert (
            specimen.GetNumDiscardedStrata() == column.GetNumDiscardedStrata()
        )
        assert specimen.HasDiscardedStrata() == column.HasDiscardedStrata()

        column.DepositStratum()


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
def test_IterRankDifferentiaZip(retention_policy):
    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=retention_policy,
    )

    for __ in range(100):
        c1.DepositStratum()
        s1 = hstrat.col_to_specimen(c1)
        assert [*s1.IterRankDifferentiaZip()] == [
            *zip(s1.IterRetainedRanks(), s1.IterRetainedDifferentia())
        ]
        iter_ = s1.IterRankDifferentiaZip(copyable=True)
        iter_copy = copy.copy(iter_)
        next(iter_copy)
        assert [*iter_copy] == [
            *zip(s1.IterRetainedRanks(), s1.IterRetainedDifferentia())
        ][1:]
        assert [*iter_] == [
            *zip(s1.IterRetainedRanks(), s1.IterRetainedDifferentia())
        ]
