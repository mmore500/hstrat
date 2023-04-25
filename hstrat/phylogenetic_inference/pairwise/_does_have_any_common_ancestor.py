import typing

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ...juxtaposition import calc_rank_of_first_retained_disparity_between
from ._calc_rank_of_earliest_detectable_mrca_between import (
    calc_rank_of_earliest_detectable_mrca_between,
)


def does_have_any_common_ancestor(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
    confidence_level: float = 0.95,
) -> typing.Optional[bool]:
    """Determine if common ancestry is evidenced with second.

    If insufficient common ranks between first and second are available to
    resolve any common ancestor, returns None.

    Note that stratum rention policies are strictly required to permanently
    retain the most ancient stratum.

    Parameters
    ----------
    confidence_level : float, optional
        The probability that we will correctly conclude no common ancestor
        is shared with second if, indeed, no common ancestor is actually
        shared. Default 0.95.

    See Also
    --------
    does_definitively_have_no_common_ancestor :
        Can we definitively conclude that first and second share no common
        ancestor?
    """
    if (
        calc_rank_of_earliest_detectable_mrca_between(
            first,
            second,
            confidence_level=confidence_level,
        )
        is None
    ):
        return None

    first_disparity = calc_rank_of_first_retained_disparity_between(
        first,
        second,
        confidence_level=confidence_level,
    )
    return True if first_disparity is None else first_disparity > 0
