import itertools as it
import random

import numpy as np
import pytest
from scipy import stats

from hstrat import hstrat


@pytest.mark.parametrize(
    "estimator",
    [
        "maximum_likelihood",
        "unbiased",
    ],
)
@pytest.mark.parametrize(
    "prior",
    [
        "arbitrary",
        hstrat.GeometricPrior(1.1),
        hstrat.ExponentialPrior(1.1),
        "uniform",
    ],
)
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
def test_estimate_ranks_since_mrca_with_specimen(
    estimator, prior, retention_policy, differentia_width
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

    assert hstrat.estimate_ranks_since_mrca_with(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(column2),
        estimator=estimator,
        prior=prior,
    ) == hstrat.estimate_ranks_since_mrca_with(
        column,
        column2,
        estimator=estimator,
        prior=prior,
    )

    assert hstrat.estimate_ranks_since_mrca_with(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(column),
        estimator=estimator,
        prior=prior,
    ) == hstrat.estimate_ranks_since_mrca_with(
        column,
        column,
        estimator=estimator,
        prior=prior,
    )

    assert hstrat.estimate_ranks_since_mrca_with(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(child1),
        estimator=estimator,
        prior=prior,
    ) == hstrat.estimate_ranks_since_mrca_with(
        column,
        child1,
        estimator=estimator,
        prior=prior,
    )

    assert hstrat.estimate_ranks_since_mrca_with(
        hstrat.col_to_specimen(child1),
        hstrat.col_to_specimen(child2),
        estimator=estimator,
        prior=prior,
    ) == hstrat.estimate_ranks_since_mrca_with(
        child1,
        child2,
        estimator=estimator,
        prior=prior,
    )

    child1.DepositStrata(10)
    assert hstrat.estimate_ranks_since_mrca_with(
        hstrat.col_to_specimen(child1),
        hstrat.col_to_specimen(child2),
        estimator=estimator,
        prior=prior,
    ) == hstrat.estimate_ranks_since_mrca_with(
        child1,
        child2,
        estimator=estimator,
        prior=prior,
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
    "differentia_width",
    [1, 8, 64],
)
@pytest.mark.parametrize(
    "estimator",
    ["maximum_likelihood", "unbiased"],
)
@pytest.mark.parametrize(
    "prior",
    [
        "arbitrary",
        hstrat.GeometricPrior(1.1),
        hstrat.ExponentialPrior(1.1),
        "uniform",
    ],
)
def test_comparison_commutativity_synchronous(
    retention_policy,
    differentia_width,
    estimator,
    prior,
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
            assert hstrat.estimate_ranks_since_mrca_with(
                first, second, estimator=estimator, prior=prior
            ) == hstrat.estimate_ranks_since_mrca_with(
                second, first, estimator=estimator, prior=prior
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
@pytest.mark.parametrize(
    "prior",
    [
        "arbitrary",
        hstrat.GeometricPrior(1.1),
        hstrat.ExponentialPrior(1.1),
        "uniform",
    ],
)
def test_comparison_validity(
    retention_policy, differentia_width, estimator, prior
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
        for first, second in it.permutations(population, 2):

            bounds = hstrat.calc_ranks_since_mrca_bounds_with(
                first, second, prior="arbitrary", confidence_level=0.49
            )
            est = hstrat.estimate_ranks_since_mrca_with(
                first,
                second,
                estimator=estimator,
                prior=prior,
            )
            if bounds is not None:
                lb, ub = bounds
                assert 0 <= lb or pytest.approx(0) == lb
                assert lb <= est or pytest.approx(lb) == est
                assert (
                    est <= first.GetNumStrataDeposited()
                    or pytest.approx(est) == first.GetNumStrataDeposited()
                )
                if estimator == "maximum_likelihood" and prior == "arbitrary":
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

    err_maximum_likelihood_arbitrary = []
    err_maximum_likelihood_uniform = []
    err_unbiased = []

    common_ancestors = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
        )
    ]
    for __ in range(113):
        common_ancestors.append(common_ancestors[-1].CloneDescendant())

    for _rep in range(10000):
        _ = _rep
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

        err_maximum_likelihood_arbitrary.append(
            hstrat.estimate_ranks_since_mrca_with(
                left,
                right,
                estimator="maximum_likelihood",
                prior="arbitrary",
            )
            - left_alone
        )
        err_maximum_likelihood_uniform.append(
            hstrat.estimate_ranks_since_mrca_with(
                left,
                right,
                estimator="maximum_likelihood",
                prior="uniform",
            )
            - left_alone
        )
        err_unbiased.append(
            hstrat.estimate_ranks_since_mrca_with(
                left,
                right,
                estimator="unbiased",
                prior="uniform",
            )
            - left_alone
        )

    err_unbiased_ = np.array(err_unbiased)
    print(np.mean(err_unbiased))
    assert stats.ttest_ind(err_unbiased_, -err_unbiased_)[1] > 0.01

    for err_maximum_likelihood in (
        err_maximum_likelihood_arbitrary,
        err_maximum_likelihood_uniform,
    ):
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
    "estimator",
    ["maximum_likelihood", "unbiased"],
)
@pytest.mark.parametrize(
    "prior",
    ["arbitrary", "uniform"],
)
def test_artifact_types_equiv(differentia_width, policy, estimator, prior):
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
        assert hstrat.estimate_ranks_since_mrca_with(
            hstrat.col_to_specimen(a),
            hstrat.col_to_specimen(b),
            estimator,
            prior,
        ) == hstrat.estimate_ranks_since_mrca_with(a, b, estimator, prior)
