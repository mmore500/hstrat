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
def test_calc_ranks_since_mrca_bounds_provided_confidence_level_specimen(
    retention_policy, differentia_width
):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=retention_policy,
        stratum_differentia_bit_width=differentia_width,
    )
    column2 = hstrat.HereditaryStratigraphicColumn(
        stratum_retention_policy=retention_policy,
        stratum_differentia_bit_width=differentia_width,
    )
    column.DepositStrata(100)

    child1 = column.CloneDescendant()
    child2 = column.CloneDescendant()

    assert hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(column2),
        prior="arbitrary",
    ) == hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
        column, column2, prior="arbitrary"
    )

    assert hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(column),
        prior="arbitrary",
    ) == hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
        column, column, prior="arbitrary"
    )

    assert hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(child1),
        prior="arbitrary",
    ) == hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
        column, child1, prior="arbitrary"
    )

    assert hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
        hstrat.col_to_specimen(child1),
        hstrat.col_to_specimen(child2),
        prior="arbitrary",
    ) == hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
        child1, child2, prior="arbitrary"
    )

    child1.DepositStrata(10)
    assert hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
        hstrat.col_to_specimen(child1),
        hstrat.col_to_specimen(child2),
        prior="arbitrary",
    ) == hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
        child1, child2, prior="arbitrary"
    )


def test_CalcRanksSinceMrcaBoundsProvidedConfidenceLevel():
    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    assert (
        hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
            c1, c1, "arbitrary", 0.5
        )
        == 0.5
    )
    assert (
        hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
            c1, c1, "arbitrary", 0.6
        )
        == 0.75
    )
    assert (
        hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
            c1, c1, "arbitrary", 0.75
        )
        == 0.75
    )

    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    p = 1 / 2**64
    assert (
        hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
            c2, c2, "arbitrary", 0.5
        )
        == 1 - p
    )
    assert (
        hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
            c2, c2, "arbitrary", 0.6
        )
        == 1 - p
    )
    assert (
        hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
            c2, c2, "arbitrary", 0.75
        )
        == 1 - p
    )
    assert (
        hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
            c2, c2, "arbitrary", 0.95
        )
        == 1 - p
    )
    assert (
        hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
            c2, c2, "arbitrary", 0.99
        )
        == 1 - p
    )


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
        assert hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
            hstrat.col_to_specimen(a),
            hstrat.col_to_specimen(b),
            prior,
        ) == hstrat.calc_ranks_since_mrca_bounds_provided_confidence_level(
            a, b, prior
        )
