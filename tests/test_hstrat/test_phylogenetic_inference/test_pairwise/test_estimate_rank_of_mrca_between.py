import itertools as it
import random

import numpy as np
import opytional as opyt
import pytest
from scipy import stats as scipy_stats

from hstrat import hstrat
from hstrat._auxiliary_lib import cmp_approx, pairwise


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
def test_estimate_rank_of_mrca_between_specimen(
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

    assert hstrat.estimate_rank_of_mrca_between(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(column2),
        estimator=estimator,
        prior=prior,
    ) == hstrat.estimate_rank_of_mrca_between(
        column,
        column2,
        estimator=estimator,
        prior=prior,
    )

    assert hstrat.estimate_rank_of_mrca_between(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(column),
        estimator=estimator,
        prior=prior,
    ) == hstrat.estimate_rank_of_mrca_between(
        column,
        column,
        estimator=estimator,
        prior=prior,
    )

    assert hstrat.estimate_rank_of_mrca_between(
        hstrat.col_to_specimen(column),
        hstrat.col_to_specimen(child1),
        estimator=estimator,
        prior=prior,
    ) == hstrat.estimate_rank_of_mrca_between(
        column,
        child1,
        estimator=estimator,
        prior=prior,
    )

    assert hstrat.estimate_rank_of_mrca_between(
        hstrat.col_to_specimen(child1),
        hstrat.col_to_specimen(child2),
        estimator=estimator,
        prior=prior,
    ) == hstrat.estimate_rank_of_mrca_between(
        child1,
        child2,
        estimator=estimator,
        prior=prior,
    )

    child1.DepositStrata(10)
    assert hstrat.estimate_rank_of_mrca_between(
        hstrat.col_to_specimen(child1),
        hstrat.col_to_specimen(child2),
        estimator=estimator,
        prior=prior,
    ) == hstrat.estimate_rank_of_mrca_between(
        child1,
        child2,
        estimator=estimator,
        prior=prior,
    )


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
    "prior",
    [
        hstrat.ArbitraryPrior(),
        hstrat.GeometricPrior(growth_factor=1.1),
        hstrat.UniformPrior(),
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
def test_comparison_commutativity_asynchronous(
    differentia_width,
    retention_policy,
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

    for _generation in range(30):
        _ = _generation
        for first, second in it.combinations(population, 2):
            # assert commutativity
            assert hstrat.estimate_rank_of_mrca_between(
                first,
                second,
                estimator=estimator,
                prior=prior,
            ) == hstrat.estimate_rank_of_mrca_between(
                second,
                first,
                estimator=estimator,
                prior=prior,
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
    "prior",
    [
        hstrat.ArbitraryPrior(),
        hstrat.GeometricPrior(growth_factor=1.1),
        hstrat.UniformPrior(),
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
def test_comparison_validity(
    differentia_width, estimator, prior, retention_policy
):
    population = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
        )
        for __ in range(10)
    ]

    for _generation in range(50):
        _ = _generation
        for first, second in it.combinations(population, 2):

            bounds = hstrat.calc_rank_of_mrca_bounds_between(
                first, second, prior="arbitrary", confidence_level=0.49
            )
            est = hstrat.estimate_rank_of_mrca_between(
                first,
                second,
                estimator=estimator,
                prior=prior,
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
                if estimator == "maximum_likelihood" and prior == "arbitrary":
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

    for _generation in range(50):
        _ = _generation
        for first, second in it.combinations(population, 2):
            assert len(
                set(
                    hstrat.estimate_rank_of_mrca_between(
                        first[i],
                        second[i],
                        estimator="maximum_likelihood",
                        prior="arbitrary",
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

                for estimator, prior in (
                    ("unbiased", "arbitrary"),
                    ("unbiased", "uniform"),
                    ("unbiased", hstrat.GeometricPrior(1.1)),
                ):
                    assert hstrat.estimate_rank_of_mrca_between(
                        first[less],
                        second[less],
                        estimator=estimator,
                        prior=prior,
                    ) < hstrat.estimate_rank_of_mrca_between(
                        first[more],
                        second[more],
                        estimator=estimator,
                        prior=prior,
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

                assert hstrat.estimate_rank_of_mrca_between(
                    first[less],
                    second[less],
                    estimator="maximum_likelihood",
                    prior="uniform",
                ) <= hstrat.estimate_rank_of_mrca_between(
                    first[more],
                    second[more],
                    estimator="maximum_likelihood",
                    prior="uniform",
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

    for _generation in range(50):
        _ = _generation
        for first, second in it.combinations(population, 2):

            bounds = hstrat.calc_rank_of_mrca_bounds_between(
                first, second, prior="arbitrary", confidence_level=0.49
            )
            if bounds is not None:
                assert hstrat.estimate_rank_of_mrca_between(
                    first,
                    second,
                    estimator="maximum_likelihood",
                    prior="arbitrary",
                ) >= hstrat.estimate_rank_of_mrca_between(
                    first, second, estimator="unbiased", prior="uniform"
                )

                assert (
                    cmp_approx(
                        hstrat.estimate_rank_of_mrca_between(
                            first,
                            second,
                            estimator="unbiased",
                            prior=hstrat.GeometricPrior(1.1),
                        ),
                        hstrat.estimate_rank_of_mrca_between(
                            first,
                            second,
                            estimator="unbiased",
                            prior="uniform",
                        ),
                    )
                    != -1
                )

                assert hstrat.estimate_rank_of_mrca_between(
                    first,
                    second,
                    estimator="unbiased",
                    prior="arbitrary",
                ) >= hstrat.estimate_rank_of_mrca_between(
                    first, second, estimator="unbiased", prior="uniform"
                )

                assert hstrat.estimate_rank_of_mrca_between(
                    first,
                    second,
                    estimator="maximum_likelihood",
                    prior="arbitrary",
                ) >= hstrat.estimate_rank_of_mrca_between(
                    first,
                    second,
                    estimator="maximum_likelihood",
                    prior="uniform",
                )

                assert (
                    hstrat.estimate_rank_of_mrca_between(
                        first,
                        second,
                        estimator="unbiased",
                        prior=hstrat.GeometricPrior(1.1),
                    )
                    > hstrat.estimate_rank_of_mrca_between(
                        first,
                        second,
                        estimator="unbiased",
                        prior=hstrat.GeometricPrior(1.05),
                    )
                    or not hstrat.calc_rank_of_first_retained_disparity_between(
                        first, second
                    )
                    or hstrat.calc_rank_of_last_retained_commonality_between(
                        first, second
                    )
                    == 0
                    or hstrat.calc_rank_of_first_retained_disparity_between(
                        first, second
                    )
                    == hstrat.calc_rank_of_last_retained_commonality_between(
                        first, second
                    )
                    + 1
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
def test_statistical_properties_uniform_prior(
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

    for _rep in range(8000):
        _ = _rep
        num_total = random.randrange(57, 113)
        num_together = random.randrange(num_total + 1)
        assert 0 <= num_together <= num_total
        num_alone = num_total - num_together

        left_alone = num_alone
        right_alone = num_alone

        common_ancestor = common_ancestors[num_together]
        left = common_ancestor.Clone()
        right = common_ancestor.Clone()

        left.DepositStrata(left_alone)
        right.DepositStrata(right_alone)

        err_maximum_likelihood_arbitrary.append(
            hstrat.estimate_rank_of_mrca_between(
                left, right, estimator="maximum_likelihood", prior="arbitrary"
            )
            - num_together
        )
        err_maximum_likelihood_uniform.append(
            hstrat.estimate_rank_of_mrca_between(
                left, right, estimator="maximum_likelihood", prior="uniform"
            )
            - num_together
        )
        err_unbiased.append(
            hstrat.estimate_rank_of_mrca_between(
                left, right, estimator="unbiased", prior="uniform"
            )
            - num_together
        )

    err_unbiased_ = np.array(err_unbiased)
    assert (
        np.count_nonzero(err_unbiased_) < 4
        or scipy_stats.ttest_ind(err_unbiased_, -err_unbiased_)[1] > 0.01
    )

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
        elif differentia_width == 8:
            _t_stat, p_value = scipy_stats.ttest_ind(
                err_unbiased, err_maximum_likelihood
            )
            _ = _t_stat
            assert (
                abs(mean_err_unbiased) <= abs(mean_err_maximum_likelihood)
                or p_value > 0.01
            )

            _w_stat, p_value = scipy_stats.wilcoxon(
                np.abs(err_unbiased), np.abs(err_maximum_likelihood)
            )
            _ = _w_stat
            assert (
                median_abs_err_unbiased >= median_abs_err_maximum_likelihood
                or p_value > 0.01
            )

        else:
            assert abs(mean_err_unbiased) <= abs(mean_err_maximum_likelihood)
            assert median_abs_err_unbiased >= median_abs_err_maximum_likelihood


@pytest.mark.filterwarnings(
    "ignore:Insufficient common ranks between columns to detect common ancestry at given confidence level."
)
@pytest.mark.parametrize(
    "retention_policy",
    [
        hstrat.nominal_resolution_algo.Policy(),
        hstrat.fixed_resolution_algo.Policy(fixed_resolution=7),
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
    "geometric_factor",
    [1.01, 1.1, 2],
)
def test_statistical_properties_geometric_prior(
    retention_policy,
    differentia_width,
    geometric_factor,
):

    err_maximum_likelihood = []
    err_unbiased = []

    common_ancestors = [
        hstrat.HereditaryStratigraphicColumn(
            stratum_differentia_bit_width=differentia_width,
            stratum_retention_policy=retention_policy,
        )
    ]
    for __ in range(113):
        common_ancestors.append(common_ancestors[-1].CloneDescendant())

    weights = np.array(
        [geometric_factor**i for i in range(113)], dtype=float
    )

    for _rep in range(8000):
        _ = _rep
        num_total = random.randrange(57, 113)

        # scrapped continuous approach to generating
        # note: e^log(b)x == b^x
        # see https://stackoverflow.com/a/40144719
        # scale = 1 / np.log(exponential_factor)
        # drawn = stats.truncexpon(b=num_total / scale, scale=scale).rvs(1)[0]
        # rounding_correction = 0.5
        # num_together = num_total - int(
        #     drawn + rounding_correction
        # )

        num_together = np.random.choice(
            np.arange(num_total + 1),
            p=weights[: num_total + 1] / weights[: num_total + 1].sum(),
        )
        assert 0 <= num_together <= num_total
        num_alone = num_total - num_together

        left_alone = num_alone
        right_alone = num_alone

        common_ancestor = common_ancestors[num_together]
        left = common_ancestor.Clone()
        right = common_ancestor.Clone()

        left.DepositStrata(left_alone)
        right.DepositStrata(right_alone)

        err_maximum_likelihood.append(
            hstrat.estimate_rank_of_mrca_between(
                left,
                right,
                estimator="maximum_likelihood",
                prior=hstrat.GeometricPrior(geometric_factor),
            )
            - num_together
        )
        err_unbiased.append(
            hstrat.estimate_rank_of_mrca_between(
                left,
                right,
                estimator="unbiased",
                prior=hstrat.GeometricPrior(geometric_factor),
            )
            - num_together
        )

    err_unbiased_ = np.array(err_unbiased)

    assert (
        np.count_nonzero(err_unbiased_) < 4
        or scipy_stats.ttest_1samp(err_unbiased_, 0)[1] > 0.01
    )

    mean_err_unbiased = np.mean(err_unbiased)
    mean_err_maximum_likelihood = np.mean(err_maximum_likelihood)

    assert not all(
        ml > ub
        for ml, ub in zip(
            sorted(np.abs(err_maximum_likelihood)),
            sorted(np.abs(err_unbiased)),
        )
    )

    if differentia_width == 1:
        assert abs(mean_err_unbiased) < abs(mean_err_maximum_likelihood)
    else:
        assert abs(mean_err_unbiased) <= abs(mean_err_maximum_likelihood)


@pytest.mark.parametrize(
    "common_ancestor",
    [
        hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=hstrat.nominal_resolution_algo.Policy(),
        ),
        hstrat.HereditaryStratigraphicColumn(
            stratum_retention_policy=hstrat.nominal_resolution_algo.Policy(),
        ).CloneNthDescendant(5),
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
def test_nominal_retention_policy(common_ancestor, estimator, prior):
    assert (
        hstrat.estimate_rank_of_mrca_between(
            common_ancestor, common_ancestor, estimator=estimator, prior=prior
        )
        == common_ancestor.GetNumStrataDeposited() - 1
    )

    assert (
        hstrat.calc_rank_of_first_retained_disparity_between(
            common_ancestor,
            common_ancestor.CloneNthDescendant(7),
        )
        == common_ancestor.GetNumStrataDeposited()
    )

    assert (
        hstrat.estimate_rank_of_mrca_between(
            common_ancestor,
            common_ancestor.CloneNthDescendant(7),
            estimator=estimator,
            prior=prior,
        )
        == (common_ancestor.GetNumStrataDeposited() - 1) / 2
    )

    assert (
        hstrat.estimate_rank_of_mrca_between(
            common_ancestor.CloneNthDescendant(2),
            common_ancestor.CloneNthDescendant(7),
            estimator=estimator,
            prior=prior,
        )
        == (common_ancestor.GetNumStrataDeposited() - 1 + 2) / 2
    )

    assert (
        hstrat.estimate_rank_of_mrca_between(
            common_ancestor.CloneNthDescendant(7),
            common_ancestor.CloneNthDescendant(7),
            estimator=estimator,
            prior=prior,
        )
        == (common_ancestor.GetNumStrataDeposited() + 7 - 1 - 1) / 2
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
        assert hstrat.estimate_rank_of_mrca_between(
            hstrat.col_to_specimen(a),
            hstrat.col_to_specimen(b),
            estimator,
            prior,
        ) == hstrat.estimate_rank_of_mrca_between(a, b, estimator, prior)
