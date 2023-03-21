import numpy as np
import pytest

from hstrat import hstrat


def test_estimate_rank_of_mrca_unbiased_no_common_ancestor():
    coincident_ranks = iter([0])
    p_differentia_collision = 0.5

    result = hstrat.estimate_rank_of_mrca_unbiased(
        coincident_ranks, p_differentia_collision, hstrat.ArbitraryPrior()
    )

    assert result is None


def test_estimate_rank_of_mrca_unbiased_with_common_ancestor1():
    coincident_ranks = iter([1, 0])
    p_differentia_collision = 0.5

    result = hstrat.estimate_rank_of_mrca_unbiased(
        coincident_ranks, p_differentia_collision, hstrat.ArbitraryPrior()
    )

    assert result == 0


def test_estimate_rank_of_mrca_unbiased_with_common_ancestor2():
    coincident_ranks = iter([7, 3, 0])
    p_differentia_collision = 0.5

    result = hstrat.estimate_rank_of_mrca_unbiased(
        coincident_ranks, p_differentia_collision, hstrat.ArbitraryPrior()
    )

    expected_result = np.average([4.5, 1], weights=[2, 1])
    assert np.isclose(result, expected_result)


def test_estimate_rank_of_mrca_unbiased_with_common_ancestor2b():
    coincident_ranks = iter([7, 3, 0])
    p_differentia_collision = 0.25

    result = hstrat.estimate_rank_of_mrca_unbiased(
        coincident_ranks, p_differentia_collision, hstrat.ArbitraryPrior()
    )

    expected_result = np.average([4.5, 1], weights=[4, 1])
    assert np.isclose(result, expected_result)


def test_estimate_rank_of_mrca_unbiased_with_common_ancestor3():
    coincident_ranks = [8, 7, 2, 0]
    p_differentia_collision = 0.5

    expected_result = np.average([7, 4, 0.5], weights=[4, 2, 1])
    result = hstrat.estimate_rank_of_mrca_unbiased(
        coincident_ranks, p_differentia_collision, hstrat.ArbitraryPrior()
    )

    assert np.isclose(result, expected_result)


@pytest.mark.parametrize(
    "prior",
    [
        hstrat.ArbitraryPrior(),
        hstrat.UniformPrior(),
        hstrat.ExponentialPrior(1.1),
        hstrat.GeometricPrior(1.1),
    ],
)
@pytest.mark.parametrize(
    "p_differentia_collision", [0.5, 0.25, 0.5**8, 0.5**64]
)
def test_estimate_rank_of_mrca_unbiased_with_common_ancestor4(
    prior, p_differentia_collision
):
    coincident_ranks = iter([8, 7, 2, 0])

    # Calculate expected result using np.average with weights
    expected_ranks = [
        prior.CalcIntervalConditionedMean(7, 8),
        prior.CalcIntervalConditionedMean(2, 7),
        prior.CalcIntervalConditionedMean(0, 2),
    ]
    weights = [
        p_differentia_collision**0
        * prior.CalcIntervalProbabilityProxy(7, 8),
        p_differentia_collision**1
        * prior.CalcIntervalProbabilityProxy(2, 7),
        p_differentia_collision**2
        * prior.CalcIntervalProbabilityProxy(0, 2),
    ]
    expected_result = np.average(expected_ranks, weights=weights)

    result = hstrat.estimate_rank_of_mrca_unbiased(
        coincident_ranks, p_differentia_collision, prior
    )

    assert np.isclose(result, expected_result)


def test_estimate_rank_of_mrca_unbiased_with_common_ancestor5():
    coincident_ranks = [8, 7, 2, 0]
    p_differentia_collision = 0.5**64

    result = hstrat.estimate_rank_of_mrca_unbiased(
        coincident_ranks, p_differentia_collision, hstrat.ArbitraryPrior()
    )

    assert np.isclose(result, 7)


def test_estimate_rank_of_mrca_unbiased_with_common_ancestor6():
    coincident_ranks = [7, 3, 0]
    p_differentia_collision = 0.5

    result1 = hstrat.estimate_rank_of_mrca_unbiased(
        coincident_ranks, p_differentia_collision, hstrat.GeometricPrior(2)
    )
    result2 = hstrat.estimate_rank_of_mrca_unbiased(
        coincident_ranks, p_differentia_collision, hstrat.GeometricPrior(2.1)
    )

    assert 4 < result1 < result2 < 6
