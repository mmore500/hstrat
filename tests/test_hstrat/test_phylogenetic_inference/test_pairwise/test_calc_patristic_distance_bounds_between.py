import itertools as it
import random

from iterify import cyclify, iterify
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
def test_calc_patristic_distance_bounds_between_specimen(
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

    assert hstrat.calc_patristic_distance_bounds_between(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(column2),
        prior="arbitrary",
        confidence_level=confidence_level,
    ) == hstrat.calc_patristic_distance_bounds_between(
        column, column2, prior="arbitrary", confidence_level=confidence_level
    )
    assert hstrat.calc_patristic_distance_bounds_between(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(column),
        prior="arbitrary",
        confidence_level=confidence_level,
    ) == hstrat.calc_patristic_distance_bounds_between(
        column, column, prior="arbitrary", confidence_level=confidence_level
    )

    assert hstrat.calc_patristic_distance_bounds_between(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(child1),
        prior="arbitrary",
        confidence_level=confidence_level,
    ) == hstrat.calc_patristic_distance_bounds_between(
        column, child1, prior="arbitrary", confidence_level=confidence_level
    )

    assert hstrat.calc_patristic_distance_bounds_between(
        hstrat.col_to_specimen(child1),
        hstrat.col_to_specimen(child2),
        prior="arbitrary",
        confidence_level=confidence_level,
    ) == hstrat.calc_patristic_distance_bounds_between(
        child1, child2, prior="arbitrary", confidence_level=confidence_level
    )

    child1.DepositStrata(10)
    assert hstrat.calc_patristic_distance_bounds_between(
        hstrat.col_to_specimen(child1),
        hstrat.col_to_specimen(child2),
        prior="arbitrary",
        confidence_level=confidence_level,
    ) == hstrat.calc_patristic_distance_bounds_between(
        child1, child2, prior="arbitrary", confidence_level=confidence_level
    )


@pytest.mark.filterwarnings(
    "ignore:Insufficient common ranks between columns to detect common ancestry at given confidence level."
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
def test_CalcRanksSinceMrcaBoundsWith(
    retention_policy,
):
    def make_bundle():
        return hstrat.HereditaryStratigraphicColumnBundle(
            {
                "test": hstrat.HereditaryStratigraphicColumn(
                    initial_stratum_annotation=0,
                    stratum_retention_policy=retention_policy,
                ),
                "control": hstrat.HereditaryStratigraphicColumn(
                    initial_stratum_annotation=0,
                    stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
                ),
            }
        )

    column = make_bundle()
    frozen_copy = column.Clone()
    frozen_unrelated = make_bundle()
    population = [column.Clone() for __ in range(10)]
    forked_isolated = column.Clone()
    unrelated_isolated = make_bundle()

    for _generation in range(100):
        _ = _generation
        for f, s in it.chain(
            it.combinations(population, 2),
            zip(population, cyclify(forked_isolated)),
            zip(population, cyclify(frozen_copy)),
            zip(cyclify(forked_isolated), population),
            zip(cyclify(frozen_copy), population),
        ):
            lb, ub = hstrat.calc_patristic_distance_bounds_between(
                f["test"],
                s["test"],
                prior="arbitrary",
            )
            actual_rank_of_mrca = hstrat.get_last_common_stratum_between(
                f["control"],
                s["control"],
            ).GetAnnotation()
            actual_patristic_distance = (
                f.GetNumStrataDeposited() - actual_rank_of_mrca - 1
            ) + (s.GetNumStrataDeposited() - actual_rank_of_mrca - 1)
            assert lb <= actual_patristic_distance < ub

        for f, s in it.chain(
            zip(population, cyclify(frozen_unrelated)),
            zip(population, cyclify(unrelated_isolated)),
            zip(cyclify(frozen_unrelated), population),
            zip(cyclify(unrelated_isolated), population),
        ):
            assert (
                hstrat.calc_patristic_distance_bounds_between(
                    f["test"],
                    s["test"],
                    prior="arbitrary",
                )
                is None
            )

        # advance generation
        random.shuffle(population)
        for target in range(3):
            population[target] = population[-1].Clone()
            population[target].DepositStratum(
                annotation=population[target].GetNumStrataDeposited(),
            )
        for individual in it.chain(
            iter(population),
            iterify(forked_isolated),
            iterify(unrelated_isolated),
        ):
            if random.choice([True, False]):
                individual.DepositStratum(
                    annotation=individual.GetNumStrataDeposited(),
                )


@pytest.mark.filterwarnings(
    "ignore:Insufficient common ranks between columns to detect common ancestry at given confidence level."
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 8, 64],
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
def test_comparison_commutativity_asynchronous(
    differentia_width,
    retention_policy,
):
    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for _generation in range(30):
        _ = _generation
        for first, second in it.combinations(population, 2):
            # assert commutativity
            assert hstrat.calc_patristic_distance_bounds_between(
                first,
                second,
                prior="arbitrary",
            ) == hstrat.calc_patristic_distance_bounds_between(
                second,
                first,
                prior="arbitrary",
            )

        # advance generation
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].CloneDescendant()
        for individual in population:
            # asynchronous generations
            if random.choice([True, False]):
                individual.DepositStratum()


@pytest.mark.filterwarnings(
    "ignore:Insufficient common ranks between columns to detect common ancestry at given confidence level."
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 8, 64],
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
def test_comparison_commutativity_synchronous(
    differentia_width,
    retention_policy,
):

    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for _generation in range(100):
        _ = _generation
        for first, second in it.combinations(population, 2):
            # assert commutativity
            assert hstrat.calc_patristic_distance_bounds_between(
                first,
                second,
                prior="arbitrary",
            ) == hstrat.calc_patristic_distance_bounds_between(
                second,
                first,
                prior="arbitrary",
            )

        # advance generation
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].Clone()
        # synchronous generations
        for individual in population:
            individual.DepositStratum()


@pytest.mark.filterwarnings(
    "ignore:Insufficient common ranks between columns to detect common ancestry at given confidence level."
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        pytest.param(
            hstrat.perfect_resolution_algo.Policy(),
            marks=pytest.mark.heavy,
        ),
        hstrat.nominal_resolution_algo.Policy(),
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
def test_comparison_validity(retention_policy, differentia_width):
    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for _generation in range(100):
        _ = _generation
        for first, second in it.permutations(population, 2):
            rsmw1 = hstrat.calc_ranks_since_mrca_bounds_with(
                first,
                second,
                prior="arbitrary",
            )
            rsmw2 = hstrat.calc_ranks_since_mrca_bounds_with(
                second,
                first,
                prior="arbitrary",
            )
            pd = hstrat.calc_patristic_distance_bounds_between(
                first,
                second,
                prior="arbitrary",
            )
            assert (rsmw1 is None) == (rsmw1 is None) == (pd is None)
            if pd is not None:
                assert all(
                    pytest.approx(pd_bound) == rsmw1_bound + rsmw2_bound
                    for rsmw1_bound, rsmw2_bound, pd_bound in zip(
                        rsmw1, rsmw2, pd
                    )
                )

        # advance generations asynchronously
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].Clone()
        for individual in population:
            if random.choice([True, False]):
                individual.DepositStratum()


@pytest.mark.filterwarnings(
    "ignore:Insufficient common ranks between columns to detect common ancestry at given confidence level."
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
        assert hstrat.calc_patristic_distance_bounds_between(
            hstrat.col_to_specimen(a),
            hstrat.col_to_specimen(b),
            prior,
        ) == hstrat.calc_patristic_distance_bounds_between(a, b, prior)
