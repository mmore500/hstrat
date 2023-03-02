import typing

import numpy as np
import opytional as opyt

from ....genome_instrumentation import HereditaryStratigraphicColumn
from .._calc_rank_of_mrca_bounds_between import (
    calc_rank_of_mrca_bounds_between,
)


def estimate_rank_of_mrca_naive(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
) -> typing.Optional[float]:

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
