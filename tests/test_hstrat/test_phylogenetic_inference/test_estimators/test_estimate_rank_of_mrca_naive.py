import numpy as np

from hstrat import hstrat


def test_estimate_rank_of_mrca_naive_no_common_ancestor():
    coincident_ranks = iter([0])
    p_differentia_collision = 0.5
    prior = object()

    result = hstrat.estimate_rank_of_mrca_naive(
        coincident_ranks, p_differentia_collision, prior
    )

    assert result is None


def test_estimate_rank_of_mrca_naive_with_common_ancestor1b():
    coincident_ranks = iter([1, 0])
    p_differentia_collision = 0.5

    result = hstrat.estimate_rank_of_mrca_naive(
        coincident_ranks, p_differentia_collision, hstrat.ArbitraryPrior()
    )

    assert result == 0


def test_estimate_rank_of_mrca_naive_with_common_ancestor1():
    coincident_ranks = iter([7, 3, 0])
    p_differentia_collision = 0.5
    prior = object()

    result = hstrat.estimate_rank_of_mrca_naive(
        coincident_ranks, p_differentia_collision, prior
    )

    assert isinstance(result, float)
    assert np.isclose(result, 4.5)


def test_estimate_rank_of_mrca_naive_with_common_ancestor2():
    coincident_ranks = [8, 7, 2, 0]
    p_differentia_collision = 0.5
    prior = object()

    result = hstrat.estimate_rank_of_mrca_naive(
        coincident_ranks, p_differentia_collision, prior
    )

    assert isinstance(result, float)
    assert np.isclose(result, 7)
