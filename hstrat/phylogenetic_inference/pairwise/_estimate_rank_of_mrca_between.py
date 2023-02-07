import statistics
import typing

from iterpop import iterpop as ip
import numpy as np
import opytional as opyt

from ..._auxiliary_lib import pairwise, unzip
from ...genome_instrumentation import HereditaryStratigraphicColumn
from ...juxtaposition import calc_rank_of_first_retained_disparity_between
from ...juxtaposition._impl import (
    iter_ranks_of_retained_commonality_between_generic,
)
from ._calc_rank_of_mrca_bounds_between import calc_rank_of_mrca_bounds_between


def _estimate_rank_of_mrca_between_maximum_likelihood(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
) -> typing.Optional[float]:
    rank_of_mrca_bounds = calc_rank_of_mrca_bounds_between(
        first,
        second,
        confidence_level=0.49,
    )
    exclusive_ub_correction = 1 / 2
    return opyt.apply_if(
        rank_of_mrca_bounds,
        lambda x: (statistics.mean(x) - exclusive_ub_correction),
    )


# tried a numpy-based implementation but it was slower
# https://gist.github.com/mmore500/fc4caba18a98b20fbda3fb223cf49552
def _estimate_rank_of_mrca_between_unbiased(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
) -> typing.Optional[float]:
    ranks_of_retained_commonality_between = [
        *iter_ranks_of_retained_commonality_between_generic(first, second)
    ]
    if not ranks_of_retained_commonality_between:
        return None

    rank_of_first_retained_disparity_between = opyt.or_else(
        calc_rank_of_first_retained_disparity_between(
            first,
            second,
            confidence_level=0.49,
        ),
        lambda: ip.pophomogeneous(
            (
                first.GetNumStrataDeposited(),
                second.GetNumStrataDeposited(),
            )
        ),
    )
    waypoints_descending = [
        rank_of_first_retained_disparity_between,
        *reversed(ranks_of_retained_commonality_between),
    ]

    base = 1 / 2 ** first.GetStratumDifferentiaBitWidth()
    expected_ranks, weights = tuple(
        unzip(
            (
                # expected rank
                statistics.mean((end_exclusive - 1, begin_inclusive)),
                # weight
                base**num_spurious_collisions,
            )
            for (
                num_spurious_collisions,
                (
                    begin_inclusive,
                    end_exclusive,
                ),
            ) in enumerate(pairwise(waypoints_descending))
        )
    )

    return np.average(
        np.array(expected_ranks),
        weights=np.array(weights),
    )


def estimate_rank_of_mrca_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    estimator: str = "maximum_likelihood",
) -> typing.Optional[float]:
    """At what generation did the most recent common ancestor of first and
    second occur?

    Parameters
    ----------
    estimator : str, default "maximum_likelihood"
        What estimation method should be used? Options are "maximum_likelihood"
        or "unbiased".

        The "maximum_likelihood" estimator is faster to compute than the
        "unbiased" estimator.

    Returns
    -------
    float, optional
        Estimate of MRCA rank, unless first and second definitively share no
        common ancestor in which case None will be returned.

    See Also
    --------
    calc_rank_of_mrca_bounds_between :
        Calculates confidence intervals for generation of most recent common ancestor between two hereditary stratigraphic columns.
    does_definitively_have_no_common_anestor :
        Does the hereditary stratigraphic record definitively prove that first and second could not possibly share a common ancestor?
    """

    return {
        "maximum_likelihood": _estimate_rank_of_mrca_between_maximum_likelihood,
        "unbiased": _estimate_rank_of_mrca_between_unbiased,
    }[estimator](first, second)
