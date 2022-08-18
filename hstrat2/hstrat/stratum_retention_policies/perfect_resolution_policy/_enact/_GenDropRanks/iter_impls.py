import typing

from .FromPredKeepRank import FromPredKeepRank
from .GenDropRanks import GenDropRanks


def iter_impls() -> typing.Iterator[typing.Type[typing.Callable]]:
    """Iterate over drop rank generator implementations for the perfect
    resolution policy.

    Useful for testing.
    """

    yield from (
        GenDropRanks,
        FromPredKeepRank,
    )
