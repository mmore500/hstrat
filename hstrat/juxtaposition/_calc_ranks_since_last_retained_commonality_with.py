import typing

from .._auxiliary_lib import HereditaryStratigraphicArtifact
from ._calc_rank_of_last_retained_commonality_between import (
    calc_rank_of_last_retained_commonality_between,
)


def calc_ranks_since_last_retained_commonality_with(
    focal: HereditaryStratigraphicArtifact,
    other: HereditaryStratigraphicArtifact,
    confidence_level: float = 0.95,
) -> typing.Optional[int]:
    """Determine generations since MRCA with particular confidence.

    How many depositions have elapsed along the focal column's line of
    descent since the last matching strata at the same rank between focal and
    other?

    Returns None if no common ancestor is shared between focal and other.

    Parameters
    ----------
    confidence_level : float, optional
        With what probability should the true number of ranks since the
        last commonality with other be less than the calculated estimate?
        Default 0.95.

    Notes
    -----
    If confidence_level < 0.5, then the true number of ranks since the last
    commonality with other is guaranteed greater than or equal to the
    calculated estimate.
    """
    assert 0.0 <= confidence_level <= 1.0

    last_common_rank = calc_rank_of_last_retained_commonality_between(
        focal,
        other,
        confidence_level=confidence_level,
    )
    if last_common_rank is None:
        return None
    else:
        assert focal.GetNumStrataDeposited()
        res = focal.GetNumStrataDeposited() - 1 - last_common_rank
        assert 0 <= res < focal.GetNumStrataDeposited()
        return res
