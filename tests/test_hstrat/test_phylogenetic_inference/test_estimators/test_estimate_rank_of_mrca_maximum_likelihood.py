import numpy as np

from hstrat import hstrat


def test_estimate_rank_of_mrca_maximum_likelihood_no_common_ancestor1():
    coincident_ranks = iter([0])
    p_differentia_collision = 0.5

    result = hstrat.estimate_rank_of_mrca_maximum_likelihood(
        coincident_ranks, p_differentia_collision, hstrat.ArbitraryPrior()
    )

    assert result is None


def test_estimate_rank_of_mrca_maximum_likelihood_with_common_ancestor1():
    coincident_ranks = iter([1, 0])
    p_differentia_collision = 0.5

    result = hstrat.estimate_rank_of_mrca_maximum_likelihood(
        coincident_ranks, p_differentia_collision, hstrat.ArbitraryPrior()
    )

    assert result == 0


def test_estimate_rank_of_mrca_maximum_likelihood_with_common_ancestor2():
    coincident_ranks = iter([7, 3, 0])
    p_differentia_collision = 0.5

    result = hstrat.estimate_rank_of_mrca_maximum_likelihood(
        coincident_ranks, p_differentia_collision, hstrat.ArbitraryPrior()
    )

    assert np.isclose(result, 4.5)


def test_estimate_rank_of_mrca_maximum_likelihood_with_common_ancestor3():
    coincident_ranks = [8, 7, 2, 0]
    p_differentia_collision = 0.5

    result = hstrat.estimate_rank_of_mrca_maximum_likelihood(
        coincident_ranks, p_differentia_collision, hstrat.ArbitraryPrior()
    )

    assert np.isclose(result, 7)


def test_estimate_rank_of_mrca_maximum_likelihood_with_common_ancestor4():
    coincident_ranks = [8, 7, 2, 0]
    p_differentia_collision = 0.5

    result = hstrat.estimate_rank_of_mrca_maximum_likelihood(
        coincident_ranks, p_differentia_collision, hstrat.UniformPrior()
    )

    assert np.isclose(result, 4)


def test_estimate_rank_of_mrca_maximum_likelihood_with_common_ancestor5():
    coincident_ranks = [8, 7, 2, 0]
    p_differentia_collision = 0.5**64

    result = hstrat.estimate_rank_of_mrca_maximum_likelihood(
        coincident_ranks, p_differentia_collision, hstrat.ArbitraryPrior()
    )

    assert np.isclose(result, 7)


def test_estimate_rank_of_mrca_maximum_likelihood_with_common_ancestor6():
    coincident_ranks = iter([7, 3, 0])
    p_differentia_collision = 0.5

    result = hstrat.estimate_rank_of_mrca_maximum_likelihood(
        coincident_ranks, p_differentia_collision, hstrat.UniformPrior()
    )

    assert np.isclose(result, 4.5)


def test_estimate_rank_of_mrca_maximum_likelihood_with_common_ancestor7():
    coincident_ranks = iter([7, 3, 0])
    p_differentia_collision = 0.5

    result = hstrat.estimate_rank_of_mrca_maximum_likelihood(
        coincident_ranks, p_differentia_collision, hstrat.GeometricPrior(1.1)
    )

    assert np.isclose(result, 6)
