import typing

from iterpop import iterpop as ip

from ..genome_instrumentation import (
    HereditaryStratigraphicColumn,
    HereditaryStratum,
)
from ._calc_rank_of_last_retained_commonality_between import (
    calc_rank_of_last_retained_commonality_between,
)


def get_last_common_stratum_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    confidence_level: float = 0.95,
) -> typing.Optional[HereditaryStratum]:
    """Get the most recent stratum in common between first and second, if any.

    Common strata share identical rank and differentia. Returns None if no
    common strata exist between the two columns. Allows probability equal
    to 1 - confidence_level that the last true common stratum is before the
    stratum returned (i.e., strata were erroneously detected as common due
    to spurious differentia collisions).

    See Also
    --------
    calc_rank_of_last_retained_commonality_between :
        Selects the stratum returned. See the corresponding docstring for
        explanation of parameters.
    """
    rank = calc_rank_of_last_retained_commonality_between(
        first,
        second,
        confidence_level=confidence_level,
    )
    if rank is not None:
        index = ip.popsingleton(
            index
            for index in range(first.GetNumStrataRetained())
            if rank == first.GetRankAtColumnIndex(index)
        )
        return first.GetStratumAtColumnIndex(index)
    else:
        return None
