import typing

from .._auxiliary_lib import HereditaryStratigraphicArtifact
from ._impl import dispatch_impl


def calc_rank_of_last_retained_commonality_between(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
    confidence_level: float = 0.95,
) -> typing.Optional[int]:
    """Determine lower bound on generation of MRCA at confidence level.

    How many depositions elapsed along the columns' lines of
    descent before the last matching strata at the same rank between
    first and second?

    Parameters
    ----------
    confidence_level : float, optional
        With what probability should the true rank of the last commonality
        between first and second fall at or after the returned rank? Default
        0.95.

    Returns
    -------
    int, optional
        The number of depositions elapsed or None if no common ancestor is
        shared between the columns.

    Notes
    -----
    The true rank of the last commonality with second is guaranteed to never
    be after the returned rank when confidence_level < 0.5.
    """
    assert 0.0 <= confidence_level <= 1.0

    return dispatch_impl(
        first, second
    ).calc_rank_of_last_retained_commonality_between(
        first, second, confidence_level
    )
