import itertools as it
import random

from iterify import cyclify, iterify
import opytional as opyt
import pytest
from scipy import stats

from hstrat import hstrat


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
def test_comparison_commutativity_asynchronous(
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

    for generation in range(100):
        for first, second in it.combinations(population, 2):
            # assert commutativity
            assert (
                hstrat.calc_rank_of_mrca_bounds_among(
                    [first, second], prior="arbitrary"
                )
                == hstrat.calc_rank_of_mrca_bounds_among(
                    [second, first], prior="arbitrary"
                )
                == hstrat.calc_rank_of_mrca_bounds_among(
                    [second, first] * 3, prior="arbitrary"
                )
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
def test_CalcRankOfMrcaBoundsWith(retention_policy, ordered_store):
    def make_bundle():
        return hstrat.HereditaryStratigraphicColumnBundle(
            {
                "test": hstrat.HereditaryStratigraphicColumn(
                    initial_stratum_annotation=0,
                    stratum_ordered_store=ordered_store,
                    stratum_retention_policy=retention_policy,
                ),
                "control": hstrat.HereditaryStratigraphicColumn(
                    initial_stratum_annotation=0,
                    stratum_ordered_store=ordered_store,
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
            lb, ub = hstrat.calc_rank_of_mrca_bounds_among(
                [f["test"], s["test"]],
                prior="arbitrary",
            )
            actual_rank_of_mrca = hstrat.get_last_common_stratum_between(
                f["control"], s["control"]
            ).GetAnnotation()
            assert lb <= actual_rank_of_mrca < ub

            lb, ub = hstrat.calc_rank_of_mrca_bounds_among(
                [f["test"], s["test"], f["test"]],
                prior="arbitrary",
            )
            assert lb <= actual_rank_of_mrca < ub

        for f, s in it.chain(
            zip(population, cyclify(frozen_unrelated)),
            zip(population, cyclify(unrelated_isolated)),
            zip(cyclify(frozen_unrelated), population),
            zip(cyclify(unrelated_isolated), population),
        ):
            assert (
                hstrat.calc_rank_of_mrca_bounds_among(
                    [f["test"], s["test"]], prior="arbitrary"
                )
                is None
            )
            assert (
                hstrat.calc_rank_of_mrca_bounds_among(
                    [f["test"], s["test"], f["test"]], prior="arbitrary"
                )
                is None
            )
            assert (
                hstrat.calc_rank_of_mrca_bounds_among(
                    [f["test"], s["test"]] * 3, prior="arbitrary"
                )
                is None
            )

        # advance generation
        random.shuffle(population)
        for target in range(3):
            population[target] = population[-1].CloneDescendant(
                stratum_annotation=population[-1].GetNumStrataDeposited(),
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

    for generation in range(100):

        for first, second in it.combinations(population, 2):
            # assert commutativity
            assert (
                hstrat.calc_rank_of_mrca_bounds_among(
                    [first, second], prior="arbitrary"
                )
                == hstrat.calc_rank_of_mrca_bounds_among(
                    [second, first], prior="arbitrary"
                )
                == hstrat.calc_rank_of_mrca_bounds_among(
                    [second, first, first], prior="arbitrary"
                )
                == hstrat.calc_rank_of_mrca_bounds_among(
                    [second, first, second, first], prior="arbitrary"
                )
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

    for generation in range(100):
        for first, second in it.combinations(population, 2):
            lcrw = hstrat.calc_rank_of_last_retained_commonality_between(
                first, second
            )
            if lcrw is not None:
                assert 0 <= lcrw <= generation

            fdrw = hstrat.calc_rank_of_first_retained_disparity_between(
                first, second
            )
            if fdrw is not None:
                assert 0 <= fdrw <= generation

            assert hstrat.calc_rank_of_mrca_bounds_among(
                [first, second], prior="arbitrary"
            ) in [
                (lcrw, opyt.or_value(fdrw, first.GetNumStrataDeposited())),
                None,
            ]
            assert hstrat.calc_rank_of_mrca_bounds_among(
                [first, second, first],
                prior="arbitrary",
            ) in [
                (lcrw, opyt.or_value(fdrw, first.GetNumStrataDeposited())),
                None,
            ]
            assert hstrat.calc_rank_of_mrca_bounds_among(
                [first, second] * 3, prior="arbitrary"
            ) in [
                (lcrw, opyt.or_value(fdrw, first.GetNumStrataDeposited())),
                None,
            ]

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
    [1, 2, 8, 64],
)
@pytest.mark.parametrize(
    "confidence_level",
    [0.8, 0.95],
)
def test_CalcRankOfMrcaBoundsWith_narrow_shallow(
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
                hstrat.calc_rank_of_mrca_bounds_among(
                    [c1, c2],
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
                is None
            )
            assert (
                hstrat.calc_rank_of_mrca_bounds_among(
                    [c2, c1],
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
                is None
            )
            assert (
                hstrat.calc_rank_of_mrca_bounds_among(
                    [c2, c1, c1],
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
                is None
            )


@pytest.mark.filterwarnings(
    "ignore:Insufficient common ranks between columns to detect common ancestry at given confidence level."
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
    [1, 2, 8, 64],
)
@pytest.mark.parametrize(
    "confidence_level",
    [0.8, 0.95],
)
@pytest.mark.parametrize(
    "mrca_rank",
    [100],
)
def test_CalcRankOfMrcaBoundsWith_narrow_with_mrca(
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
            assert (
                hstrat.calc_rank_of_mrca_bounds_among(
                    [c1, c2],
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
                == hstrat.calc_rank_of_mrca_bounds_among(
                    [c2, c1],
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
                == hstrat.calc_rank_of_mrca_bounds_among(
                    [c2, c1, c2],
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
                == hstrat.calc_rank_of_mrca_bounds_among(
                    [c2, c1] * 2,
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
            )
            res = hstrat.calc_rank_of_mrca_bounds_among(
                [c1, c2, c1],
                prior="arbitrary",
                confidence_level=confidence_level,
            )

            if res is None:
                num_outside_bounds += 1
                continue

            lb, ub = res
            assert lb < ub
            assert lb >= 0
            assert ub >= 0

            num_inside_bounds += lb <= mrca_rank < ub
            num_outside_bounds += not (lb <= mrca_rank < ub)

            assert mrca_rank < ub

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


@pytest.mark.filterwarnings(
    "ignore:Insufficient common ranks between columns to detect common ancestry at given confidence level."
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
    [1, 2, 8, 64],
)
@pytest.mark.parametrize(
    "confidence_level",
    [0.8, 0.95],
)
@pytest.mark.parametrize(
    "mrca_rank",
    [0, 100],
)
def test_CalcRankOfMrcaBoundsWith_narrow_no_mrca(
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
            assert (
                hstrat.calc_rank_of_mrca_bounds_among(
                    [c1, c2],
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
                == hstrat.calc_rank_of_mrca_bounds_among(
                    [c2, c1],
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
                == hstrat.calc_rank_of_mrca_bounds_among(
                    [c2, c1, c2],
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
                == hstrat.calc_rank_of_mrca_bounds_among(
                    [c2, c1] * 2,
                    prior="arbitrary",
                    confidence_level=confidence_level,
                )
            )
            res = hstrat.calc_rank_of_mrca_bounds_among(
                [c1, c2, c1],
                prior="arbitrary",
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


@pytest.mark.filterwarnings("ignore:Empty or singleton population.")
def test_calc_rank_of_mrca_bounds_among_singletonpop():

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )
    for __ in range(10):
        assert hstrat.calc_rank_of_earliest_detectable_mrca_among([c1]) is None
        c1.DepositStratum()

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )
    for __ in range(10):
        assert hstrat.calc_rank_of_earliest_detectable_mrca_among([c1]) is None
        c1.DepositStratum()


@pytest.mark.filterwarnings("ignore:Empty or singleton population.")
def test_calc_rank_of_earliest_detectable_mrca_emptypop():

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )
    for __ in range(10):
        assert hstrat.calc_rank_of_earliest_detectable_mrca_among([]) is None
        c1.DepositStratum()

    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
        stratum_retention_policy=hstrat.perfect_resolution_algo.Policy(),
    )
    for __ in range(10):
        assert hstrat.calc_rank_of_earliest_detectable_mrca_among([]) is None
        c1.DepositStratum()


@pytest.mark.filterwarnings(
    "ignore:Insufficient common ranks between columns to detect common ancestry at given confidence level."
)
def test_calc_rank_of_mrca_bounds_among_generator():
    c1 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=1,
    )
    for __ in range(10):
        assert hstrat.calc_rank_of_mrca_bounds_among(
            [c1 for __ in range(10)],
            prior="arbitrary",
        ) == hstrat.calc_rank_of_mrca_bounds_among(
            (c1 for __ in range(10)), prior="arbitrary"
        )
        c1.DepositStratum()

    c2 = hstrat.HereditaryStratigraphicColumn(
        stratum_differentia_bit_width=64,
    )
    for __ in range(10):
        assert hstrat.calc_rank_of_mrca_bounds_among(
            [c2 for __ in range(10)], prior="arbitrary"
        ) == hstrat.calc_rank_of_mrca_bounds_among(
            (c2 for __ in range(10)), prior="arbitrary"
        )
        c2.DepositStratum()
