import typing

import opytional as opyt

from ...genome_instrumentation import HereditaryStratigraphicColumn
from ._calc_rank_of_earliest_detectable_mrca_between import (
    calc_rank_of_earliest_detectable_mrca_between,
)


def calc_ranks_since_earliest_detectable_mrca_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    confidence_level: float = 0.95,
) -> typing.Optional[int]:
    """How long since first generation common ancestor could be detected?

    How many depositions have elapsed since the earliest possible rank a
    MRCA between self and other could be reliably detected at?

    Even if a true MRCA of self and other exists, if it occured earlier
    than the rank calculated here it could not be reliably detected with
    sufficient confidence after accounting for the possibility of spurious
    differentia collisions. (Although subsequent spurious differentia
    collisions after the true MRCA of self and other could lead to MRCA
    detection at such a rank.)

    Returns None if insufficient common ranks exist between self and other
    to ever conclude at the given confidence level the existance of any
    common ancestry between self and other (even if all strata at common
    ranks had equivalent differentiae).
    """
    return opyt.apply_if(
        self.CalcRankOfEarliestDetectableMrcaWith(
            other,
            confidence_level=confidence_level,
        ),
        lambda rank: self.GetNumStrataDeposited() - 1 - rank,
    )
