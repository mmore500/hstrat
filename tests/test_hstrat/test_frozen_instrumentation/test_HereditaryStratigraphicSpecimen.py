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
