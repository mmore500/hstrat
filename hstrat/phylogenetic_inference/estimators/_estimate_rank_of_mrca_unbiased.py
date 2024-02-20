import typing

import numpy as np

from ..._auxiliary_lib import pairwise
from ..priors._detail import PriorBase


# tried a numpy-based implementation but it was slower
# https://gist.github.com/mmore500/fc4caba18a98b20fbda3fb223cf49552
def estimate_rank_of_mrca_unbiased(
    coincident_ranks_from_first_disparity_through_first_commonality: typing.Iterator[
        int
    ],
    p_differentia_collision: float,
    prior: PriorBase,
) -> typing.Optional[float]:
    """Compute an estimate for the rank of the most recent common ancestor (MRCA) that, on average, avoids systematic over- or under-estimation.

    Parameters
    ----------
    coincident_ranks_from_first_disparity_through_first_commonality : typing.Iterator[int]
        Iterator of integer values indicating the coincident ranks between two taxa.

        Inclusive to first disparity and first commonality.
    p_differentia_collision : float
        The multiplicative inverse of the number of possible differentia.
    prior : PriorBase
        Prior expectation for the distribution of MRCA generation
        between hereditary stratigraphic columns.

    Returns
    -------
    typing.Optional[float]
        Estimated rank of the MRCA, or None if the two hereditary stratigraphic
        artifacts definitively share no common ancestor.
    """

    base = p_differentia_collision

    weights, expected_ranks, sum_weight = [], [], 0.0
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
        expected_ranks.append(
            prior.CalcIntervalConditionedMean(begin_inclusive, end_exclusive)
        )
        weights.append(
            base**num_spurious_collisions
            * prior.CalcIntervalProbabilityProxy(
                begin_inclusive, end_exclusive
            )
        )
        sum_weight += weights[-1]

        # if whole rest of the remaining record cannot meaningfully impact
        # average, exit early
        if (
            begin_inclusive
            and base ** (num_spurious_collisions + 1)
            * prior.CalcIntervalProbabilityProxy(
                0,
                begin_inclusive,
            )
            * begin_inclusive
            < sum_weight * 10e-6  # numpy uses reltol 10e-5
        ):
            break

    try:
        return np.average(
            np.array(expected_ranks),
            weights=np.array(weights),
        )
    except ZeroDivisionError:
        # handle empty array case
        return None
