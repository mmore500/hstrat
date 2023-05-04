import itertools as it
import typing

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ._calc_rank_of_earliest_detectable_mrca_among import (
    calc_rank_of_earliest_detectable_mrca_among,
)
from ._calc_rank_of_mrca_bounds_among import calc_rank_of_mrca_bounds_among


def does_share_any_common_ancestor(
    population: typing.Iterable[HereditaryStratigraphicArtifact],
    confidence_level: float = 0.95,
) -> typing.Optional[bool]:
    """Determine if common ancestry is evidenced within the population.

    If insufficient common ranks between strata are available to
    resolve any common ancestor, returns None.

    Note that stratum rention policies are strictly required to permanently
    retain the most ancient stratum.

    Parameters
    ----------
    confidence_level : float, optional
        The probability that we will correctly conclude no common ancestor
        is shared if, indeed, no common ancestor is actually shared. Default
        0.95.

    See Also
    --------
    does_definitively_share_no_common_ancestor :
        Can we definitively conclude that first and second share no common
        ancestor?
    """
    pop_tee1, pop_tee2 = it.tee(population)

    if (
        calc_rank_of_earliest_detectable_mrca_among(
            pop_tee1,
            confidence_level=confidence_level,
        )
        is None
    ):
        return None

    mrca_bounds = calc_rank_of_mrca_bounds_among(
        pop_tee2, "arbitrary", confidence_level
    )
    return mrca_bounds is not None
