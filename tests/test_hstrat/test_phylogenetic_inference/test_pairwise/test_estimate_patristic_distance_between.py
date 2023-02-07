import itertools as it
import random

from iterify import cyclify, iterify
import numpy as np
import opytional as opyt
import pytest
from scipy import stats

from hstrat import hstrat


@pytest.mark.filterwarnings(
    "ignore:Insufficient common ranks between columns to detect common ancestry at given confidence level."
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 8, 64],
)
@pytest.mark.parametrize(
    "estimator",
    [
        "maximum_likelihood",
        "unbiased",
    ],
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
def test_comparison_commutativity_asyncrhonous(
    differentia_width,
    retention_policy,
    estimator,
):
    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for generation in range(30):
        for first, second in it.combinations(population, 2):
            # assert commutativity
            assert hstrat.estimate_patristic_distance_between(
                first,
                second,
                estimator=estimator,
            ) == hstrat.estimate_patristic_distance_between(
                second, first, estimator=estimator
            )

        # advance generation
        random.shuffle(population)
        for target in range(5):
            population[target] = population[-1].CloneDescendant()
        for individual in population:
            # asynchronous generations
            if random.choice([True, False]):
                individual.DepositStratum()


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
    "differentia_width",
    [1, 8, 64],
)
@pytest.mark.parametrize(
    "estimator",
    ["maximum_likelihood", "unbiased"],
)
def test_comparison_commutativity_syncrhonous(
    retention_policy,
    differentia_width,
    estimator,
):

    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for generation in range(100):

        for first, second in it.combinations(population, 2):
            # assert commutativity
            assert hstrat.estimate_patristic_distance_between(
                first, second, estimator=estimator
            ) == hstrat.estimate_patristic_distance_between(
                second, first, estimator=estimator
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
@pytest.mark.parametrize(
    "estimator",
    ["maximum_likelihood", "unbiased"],
)
def test_comparison_validity(retention_policy, differentia_width, estimator):
    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for generation in range(100):
        for first, second in it.permutations(population, 2):

            rsmw1 = hstrat.estimate_ranks_since_mrca_with(
                first,
                second,
                estimator=estimator,
            )
            rsmw2 = hstrat.estimate_ranks_since_mrca_with(
                second,
                first,
                estimator=estimator,
            )
            est = hstrat.estimate_patristic_distance_between(
                first,
                second,
                estimator=estimator,
            )
            assert (rsmw1 is None) == (rsmw1 is None) == (est is None)
            if est is not None:
                assert rsmw1 + rsmw2 == pytest.approx(est)

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
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=13),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=10,
        ),
    ],
)
@pytest.mark.parametrize(
    "differentia_width",
    [1, 8, 64],
)
def test_statistical_properties(
    retention_policy,
    differentia_width,
):

    err_maximum_likelihood = []
    err_unbiased = []

    common_ancestors = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
        )
    ]
    for i in range(113):
        common_ancestors.append(common_ancestors[-1].CloneDescendant())

    for rep in range(10000):
        num_total = random.randrange(57, 113)
        num_together = random.randrange(num_total + 1)
        num_alone = num_total - num_together

        left_alone = num_alone
        right_alone = num_alone + random.randrange(19)

        common_ancestor = common_ancestors[num_together]
        left = common_ancestor.Clone()
        right = common_ancestor.Clone()

        left.DepositStrata(left_alone)
        right.DepositStrata(right_alone)

        err_maximum_likelihood.append(
            hstrat.estimate_patristic_distance_between(
                left, right, estimator="maximum_likelihood"
            )
            - (left_alone + right_alone)
        )
        err_unbiased.append(
            hstrat.estimate_patristic_distance_between(
                left, right, estimator="unbiased"
            )
            - (left_alone + right_alone)
        )

    err_unbiased_ = np.array(err_unbiased)
    print(np.mean(err_unbiased))
    assert stats.ttest_ind(err_unbiased_, -err_unbiased_)[1] > 0.01

    mean_err_unbiased = np.mean(err_unbiased)
    mean_err_maximum_likelihood = np.mean(err_maximum_likelihood)

    median_abs_err_unbiased = np.percentile(np.abs(err_unbiased), 50)
    median_abs_err_maximum_likelihood = np.percentile(
        np.abs(err_maximum_likelihood), 50
    )

    if differentia_width == 1 and isinstance(
        retention_policy, hstrat.nominal_resolution_algo.Policy
    ):
        assert abs(mean_err_unbiased) < abs(mean_err_maximum_likelihood)
        assert not all(
            ml > ub
            for ml, ub in zip(
                sorted(np.abs(err_maximum_likelihood)),
                sorted(np.abs(err_unbiased)),
            )
        )
    elif differentia_width == 1:
        assert abs(mean_err_unbiased) < abs(mean_err_maximum_likelihood)
        assert median_abs_err_unbiased > median_abs_err_maximum_likelihood
    else:
        assert abs(mean_err_unbiased) <= abs(mean_err_maximum_likelihood)
        assert median_abs_err_unbiased >= median_abs_err_maximum_likelihood
