import itertools as it
import random

from iterify import cyclify, iterify
import numpy as np
import opytional as opyt
import pytest
from scipy import stats

from hstrat import hstrat


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
            assert hstrat.estimate_ranks_since_mrca_with(
                first, second, estimator=estimator
            ) == hstrat.estimate_ranks_since_mrca_with(
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

            bounds = hstrat.calc_ranks_since_mrca_bounds_with(
                first, second, confidence_level=0.49
            )
            est = hstrat.estimate_ranks_since_mrca_with(
                first,
                second,
                estimator=estimator,
            )
            if bounds is not None:
                lb, ub = bounds
                assert 0 <= lb <= est <= first.GetNumStrataDeposited()
                if estimator == "maximum_likelihood":
                    assert est < ub
            else:
                assert est is None

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
    for i in range(100):
        common_ancestors.append(common_ancestors[-1].CloneDescendant())

    for rep in range(10000):
        num_together = random.randrange(100)
        left_alone = random.randrange(100)
        right_alone = random.randrange(100)

        common_ancestor = common_ancestors[num_together]
        left = common_ancestor.Clone()
        right = common_ancestor.Clone()

        left.DepositStrata(left_alone)
        right.DepositStrata(right_alone)

        err_maximum_likelihood.append(
            hstrat.estimate_rank_of_mrca_between(
                left, right, estimator="maximum_likelihood"
            )
            - num_together
        )
        err_unbiased.append(
            hstrat.estimate_rank_of_mrca_between(
                left, right, estimator="unbiased"
            )
            - num_together
        )

    mean_err_unbiased = np.mean(err_unbiased)
    mean_err_maximum_likelihood = np.mean(err_maximum_likelihood)

    median_abs_err_unbiased = np.percentile(np.abs(err_unbiased), 50)
    median_abs_err_maximum_likelihood = np.percentile(
        np.abs(err_maximum_likelihood), 50
    )

    if differentia_width == 1 and not isinstance(
        retention_policy, hstrat.nominal_resolution_algo.Policy
    ):
        assert mean_err_unbiased < mean_err_maximum_likelihood
        assert median_abs_err_unbiased > median_abs_err_maximum_likelihood
    else:
        assert mean_err_unbiased <= mean_err_maximum_likelihood
        assert median_abs_err_unbiased >= median_abs_err_maximum_likelihood


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
        right_alone = num_alone

        common_ancestor = common_ancestors[num_together]
        left = common_ancestor.Clone()
        right = common_ancestor.Clone()

        left.DepositStrata(left_alone)
        right.DepositStrata(right_alone)

        err_maximum_likelihood.append(
            hstrat.estimate_ranks_since_mrca_with(
                left, right, estimator="maximum_likelihood"
            )
            - left_alone
        )
        err_unbiased.append(
            hstrat.estimate_ranks_since_mrca_with(
                left, right, estimator="unbiased"
            )
            - left_alone
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