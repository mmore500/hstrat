import itertools as it
import typing

import numpy as np


def estimate_rank_of_mrca_naive(
    coincident_ranks_from_first_disparity_through_first_commonality: typing.Iterator[
        int
    ],
    p_differentia_collision: float,
    prior: object,
) -> typing.Optional[float]:
    """Compute a simple, fast estimate the rank of the most recent common
    ancestor (MRCA).

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
    This function estimates the rank of the MRCA by computing the mean of the
    first retained disparite rank and the last retained common rank, with a correction factor for upper bound exclusivity.
    """

    rank_of_mrca_bounds = tuple(
        it.islice(
            coincident_ranks_from_first_disparity_through_first_commonality,
            2,
        )
    )
    assert len(rank_of_mrca_bounds)
    if len(rank_of_mrca_bounds) == 1:
        # rank 0 is a disparity --- definitively share no common ancestor
        return None

    exclusive_ub_correction = 1 / 2
    return np.mean(rank_of_mrca_bounds) - exclusive_ub_correction
