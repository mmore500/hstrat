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
def test_ballpark_patristic_distance_between(
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
        assert hstrat.estimate_patristic_distance_between(
            wrap(first),
            wrap(second),
            estimator="maximum_likelihood",
            prior="arbitrary",
        ) == hstrat.ballpark_patristic_distance_between(first, second)


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
@pytest.mark.parametrize(
    "prior",
    ["arbitrary"],
)
def test_artifact_types_equiv(differentia_width, policy, prior):
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
        assert hstrat.ballpark_patristic_distance_between(
            hstrat.col_to_specimen(a),
            hstrat.col_to_specimen(b),
        ) == hstrat.ballpark_patristic_distance_between(a, b)
