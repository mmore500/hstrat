import typing

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ._estimate_ranks_since_mrca_with import estimate_ranks_since_mrca_with


def ballpark_ranks_since_mrca_with(
    focal: HereditaryStratigraphicArtifact,
    other: HereditaryStratigraphicArtifact,
) -> typing.Optional[float]:
    """Calculate a fast, rough estimate of generations elapsed since MRCA with
    other.

    See `estimate_ranks_since_mrca_with` for details.
    """
    return estimate_ranks_since_mrca_with(
        focal,
        other,
        estimator="maximum_likelihood",
        prior="arbitrary",
    )
