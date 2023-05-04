import typing

from .._auxiliary_lib import HereditaryStratigraphicArtifact


def diff_retained_ranks(
    first: HereditaryStratigraphicArtifact,
    second: HereditaryStratigraphicArtifact,
) -> typing.Tuple[typing.Set[int], typing.Set[int]]:
    """Return ranks retained by first but not second, and vice versa.

    Returned as a tuple of sets.
    """
    first_ranks = set(first.IterRetainedRanks())
    second_ranks = set(second.IterRetainedRanks())

    return (
        first_ranks - second_ranks,
        second_ranks - first_ranks,
    )
