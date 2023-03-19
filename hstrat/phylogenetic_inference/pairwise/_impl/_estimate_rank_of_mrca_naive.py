import typing

import numpy as np
import opytional as opyt

from ...._auxiliary_lib import HereditaryStratigraphicArtifact
from .._calc_rank_of_mrca_bounds_between import (
    calc_rank_of_mrca_bounds_between,
)


def estimate_rank_of_mrca_naive(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
) -> typing.Optional[float]:
    """Compute a simple, fast estimate the rank of the most recent common
    ancestor (MRCA).

    Returns None if the two hereditary stratigraphic artifacts definitvely
    share no common ancestor.
    """
    rank_of_mrca_bounds = calc_rank_of_mrca_bounds_between(
        first,
        second,
        prior="arbitrary",
        confidence_level=0.49,
    )
    exclusive_ub_correction = 1 / 2
    return opyt.apply_if(
        rank_of_mrca_bounds,
        lambda x: (np.mean(x) - exclusive_ub_correction),
    )
