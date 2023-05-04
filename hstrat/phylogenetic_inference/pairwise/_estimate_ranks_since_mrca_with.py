import math
import typing

import opytional as opyt

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ._estimate_rank_of_mrca_between import estimate_rank_of_mrca_between


def estimate_ranks_since_mrca_with(
    focal: HereditaryStratigraphicArtifact,
    other: HereditaryStratigraphicArtifact,
    estimator: str,
    prior: typing.Union[str, typing.Any],
) -> typing.Optional[float]:
    """How many generations have elapsed since focal's most recent common
    ancestor with other?

    More specifically, estimate the number of depositions elapsed along focal
    column's line of descent since the most recent common ancestor with other.

    Parameters
    ----------
    estimator : {"maximum_likelihood", "unbiased"}
        What estimation method should be used? Options are "maximum_likelihood"
        or "unbiased".

        See `estimate_ranks_since_mrca_with` for discussion of estimator
        options.
    prior : {"arbitrary", "uniform"} or object implementing prior interface

        Prior probability density distribution over possible generations of the
        MRCA.

        See `estimate_ranks_since_mrca_with` for discussion of prior
        options.

    Returns
    -------
    float, optional
        Estimate of generations elapsed since MRCA, unless first and second
        definitively share no common ancestor in which case None will be
        returned.

    See Also
    --------
    calc_ranks_since_mrca_bounds_with :
        Calculates confidence intervals for generations elapsed along one
        column's line of descent since most recent common ancestor with another
        column.
    does_definitively_have_no_common_anestor :
        Does the hereditary stratigraphic record definitively prove that first
        and second could not possibly share a common ancestor?
    """

    est_rank_of_mrca_between = estimate_rank_of_mrca_between(
        focal,
        other,
        estimator=estimator,
        prior=prior,
    )
    res = opyt.apply_if(
        est_rank_of_mrca_between,
        lambda est: focal.GetNumStrataDeposited()
        - 1
        - est_rank_of_mrca_between,
    )
    if res is not None:
        assert 0 <= res or math.isclose(0, res, abs_tol=10e-6)
        assert res <= focal.GetNumStrataDeposited() or math.isclose(
            res, focal.GetNumStrataDeposited()
        )
    return res
