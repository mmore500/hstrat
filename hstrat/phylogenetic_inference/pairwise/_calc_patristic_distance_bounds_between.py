import typing

import opytional as opyt

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ._calc_rank_of_mrca_bounds_between import calc_rank_of_mrca_bounds_between


def calc_patristic_distance_bounds_between(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
    prior: str,
    confidence_level: float = 0.95,
) -> typing.Optional[typing.Tuple[int, int]]:
    """What is the total phylogenetic distance along the branch path connecting
    first and second?

    Calculate confidence interval for patristic distance estimate. Branch
    length here is in terms of number of generations elapsed. So the
    calculated distance estimates the sum of the number of generations elapsed

    Parameters
    ----------
    prior : {"arbitrary"}
        Prior probability density distribution over possible generations of the
        MRCA.

        Currently only "arbitrary" supported.
    confidence_level : float, optional
        Bounds must capture what probability of containing the true patristic
        distance? Default 0.95.

    Returns
    -------
    (int, int), optional
        Inclusive lower and then exclusive upper bound on patristic distance
        estimate or None if no common ancestor between first and second can be
        resolved with sufficient confidence. (Sufficient confidence depends on
        confidence_level.)

    See Also
    --------
    calc_rank_of_earliest_detectable_mrca_between :
        Could any MRCA be detected between first and second? What is the rank
        of the earliest MRCA that could be reliably detected?
    does_definitively_have_no_common_anestor :
        Does the hereditary stratigraphic record definitively prove that first and second could not possibly share a common ancestor?

    Notes
    -----
    The true patristic distance is guaranteed to never fall below the returned bounds but may fall above.
    """

    mrca_rank_bounds = calc_rank_of_mrca_bounds_between(
        first, second, prior=prior
    )
    inclusive_exclusive_ub_lb_switch_correction = 2
    max_patristic_distance = (
        first.GetNumStrataDeposited() - 1 + second.GetNumStrataDeposited() - 1
    ) + inclusive_exclusive_ub_lb_switch_correction

    return opyt.apply_if(
        mrca_rank_bounds,
        lambda bounds: tuple(
            max_patristic_distance - 2 * bound for bound in reversed(bounds)
        ),
    )
