import typing

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ._estimate_patristic_distance_between import (
    estimate_patristic_distance_between,
)


def ballpark_patristic_distance_between(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
) -> typing.Optional[float]:
    """Calculate a fast, rough estimate of the patristic distance between first
    and second.

    See `estimate_patristic_distance_between` for details.
    """
    return estimate_patristic_distance_between(
        first,
        second,
        estimator="maximum_likelihood",
        prior="arbitrary",
    )
