import typing

from .GenDropRanks import GenDropRanks
from .FromPredKeepRank import FromPredKeepRank


def iter_impls() -> typing.Iterator[typing.Type[typing.Callable]]:
    """Iterate over drop rank generator implementations for the
    depth-proportional resolution policy.

    Useful for testing.
    """

    yield from (
        GenDropRanks,
        FromPredKeepRank,
    )
