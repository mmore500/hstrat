import typing

import numpy as np

from ..._auxiliary_lib import cmp_approx, pairwise


def estimate_rank_of_mrca_maximum_likelihood(
    coincident_ranks_from_first_disparity_through_first_commonality: typing.Iterator[
        int
    ],
    p_differentia_collision: float,
    prior: object,
) -> typing.Optional[float]:
    """Estimate the most recent common ancestor (MRCA) at the rank with the
    highest posterior probability.

    Parameters
    ----------
    coincident_ranks_from_first_disparity_through_first_commonality
    : typing.Iterator[int]
        Iterator of integer values indicating the coincident ranks between two
        taxa.

        Inclusive to first disparity and first commonality.
    p_differentia_collision : float
        The multiplicative inverse of the number of possible differentia.
    prior : object
        Prior expectation for the distribution of MRCA generation
        between hereditary stratigraphic columns/

    Returns
    -------
    typing.Optional[float]
        Estimated rank of the MRCA, or None if the two hereditary stratigraphic
        artifacts definitvely share no common ancestor.

    Notes
    -----
    The midpoint rank will be estimated for windows of equal posterior
    probability.
    """

    base = p_differentia_collision

    max_weight, best_expected_rank = -1.0, None
    for (
        num_spurious_collisions,
        (
            end_exclusive,
            begin_inclusive,
        ),
    ) in enumerate(
        pairwise(
            coincident_ranks_from_first_disparity_through_first_commonality
        )
    ):
        cur_weight = (
            base**num_spurious_collisions
            * prior.CalcIntervalProbabilityProxy(
                begin_inclusive, end_exclusive
            )
        )
        assert cur_weight >= 0

        if cur_weight > max_weight:
            max_weight = cur_weight
            # slide to most likely end of interval
            # assumes monotonicity of prior
            best_expected_rank = {
                1: end_exclusive - 1,
                0: np.mean((end_exclusive - 1, begin_inclusive)),
                -1: begin_inclusive,
            }[
                cmp_approx(
                    prior.CalcIntervalConditionedMean(
                        begin_inclusive, end_exclusive
                    ),
                    np.mean((end_exclusive - 1, begin_inclusive)),
                )
            ]

        # if whole rest of the remaining record cannot have higher cur_weight
        # than best, terminate early
        if (
            begin_inclusive
            and base ** (num_spurious_collisions + 1)
            * prior.CalcIntervalProbabilityProxy(
                0,
                begin_inclusive,
            )
            < max_weight
        ):
            break

    assert max_weight > 0.0 or best_expected_rank is None

    # may be None if only one waypoint provided
    return best_expected_rank
