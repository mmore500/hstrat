import itertools as it
import random

from iterify import cyclify, iterify
import opytional as opyt
import pytest
from scipy import stats

from hstrat import hstrat


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
def test_CalcRanksSinceMrcaBoundsWith(
    retention_policy,
    ordered_store,
):
    def make_bundle():
        return hstrat.HereditaryStratigraphicColumnBundle(
            {
                "test": hstrat.HereditaryStratigraphicColumn(
                    initial_stratum_annotation=0,
                    stratum_ordered_store_factory=ordered_store,
                    stratum_retention_policy=retention_policy,
                ),
                "control": hstrat.HereditaryStratigraphicColumn(
                    initial_stratum_annotation=0,
                    stratum_ordered_store_factory=ordered_store,
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

    for generation in range(100):
        for f, s in it.chain(
            it.combinations(population, 2),
            zip(population, cyclify(forked_isolated)),
            zip(population, cyclify(frozen_copy)),
            zip(cyclify(forked_isolated), population),
            zip(cyclify(frozen_copy), population),
        ):
            lb, ub = hstrat.calc_ranks_since_mrca_bounds_with(
                f["test"], s["test"]
            )
            actual_rank_of_mrca = hstrat.get_last_common_stratum_between(
                f["control"],
                s["control"],
            ).GetAnnotation()
            actual_ranks_since_mrca = (
                f.GetNumStrataDeposited() - actual_rank_of_mrca - 1
            )
            assert lb <= actual_ranks_since_mrca < ub

        for f, s in it.chain(
            zip(population, cyclify(frozen_unrelated)),
            zip(population, cyclify(unrelated_isolated)),
            zip(cyclify(frozen_unrelated), population),
            zip(cyclify(unrelated_isolated), population),
        ):
            assert (
                hstrat.calc_ranks_since_mrca_bounds_with(f["test"], s["test"])
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
def test_comparison_commutativity_syncrhonous(
    retention_policy,
    ordered_store,
):

    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_ordered_store_factory=ordered_store,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for generation in range(100):

        for first, second in it.combinations(population, 2):
            # assert commutativity
            assert hstrat.calc_ranks_since_mrca_bounds_with(
                first, second
            ) == hstrat.calc_ranks_since_mrca_bounds_with(second, first)

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
            stratum_ordered_store_factory=ordered_store,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for generation in range(100):
        for first, second in it.combinations(population, 2):
            rslcw = hstrat.calc_ranks_since_last_retained_commonality_with(
                first, second
            )
            if rslcw is not None:
                assert 0 <= rslcw <= generation

            rsfdw = hstrat.calc_ranks_since_first_retained_disparity_with(
                first, second
            )
            if rsfdw is not None:
                assert -1 <= rsfdw <= generation

            assert hstrat.calc_ranks_since_mrca_bounds_with(
                first, second
            ) is None or hstrat.calc_ranks_since_mrca_bounds_with(
                first, second
            ) == (
                opyt.or_value(rsfdw, -1) + 1,
                rslcw + 1,
            )
            if rslcw is not None and rsfdw is not None:
                assert rsfdw < rslcw

        # advance generations asynchronously
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].Clone()
        for individual in population:
            if random.choice([True, False]):
                individual.DepositStratum()


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
def test_CalcRanksSinceMrcaBoundsWith_narrow_shallow(
    retention_policy,
    differentia_width,
    confidence_level,
):

    columns = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
            stratum_ordered_store_factory=hstrat.HereditaryStratumOrderedStoreDict,
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
                hstrat.calc_ranks_since_mrca_bounds_with(
                    c1, c2, confidence_level=confidence_level
                )
                is None
            )
            assert (
                hstrat.calc_ranks_since_mrca_bounds_with(
                    c2,
                    c1,
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
def test_CalcRanksSinceMrcaBoundsWith_narrow_with_mrca(
    retention_policy,
    differentia_width,
    confidence_level,
    mrca_rank,
):

    columns = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
            stratum_ordered_store_factory=hstrat.HereditaryStratumOrderedStoreDict,
        )
        for __ in range(20)
    ]

    for generation in range(mrca_rank):
        for column in columns:
            column.DepositStratum()

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

        num_inside_bounds = 0
        num_outside_bounds = 0
        for c1, c2 in zip(column1, column2):
            res = hstrat.calc_ranks_since_mrca_bounds_with(
                c1,
                c2,
                confidence_level=confidence_level,
            )

            if res is None:
                num_outside_bounds += 1
                continue

            lb, ub = res
            assert lb < ub
            assert lb >= 0
            assert ub >= 0

            num_inside_bounds += (
                lb <= c1.GetNumStrataDeposited() - 1 - mrca_rank < ub
            )
            num_outside_bounds += not (
                lb <= c1.GetNumStrataDeposited() - 1 - mrca_rank < ub
            )

            assert c1.GetNumStrataDeposited() - 1 - mrca_rank >= lb

        num_trials = num_inside_bounds + num_outside_bounds
        assert (
            0.001
            < stats.binom.cdf(
                n=num_trials,
                p=1 - confidence_level,
                k=num_outside_bounds,
            )
            < 0.999
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
def test_CalcRanksSinceMrcaBoundsWith_narrow_no_mrca(
    retention_policy,
    differentia_width,
    confidence_level,
    mrca_rank,
):
    def make_column():
        return hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
            stratum_ordered_store_factory=hstrat.HereditaryStratumOrderedStoreDict,
        )

    columns = [make_column() for __ in range(20)]

    for generation in range(mrca_rank):
        for column in columns:
            column.DepositStratum()

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

        num_inside_bounds = 0
        num_outside_bounds = 0
        for c1, c2 in zip(column1, column2):
            res = hstrat.calc_ranks_since_mrca_bounds_with(
                c1,
                c2,
                confidence_level=confidence_level,
            )

            if res is None:
                num_inside_bounds += 1
                continue

            lb, ub = res
            assert lb < ub
            assert lb >= 0
            assert ub >= 0

            num_outside_bounds += 1

        num_trials = num_inside_bounds + num_outside_bounds
        assert (
            0.001
            < stats.binom.cdf(
                n=num_trials,
                p=1 - confidence_level,
                k=num_outside_bounds,
            )
            < 0.999
        )