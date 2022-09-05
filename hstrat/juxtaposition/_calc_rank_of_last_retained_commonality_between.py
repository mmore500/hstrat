import typing

from ..genome_instrumentation import (
    HereditaryStratigraphicColumn,
    HereditaryStratumOrderedStoreDict,
    HereditaryStratumOrderedStoreList,
)
from ._impl import (
    calc_rank_of_last_retained_commonality_between_bsearch,
    calc_rank_of_last_retained_commonality_between_generic,
)


def calc_rank_of_last_retained_commonality_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    confidence_level: float = 0.95,
) -> typing.Optional[int]:
    """Determine lower bound on generation of MRCA at confidence level.

    How many depositions elapsed along the columns' lines of
    descent before the last matching strata at the same rank between
    self and other?

    Parameters
    ----------
    confidence_level : float, optional
        With what probability should the true rank of the last commonality
        with other fall at or after the returned rank? Default 0.95.

    Returns
    -------
    int, optional
        The number of depositions elapsed or None if no common ancestor is
        shared between the columns.

    Notes
    -----
    The true rank of the last commonality with other is guaranteed to never
    be after the returned rank when confidence_level < 0.5.
    """
    assert 0.0 <= confidence_level <= 1.0

    if (
        self.HasDiscardedStrata()
        or other.HasDiscardedStrata()
        # for performance reasons
        # only binary search stores that support random access
        or not isinstance(
            self._stratum_ordered_store, HereditaryStratumOrderedStoreList
        )
        or not isinstance(
            other._stratum_ordered_store, HereditaryStratumOrderedStoreList
        )
        # binary search currently requires no spurious collisions
        or self._stratum_differentia_bit_width < 64
    ):
        return self._do_generic_CalcRankOfLastRetainedCommonalityWith(
            other,
            confidence_level=confidence_level,
        )
    else:
        return self._do_binary_search_CalcRankOfLastRetainedCommonalityWith(
            other,
            confidence_level=confidence_level,
        )
