import operator

import pytest

from hstrat import hstrat


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=4
        ),
    ],
)
@pytest.mark.parametrize(
    "num_deposits",
    [0, 1, 6, 8, 64, 65],
)
@pytest.mark.parametrize(
    "differentia_bit_width",
    [1, 2, 8, 20, 32, 64, 129],
)
def test_col_to_specimen(
    retention_policy,
    num_deposits,
    differentia_bit_width,
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=retention_policy,
        stratum_differentia_bit_width=differentia_bit_width,
    ).CloneNthDescendant(num_deposits)

    specimen = hstrat.col_to_specimen(column)
    assert all(
        map(
            lambda x: operator.eq(*x),
            zip(column.IterRetainedRanks(), specimen.GetRankIndex()),
        )
    )
    assert all(
        map(
            lambda x: operator.eq(*x),
            zip(
                column.IterRetainedDifferentia(), specimen.GetDifferentiaVals()
            ),
        )
    )
