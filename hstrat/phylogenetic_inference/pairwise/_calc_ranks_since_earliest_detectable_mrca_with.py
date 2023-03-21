import typing

import opytional as opyt

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ._calc_rank_of_earliest_detectable_mrca_between import (
    calc_rank_of_earliest_detectable_mrca_between,
)


def calc_ranks_since_earliest_detectable_mrca_with(
    focal: HereditaryStratigraphicArtifact,
    other: HereditaryStratigraphicArtifact,
    confidence_level: float = 0.95,
) -> typing.Optional[int]:
    """How many generations have elapsed since the first where common ancestry
    with other could be detected?

    How many depositions have elapsed along focal's lineage since the earliest
    possible rank a MRCA between focal and other could be reliably detected at?

    Even if a true MRCA of focal and other exists, if it occured earlier
    than the rank calculated here it could not be reliably detected with
    sufficient confidence after accounting for the possibility of spurious
    differentia collisions. (Although subsequent spurious differentia
    collisions after the true MRCA of focal and other could lead to MRCA
    detection at such a rank.)

    Returns None if insufficient common ranks exist between focal and other
    to ever conclude at the given confidence level the existance of any
    common ancestry between focal and other (even if all strata at common
    ranks had equivalent differentiae).
    """
    return opyt.apply_if(
        calc_rank_of_earliest_detectable_mrca_between(
            focal,
            other,
            confidence_level=confidence_level,
        ),
        lambda rank: focal.GetNumStrataDeposited() - 1 - rank,
    )
