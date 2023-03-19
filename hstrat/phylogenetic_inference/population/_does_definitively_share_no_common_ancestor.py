import itertools as it
import typing
import warnings

from ..._auxiliary_lib import HereditaryStratigraphicArtifact


def does_definitively_share_no_common_ancestor(
    population: typing.Iterable[HereditaryStratigraphicArtifact],
) -> typing.Optional[bool]:
    """Could the population possibly share a common ancestor?

    Note that stratum rention policies are strictly required to permanently
    retain the most ancient stratum.

    Returns None if population is empty or singleton.

    See Also
    --------
    does_share_any_common_ancestor:
        Can we conclude with confidence_level confidence that the population
        shares a common ancestor?
    """
    pop_tee1, pop_tee2 = it.tee(population)
    if len([*zip(pop_tee1, range(2))]) < 2:
        warnings.warn(
            "Empty or singleton population. Unable to detect if does "
            "definitively share no common ancestor."
        )
        return None

    num_unique_rank_0_differentia = len(
        {
            (
                # note: columns guaranteed never empty
                next(column.IterRetainedDifferentia()),
                column.GetStratumDifferentiaBitWidth(),
            )
            for column in pop_tee2
        }
    )

    return num_unique_rank_0_differentia > 1
