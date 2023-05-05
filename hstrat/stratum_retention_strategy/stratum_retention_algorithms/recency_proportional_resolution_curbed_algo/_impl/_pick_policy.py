from ..._detail import PolicyCouplerBase
from ...geom_seq_nth_root_algo import Policy as gsnra_Policy
from ...recency_proportional_resolution_algo import Policy as rpra_Policy
from ._calc_provided_degree import calc_provided_degree
from ._calc_provided_resolution import calc_provided_resolution


def pick_policy(
    size_curb: int,
    num_stratum_depositions_completed: int,
) -> PolicyCouplerBase:
    """Helper that dispatches current retention policy after n depositions."""
    resolution = calc_provided_resolution(
        size_curb,
        num_stratum_depositions_completed,
    )

    if resolution >= 0:
        return rpra_Policy(
            resolution,
        )
    else:
        interspersal = 2
        degree = calc_provided_degree(
            size_curb,
            interspersal,
            num_stratum_depositions_completed,
        )
        return gsnra_Policy(
            degree,
            interspersal,
        )
