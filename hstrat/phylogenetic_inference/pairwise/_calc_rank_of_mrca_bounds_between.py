import typing
import warnings

import opytional as opyt

from ...genome_instrumentation import HereditaryStratigraphicColumn
from ...juxtaposition import (
    calc_definitive_max_rank_of_first_retained_disparity_between,
    calc_rank_of_last_retained_commonality_between,
)
from ._calc_rank_of_earliest_detectable_mrca_between import (
    calc_rank_of_earliest_detectable_mrca_between,
)
from ._does_have_any_common_ancestor import does_have_any_common_ancestor


def calc_rank_of_mrca_bounds_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    confidence_level: float = 0.95,
) -> typing.Optional[typing.Tuple[int, int]]:
    """Within what generation range did MRCA fall?

    Calculate bounds on estimate for the number of depositions elapsed
    along the line of descent before the most recent common ancestor with
    second.

    Parameters
    ----------
    confidence_level : float, optional
        Bounds must capture what probability of containing the true rank of
        the MRCA? Default 0.95.

    Returns
    -------
    (int, int), optional
        Inclusive lower and then exclusive upper bound on estimate or None
        if no common ancestor between first and second can be resolved with
        sufficient confidence. (Sufficient confidence depends on
        confidence_level.)

    See Also
    --------
    calc_rank_of_mrca_uncertainty_between :
        Wrapper to report uncertainty of calculated bounds.
    calc_rank_of_earliest_detectable_mrca_between :
        Could any MRCA be detected between first and second? What is the rank
        of the earliest MRCA that could be reliably detected?
    calc_rank_of_mrca_bounds_provided_confidence_level :
        With what actual confidence (i.e., more than requested) is the true
        rank of the MRCA captured within the calculated bounds?

    Notes
    -----
    The true rank of the MRCA is guaranteed to never fall above the bounds
    but may fall below.

    An alternate approach could be to construct the bounds such that the
    true rank of the MRCA will fall above or below the bounds with equal
    probability. This would involve setting the confidence level for
    calculating the first disparity with second to significance_level/2 and
    the confidence level for calculaing the last comonality with second to
    1 - significance_level/2. This means the confidence level applied to
    calculating the first disparity with second would always be <= 0.5.
    However, shifting the calculated first disparity with second below
    the definitive max first retained disparity requires confidence level
    >= 0.5. So, in practice such a symmetric approach would only result in
    the lower bound being shifted downward. For this reason, it is no longer
    provided as an option.

    In the absence of evidence to the contrary (i.e., more common
    strata than spurious differentia collisions alone could plausibly
    cause), this method assumes no common ancestry between first and second,
    returning None. This means that if few enough common ranks are shared
    between first and second (and the differentia bit with is small enough),
    it may not be possible to detect any common ancestry after accounting
    for the possibility of spurious differentia collisions (even if common
    ancestry did exist). So, calls to this method would always return None.
    Likewise, MRCAs at very early ranks may not be able to be reliably
    detected due to insufficient evidence. This can lead to cases where
    columns with true common ancestry have MRCA bounds estimated as None at
    much higher than the expected failure rate at the given confidence
    level. Note that with sufficient differentia bit width (i.e., so that
    even one collision is implausible at the given confidence level) this
    issue does not occur. Use CalcRankOfEarliestDetectableMrcaWith to
    determine the earliest rank at which an MRCA could be reliably detected
    between first and second.
    """
    assert 0.0 <= confidence_level <= 1.0

    if (
        calc_rank_of_earliest_detectable_mrca_between(
            first,
            second,
            confidence_level=confidence_level,
        )
        is None
    ):
        warnings.warn(
            "Insufficient common ranks between columns to detect common "
            "ancestry at given confidence level."
        )

    if does_have_any_common_ancestor(
        first,
        second,
        confidence_level=confidence_level,
    ):
        first_disparity = (
            calc_definitive_max_rank_of_first_retained_disparity_between(
                first,
                second,
            )
        )
        if first_disparity is None:
            num_self_deposited = first.GetNumStrataDeposited()
            num_other_deposited = second.GetNumStrataDeposited()
            assert num_self_deposited == num_other_deposited
        last_commonality = calc_rank_of_last_retained_commonality_between(
            first,
            second,
            confidence_level=confidence_level,
        )
        assert last_commonality is not None
        return (
            last_commonality,
            opyt.or_value(first_disparity, first.GetNumStrataDeposited()),
        )
    else:
        return None
