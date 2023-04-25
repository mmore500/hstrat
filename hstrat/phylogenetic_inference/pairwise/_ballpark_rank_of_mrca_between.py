import typing

from ..._auxiliary_lib import HereditaryStratigraphicArtifact
from ._estimate_rank_of_mrca_between import estimate_rank_of_mrca_between


def ballpark_rank_of_mrca_between(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
) -> typing.Optional[float]:
    """Calculate a fast, rough estimate of the rank of the MRCA beteen first
    and second.

    See `estimate_rank_of_mrca_between` for details.
    """
    return estimate_rank_of_mrca_between(
        first,
        second,
        estimator="maximum_likelihood",
        prior="arbitrary",
    )
