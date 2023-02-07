import itertools as it
import random

from iterify import cyclify, iterify
import numpy as np
import opytional as opyt
import pytest
from scipy import stats

from hstrat import hstrat
from hstrat._auxiliary_lib import is_strictly_increasing, pairwise


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
            assert hstrat.estimate_rank_of_mrca_between(
                first,
                second,
                estimator=estimator,
            ) == hstrat.estimate_rank_of_mrca_between(
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
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=3
        ),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
def test_comparison_validity(differentia_width, estimator, retention_policy):
    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for generation in range(50):
        for first, second in it.combinations(population, 2):

            bounds = hstrat.calc_rank_of_mrca_bounds_between(
                first, second, confidence_level=0.49
            )
            est = hstrat.estimate_rank_of_mrca_between(
                first, second, estimator=estimator
            )
            if bounds is not None:
                lb, ub = bounds
                assert (
                    0
                    <= est
                    < ub
                    <= min(
                        first.GetNumStrataDeposited(),
                        second.GetNumStrataDeposited(),
                    )
                )
                if estimator == "maximum_likelihood":
                    assert lb <= est
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
        hstrat.perfect_resolution_algo.Policy(),
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=3
        ),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
def test_comparison_bit_width_effects(retention_policy):
    population = [
        (
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=1,
                stratum_retention_policy=retention_policy,
            ),
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=8,
                stratum_retention_policy=retention_policy,
            ),
            hstrat.HereditaryStratigraphicColumn(
                stratum_differentia_bit_width=64,
                stratum_retention_policy=retention_policy,
            ),
        )
        for __ in range(10)
    ]

    for generation in range(50):
        for first, second in it.combinations(population, 2):
            assert len(
                set(
                    hstrat.estimate_rank_of_mrca_between(
                        first[i], second[i], estimator="maximum_likelihood"
                    )
                    for i in range(3)
                )
            ) == len(
                set(
                    hstrat.calc_rank_of_first_retained_disparity_between(
                        first[i],
                        second[i],
                        confidence_level=0.49,
                    )
                    for i in range(3)
                )
            )

            for less, more in pairwise(range(3)):

                if not hstrat.calc_rank_of_last_retained_commonality_between(
                    first[less],
                    second[less],
                    confidence_level=0.49,
                ) or not hstrat.calc_rank_of_last_retained_commonality_between(
                    first[more],
                    second[more],
                    confidence_level=0.49,
                ):
                    continue

                min_len_less = min(
                    first[less].GetNumStrataDeposited(),
                    second[less].GetNumStrataDeposited(),
                )
                min_len_more = min(
                    first[more].GetNumStrataDeposited(),
                    second[more].GetNumStrataDeposited(),
                )
                assert min_len_less == min_len_more

                assert hstrat.estimate_rank_of_mrca_between(
                    first[less], second[less], estimator="unbiased"
                ) < hstrat.estimate_rank_of_mrca_between(
                    first[more], second[more], estimator="unbiased"
                ) or opyt.or_value(
                    hstrat.calc_rank_of_first_retained_disparity_between(
                        first[less],
                        second[less],
                        confidence_level=0.49,
                    ),
                    min_len_less,
                ) > opyt.or_value(
                    hstrat.calc_rank_of_first_retained_disparity_between(
                        first[more],
                        second[more],
                        confidence_level=0.49,
                    ),
                    min_len_more,
                )

        # advance generations asynchronously
        random.shuffle(population)
        for target in range(5):
            population[target] = tuple(c.Clone() for c in population[-1])
        for individual in population:
            if random.choice([True, False]):
                for c in individual:
                    c.DepositStratum()


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
        hstrat.recency_proportional_resolution_algo.Policy(
            recency_proportional_resolution=3
        ),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=10),
    ],
)
def test_comparison_ml_vs_unbiased(differentia_width, retention_policy):
    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for generation in range(50):
        for first, second in it.combinations(population, 2):

            bounds = hstrat.calc_rank_of_mrca_bounds_between(
                first, second, confidence_level=0.49
            )
            if bounds is not None:
                lb, ub = bounds
                assert hstrat.estimate_rank_of_mrca_between(
                    first, second, estimator="maximum_likelihood"
                ) >= hstrat.estimate_rank_of_mrca_between(
                    first, second, estimator="unbiased"
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
