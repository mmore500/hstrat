import typing

from ...genome_instrumentation import HereditaryStratigraphicColumn
from ...juxtaposition import calc_rank_of_first_retained_disparity_between
from ._calc_rank_of_earliest_detectable_mrca_between import (
    calc_rank_of_earliest_detectable_mrca_between,
)


def does_have_any_common_ancestor(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    confidence_level: float = 0.95,
) -> typing.Optional[bool]:
    """Determine if common ancestry is evidenced with other.

    If insufficient common ranks between self and other are available to
    resolve any common ancestor, returns None.

    Note that stratum rention policies are strictly required to permanently
    retain the most ancient stratum.

    Parameters
    ----------
    confidence_level : float, optional
        The probability that we will correctly conclude no common ancestor
        is shared with other if, indeed, no common ancestor is actually
        shared. Default 0.95.

    See Also
    --------
    does_definitively_have_no_common_ancestor :
        Can we definitively conclude that self and other share no common
        ancestor?
    """
    if (
        self.CalcRankOfEarliestDetectableMrcaWith(
            other,
            confidence_level=confidence_level,
        )
        is None
    ):
        return None

    first_disparity = self.CalcRankOfFirstRetainedDisparityWith(
        other,
        confidence_level=confidence_level,
    )
    return True if first_disparity is None else first_disparity > 0
