import typing

from ..genome_instrumentation import HereditaryStratigraphicColumn


def diff_retained_ranks(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
) -> typing.Tuple[typing.Set[int], typing.Set[int]]:
    """Return ranks retained by self but not other, and vice versa.

    Returned as a tuple of sets.
    """
    self_ranks = set(self.IterRetainedRanks())
    other_ranks = set(other.IterRetainedRanks())

    return (
        self_ranks - other_ranks,
        other_ranks - self_ranks,
    )
