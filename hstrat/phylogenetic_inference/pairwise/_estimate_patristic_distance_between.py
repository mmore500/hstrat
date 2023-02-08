import operator
import typing

import opytional as opyt

from ...genome_instrumentation import HereditaryStratigraphicColumn
from ._estimate_rank_of_mrca_between import estimate_rank_of_mrca_between


def estimate_patristic_distance_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    estimator: str,
    prior: str,
    prior_exponential_factor: typing.Optional[float] = None,
) -> typing.Optional[float]:
    """Estimate the total phylogenetic distance along the branch path connecting
    the columns.

    Branch length here is in terms of number of generations elapsed. So the
    calculated distance estimates the sum of the number of generations elapsed
    from each to their most recent common ancestor.

    Parameters
    ----------
    estimator : {"maximum_likelihood", "unbiased"}
        What estimation method should be used? Options are "maximum_likelihood"
        or "unbiased".

        See `estimate_ranks_since_mrca_with` for discussion of estimator
        options.
    prior : {"arbitrary", "uniform", "exponential"}
        Prior probability density distribution over possible generations of the
        MRCA.

        See `estimate_ranks_since_mrca_with` for discussion of prior
        options.
    prior_exponential_factor : optional float
        See `estimate_ranks_since_mrca_with` for discussion of estimator
        options.

    Returns
    -------
    float, optional
        Estimate of patristic distance, unless first and second definitively
        share no common ancestor in which case None will be returned.

    See Also
    --------
    calc_patristic_distance_bounds_between :
        Calculates confidence intervals for patristic distance between two
        hereditary stratigraphic columns.
    does_definitively_have_no_common_anestor :
        Does the hereditary stratigraphic record definitively prove that first and second could not possibly share a common ancestor?
    """

    est_rank_of_mrca_between = estimate_rank_of_mrca_between(
        first,
        second,
        estimator=estimator,
        prior=prior,
        prior_exponential_factor=prior_exponential_factor,
    )
    max_patristic_distance = (
        first.GetNumStrataDeposited() - 1 + second.GetNumStrataDeposited() - 1
    )

    return opyt.apply_if(
        est_rank_of_mrca_between,
        lambda est: max_patristic_distance - 2 * est,
    )


def ballpark_patristic_distance_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
) -> typing.Optional[float]:
    """Calculate a fast, rough estimate of the patristic distance between first
    and second.

    See `estimate_patristic_distance_between` for details.
    """

    return estimate_patristic_distance_between(
        first,
        second,
        estimator="maximum_likelihood",
        prior="arbitrary",
    )