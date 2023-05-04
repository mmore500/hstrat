import itertools as it
import random

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
    "confidence_level",
    [0.95, 0.88],
)
def test_calc_ranks_since_mrca_uncertainty_with_specimen(
    retention_policy, differentia_width, confidence_level
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

    assert hstrat.calc_ranks_since_mrca_uncertainty_with(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(column2),
        prior="arbitrary",
        confidence_level=confidence_level,
    ) == hstrat.calc_ranks_since_mrca_uncertainty_with(
        column, column2, prior="arbitrary", confidence_level=confidence_level
    )

    assert hstrat.calc_ranks_since_mrca_uncertainty_with(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(column),
        prior="arbitrary",
        confidence_level=confidence_level,
    ) == hstrat.calc_ranks_since_mrca_uncertainty_with(
        column, column, prior="arbitrary", confidence_level=confidence_level
    )

    assert hstrat.calc_ranks_since_mrca_uncertainty_with(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(child1),
        prior="arbitrary",
        confidence_level=confidence_level,
    ) == hstrat.calc_ranks_since_mrca_uncertainty_with(
        column, child1, prior="arbitrary", confidence_level=confidence_level
    )

    assert hstrat.calc_ranks_since_mrca_uncertainty_with(
        hstrat.col_to_specimen(child1),
        hstrat.col_to_specimen(child2),
        prior="arbitrary",
        confidence_level=confidence_level,
    ) == hstrat.calc_ranks_since_mrca_uncertainty_with(
        child1, child2, prior="arbitrary", confidence_level=confidence_level
    )

    child1.DepositStrata(10)
    assert hstrat.calc_ranks_since_mrca_uncertainty_with(
        hstrat.col_to_specimen(child1),
        hstrat.col_to_specimen(child2),
        prior="arbitrary",
        confidence_level=confidence_level,
    ) == hstrat.calc_ranks_since_mrca_uncertainty_with(
        child1, child2, prior="arbitrary", confidence_level=confidence_level
    )


@pytest.mark.parametrize(
    "retention_policy",
    [
        pytest.param(
            hstrat.perfect_resolution_algo.Policy(),
            marks=pytest.mark.heavy_2a,
        ),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        pytest.param(
            hstrat.HereditaryStratumOrderedStoreDict,
            marks=pytest.mark.heavy_2b,
        ),
        hstrat.HereditaryStratumOrderedStoreList,
        pytest.param(
            hstrat.HereditaryStratumOrderedStoreTree,
            marks=pytest.mark.heavy,
        ),
    ],
)
def test_comparison_commutativity_synchronous(
    retention_policy,
    ordered_store,
):

    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store=ordered_store,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for _generation in range(100):
        _ = _generation
        for first, second in it.combinations(population, 2):
            # assert commutativity
            assert hstrat.calc_ranks_since_mrca_uncertainty_with(
                first,
                second,
                prior="arbitrary",
            ) == hstrat.calc_ranks_since_mrca_uncertainty_with(
                second, first, prior="arbitrary"
            )

        # advance generation
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].Clone()
        # synchronous generations
        for individual in population:
            individual.DepositStratum()


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        pytest.param(
            hstrat.HereditaryStratumOrderedStoreTree,
            marks=pytest.mark.heavy,
        ),
    ],
)
def test_comparison_validity(retention_policy, ordered_store):
    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store=ordered_store,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for _generation in range(100):
        _ = _generation
        for first, second in it.combinations(population, 2):
            assert (
                hstrat.calc_ranks_since_mrca_uncertainty_with(
                    first, second, prior="arbitrary"
                )
                >= 0
            )

        # advance generations asynchronously
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].Clone()
        for individual in population:
            if random.choice([True, False]):
                individual.DepositStratum()


@pytest.mark.parametrize(
    "retention_policy1",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "retention_policy2",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_scenario_no_mrca(
    retention_policy1,
    retention_policy2,
    ordered_store,
):
    first = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy1,
    )
    second = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy2,
    )

    for _generation in range(100):
        _ = _generation
        assert (
            hstrat.calc_ranks_since_mrca_uncertainty_with(
                first, second, prior="arbitrary"
            )
            == 0
        )
        assert (
            hstrat.calc_ranks_since_mrca_uncertainty_with(
                second, first, prior="arbitrary"
            )
            == 0
        )

        first.DepositStratum()
        second.DepositStratum()


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
@pytest.mark.parametrize(
    "ordered_store",
    [
        hstrat.HereditaryStratumOrderedStoreDict,
        hstrat.HereditaryStratumOrderedStoreList,
        hstrat.HereditaryStratumOrderedStoreTree,
    ],
)
def test_scenario_no_divergence(retention_policy, ordered_store):
    column = hstrat.HereditaryStratigraphicColumn(
        stratum_ordered_store=ordered_store,
        stratum_retention_policy=retention_policy,
    )

    for _generation in range(100):
        _ = _generation
        assert (
            hstrat.calc_ranks_since_mrca_uncertainty_with(
                column, column, prior="arbitrary"
            )
            == 0
        )
        column.DepositStratum()


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=10,
        ),
    ],
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 8, 64],
)
@pytest.mark.parametrize(
    "confidence_level",
    [0.95],
)
def test_CalcRanksSinceMrcaUncertaintyWith_narrow_shallow(
    retention_policy,
    differentia_width,
    confidence_level,
):
    columns = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
            stratum_ordered_store=hstrat.HereditaryStratumOrderedStoreDict,
        )
        for __ in range(20)
    ]
    steps = list(
        range(
            columns[
                0
            ].CalcMinImplausibleSpuriousConsecutiveDifferentiaCollisions(
                significance_level=1 - confidence_level,
            )
            - columns[0].GetNumStrataDeposited()
        )
    )

    for step1, step2 in it.product(steps, steps):
        column1 = [col.Clone() for col in columns]
        column2 = [col.Clone() for col in columns]
        for __ in range(step1):
            for col in column1:
                col.DepositStratum()
        for i in range(step2):
            for col in column2:
                col.DepositStratum()

        for c1, c2 in zip(column1, column2):
            assert (
                hstrat.calc_ranks_since_mrca_uncertainty_with(
                    c1,
                    c2,
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
                is None
            )
            assert (
                hstrat.calc_ranks_since_mrca_uncertainty_with(
                    c2,
                    c1,
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
                is None
            )


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=10,
        ),
    ],
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 8, 64],
)
@pytest.mark.parametrize(
    "confidence_level",
    [0.95],
)
@pytest.mark.parametrize(
    "mrca_rank",
    [100],
)
def test_CalcRanksSinceMrcaUncertaintyWith_narrow_with_mrca(
    retention_policy,
    differentia_width,
    confidence_level,
    mrca_rank,
):

    columns = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
            stratum_ordered_store=hstrat.HereditaryStratumOrderedStoreDict,
        )
        for __ in range(20)
    ]

    for column in columns:
        column.DepositStrata(mrca_rank)

    steps = (0, 16, 51)

    for step1, step2 in it.product(steps, steps):
        column1 = [col.Clone() for col in columns]
        column2 = [col.Clone() for col in columns]
        for __ in range(step1):
            for col in column1:
                col.DepositStratum()
        for i in range(step2):
            for col in column2:
                col.DepositStratum()

        for c1, c2 in zip(column1, column2):
            assert hstrat.calc_ranks_since_mrca_uncertainty_with(
                c1, c2, prior="arbitrary", confidence_level=confidence_level
            ) == hstrat.calc_ranks_since_mrca_uncertainty_with(
                c2,
                c1,
                prior="arbitrary",
                confidence_level=confidence_level,
            )
            res = hstrat.calc_ranks_since_mrca_uncertainty_with(
                c1,
                c2,
                prior="arbitrary",
                confidence_level=confidence_level,
            )

            if res is not None:
                assert res >= 0
                assert hstrat.calc_ranks_since_mrca_uncertainty_with(
                    c1,
                    c2,
                    prior="arbitrary",
                    confidence_level=confidence_level,
                ) >= hstrat.calc_ranks_since_mrca_uncertainty_with(
                    c2,
                    c1,
                    prior="arbitrary",
                    confidence_level=confidence_level / 2,
                )


@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=10,
        ),
    ],
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 8, 64],
)
@pytest.mark.parametrize(
    "confidence_level",
    [0.95],
)
@pytest.mark.parametrize(
    "mrca_rank",
    [100],
)
def test_CalcRanksSinceMrcaUncertaintyWith_narrow_no_mrca(
    retention_policy,
    differentia_width,
    confidence_level,
    mrca_rank,
):
    def make_column():
        return hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
            stratum_ordered_store=hstrat.HereditaryStratumOrderedStoreDict,
        )

    columns = [make_column() for __ in range(20)]

    for column in columns:
        column.DepositStrata(mrca_rank)

    steps = (0, 16, 51)

    for step1, step2 in it.product(steps, steps):
        column1 = [make_column() for col in columns]
        column2 = [make_column() for col in columns]
        for __ in range(step1):
            for col in column1:
                col.DepositStratum()
        for i in range(step2):
            for col in column2:
                col.DepositStratum()

        for c1, c2 in zip(column1, column2):
            assert hstrat.calc_ranks_since_mrca_uncertainty_with(
                c1, c2, prior="arbitrary", confidence_level=confidence_level
            ) == hstrat.calc_ranks_since_mrca_uncertainty_with(
                c2,
                c1,
                prior="arbitrary",
                confidence_level=confidence_level,
            )
            res = hstrat.calc_ranks_since_mrca_uncertainty_with(
                c1,
                c2,
                prior="arbitrary",
                confidence_level=confidence_level,
            )

            if res is not None:
                assert 0 <= res
                assert (
                    hstrat.calc_ranks_since_mrca_uncertainty_with(
                        c1,
                        c2,
                        prior="arbitrary",
                        confidence_level=confidence_level,
                    )
                    >= hstrat.calc_ranks_since_mrca_uncertainty_with(
                        c2,
                        c1,
                        prior="arbitrary",
                        confidence_level=confidence_level / 2,
                    )
                    or hstrat.calc_ranks_since_mrca_uncertainty_with(
                        c1,
                        c2,
                        prior="arbitrary",
                        confidence_level=confidence_level,
                    )
                    == 0
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
        assert hstrat.calc_ranks_since_mrca_uncertainty_with(
            hstrat.col_to_specimen(a),
            hstrat.col_to_specimen(b),
            prior,
        ) == hstrat.calc_ranks_since_mrca_uncertainty_with(a, b, prior)
