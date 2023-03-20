import typing

import numpy as np
import opytional as opyt

from ...._auxiliary_lib import HereditaryStratigraphicArtifact
from ...estimators import (
    estimate_rank_of_mrca_naive as estimate_rank_of_mrca_naive_,
)
from .._calc_rank_of_mrca_bounds_between import (
    calc_rank_of_mrca_bounds_between,
)


def estimate_rank_of_mrca_naive(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
) -> typing.Optional[float]:
    """Forwards to estimate_rank_of_mrca_naive estimator."""
    # optimization: naive estimator only consideres at the two ranks on either
    # side of the first retained disparity, so only extract those ranks
    rank_of_mrca_bounds = calc_rank_of_mrca_bounds_between(
        first,
        second,
        prior="arbitrary",
        confidence_level=0.49,
    )
    return estimate_rank_of_mrca_naive_(
        # in case of no shared ancestry, rank 0 is first disparity
        opyt.or_value(rank_of_mrca_bounds, [0]),
        p_differentia_collision=np.nan,
        prior=object(),
    )
