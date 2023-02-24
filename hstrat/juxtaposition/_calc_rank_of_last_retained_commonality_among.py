import typing

import opytional as opyt

from .._auxiliary_lib import HereditaryStratigraphicArtifact, pairwise
from ._calc_rank_of_last_retained_commonality_between import (
    calc_rank_of_last_retained_commonality_between,
)


def calc_rank_of_last_retained_commonality_between_(
    c1, c2, confidence_level=0.95
):
    return opyt.or_value(
        calc_rank_of_last_retained_commonality_between(
            c1, c2, confidence_level=confidence_level
        ),
        0,
    )


def calc_rank_of_last_retained_commonality_among(
    population: typing.Iterable[HereditaryStratigraphicArtifact],
    confidence_level=0.95,
) -> typing.Optional[int]:
    """Determine lower bound on generation of MRCA at confidence level.

    How many depositions elapsed along the columns' lines of
    descent before the last matching strata at the same rank between
    first and second?

    Parameters
    ----------
    confidence_level : float, optional
        With what probability should the true rank of the last commonality
        between first and second fall at or after the returned rank? Default
        0.95.

    Returns
    -------
    int, optional
        The number of depositions elapsed or None if no common ancestor is
        shared between the columns.

    Notes
    -----
    The true rank of the last commonality with second is guaranteed to never
    be after the returned rank when confidence_level < 0.5.
    """
    # assert 0.0 <= confidence_level <= 1.0
    population = [*population]

    if not population:
        return None
    elif len(population) == 1:
        return population[0].GetNumStrataDeposited() - 1
    else:
        # TODO handle NONE
        return max(
            calc_rank_of_last_retained_commonality_between_(
                *pair, confidence_level=confidence_level
            )
            for pair in pairwise(population)
        )
