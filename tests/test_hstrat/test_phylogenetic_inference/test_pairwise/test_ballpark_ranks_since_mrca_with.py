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
    "wrap",
    [lambda x: x, hstrat.col_to_specimen],
)
def test_ballpark_ranks_since_mrca_with(
    retention_policy, differentia_width, wrap
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=retention_policy,
        stratum_differentia_bit_width=differentia_width,
    )
    column2 = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=retention_policy,
        stratum_differentia_bit_width=differentia_width,
    )
    column.DepositStrata(25)

    child1 = column.CloneDescendant()
    child2 = column.CloneDescendant()
    grandchild = child1.CloneNthDescendant(20)

    for first, second in it.product(
        *[[column, column2, child1, child2, grandchild]] * 2
    ):
        assert hstrat.estimate_ranks_since_mrca_with(
            wrap(first),
            wrap(second),
            estimator="maximum_likelihood",
            prior="arbitrary",
        ) == hstrat.ballpark_ranks_since_mrca_with(first, second)
