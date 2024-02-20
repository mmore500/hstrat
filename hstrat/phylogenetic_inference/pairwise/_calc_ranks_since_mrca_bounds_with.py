import typing
import warnings

import opytional as opyt

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ...juxtaposition import (
    calc_definitive_min_ranks_since_first_retained_disparity_with,
    calc_ranks_since_last_retained_commonality_with,
)
from ._calc_rank_of_earliest_detectable_mrca_between import (
    calc_rank_of_earliest_detectable_mrca_between,
)
from ._does_have_any_common_ancestor import does_have_any_common_ancestor


def calc_ranks_since_mrca_bounds_with(
    focal: HereditaryStratigraphicArtifact,
    other: HereditaryStratigraphicArtifact,
    prior: typing.Literal["arbitrary"],
    confidence_level: float = 0.95,
) -> typing.Optional[typing.Tuple[int, int]]:
    """How many generations have elapsed since MRCA?

    Calculate bounds on estimate for the number of depositions elapsed
    along focal column's line of descent since the most recent common
    ancestor with other.

    Parameters
    ----------
    prior : {"arbitrary"}
        Prior probability density distribution over possible generations of the
        MRCA.

        Currently only "arbitrary" supported.
    confidence_level : float, optional
        With what probability should the true rank of the MRCA fall
        within the calculated bounds? Default 0.95.

    Returns
    -------
    (int, int), optional
        Inclusive lower bound and then exclusive upper bound on estimate or
        None if no common ancestor between focal and other can be resolved
        with sufficient confidence. (Sufficient confidence depends on
        bound_type.)

    See Also
    --------
    calc_ranks_since_mrca_uncertainty_between :
        Wrapper to report uncertainty of calculated bounds.
    calc_ranks_since_earliest_detectable_mrca_between :
        Could any MRCA be detected between focal and other? How many ranks
        have elapsed since the earliest MRCA that could be reliably
        detected?
    calc_ranks_since_mrca_bounds_provided_confidence_level :
        With what actual confidence (i.e., more than requested) is the true
        rank of the MRCA captured within the calculated bounds?
    does_definitively_have_no_common_anestor :
        Does the hereditary stratigraphic record definitively prove that first
        and second could not possibly share a common ancestor?

    Notes
    -----
    The true number of ranks since the MRCA is guaranteed to never fall
    below the bounds but may fall above.

    An alternate approach could be to construct the bounds such that the
    true number of ranks since the MRCA will fall above or below the bounds
    with equal probability. This would involve setting the confidence level
    for calculating the first disparity with other to significance_level/2
    and the confidence level for calculaing the last comonality with other
    to 1 - significance_level/2. This means the confidence level applied to
    calculating the first disparity with other would always be <= 0.5.
    However, shifting the calculated first disparity with other above
    the definitive min first retained disparity requires confidence level
    >= 0.5. So, in practice such a symmetric approach would only result in
    the upper bound being shifted upward. For this reason, it is no longer
    provided as an option.

    In the absence of evidence to the contrary (i.e., more common
    strata than spurious differentia collisions alone could plausibly
    cause), this method assumes no common ancestry between focal and other,
    returning None. This means that if few enough common ranks are shared
    between focal and other (and the differentia bit with is small enough),
    it may not be possible to detect any common ancestry after accounting
    for the possibility of spurious differentia collisions (even if common
    ancestry did exist). So, calls to this method would always return None.
    Likewise, MRCAs at very early ranks may not be able to be reliably
    detected due to insufficient evidence. This can lead to cases where
    columns with true common ancestry have MRCA bounds estimated as None at
    much higher than the expected failure rate at the given confidence
    level. Note that with sufficient differentia bit width (i.e., so that
    even one collision is implausible at the given confidence level) this
    issue does not occur. Use CalcRanksSinceEarliestDetectableMrcaWith to
    determine the earliest rank at which an MRCA could be reliably detected
    between focal and other.
    """
    if prior != "arbitrary":
        raise NotImplementedError
    assert 0.0 <= confidence_level <= 1.0

    if (
        calc_rank_of_earliest_detectable_mrca_between(
            focal,
            other,
            confidence_level=confidence_level,
        )
        is None
    ):
        warnings.warn(
            "Insufficient common ranks between columns to detect common "
            "ancestry at given confidence level."
        )

    if does_have_any_common_ancestor(
        focal,
        other,
        confidence_level=confidence_level,
    ):
        since_first_disparity = (
            calc_definitive_min_ranks_since_first_retained_disparity_with(
                focal,
                other,
            )
        )

        lb_exclusive = opyt.or_value(since_first_disparity, -1)
        lb_inclusive = lb_exclusive + 1

        since_last_commonality = (
            calc_ranks_since_last_retained_commonality_with(
                focal,
                other,
                confidence_level=confidence_level,
            )
        )
        assert since_last_commonality is not None
        ub_inclusive = since_last_commonality
        ub_exclusive = ub_inclusive + 1

        return (lb_inclusive, ub_exclusive)
    else:
        return None
