import typing

from ...frozen_instrumentation import HereditaryStratigraphicSpecimen
from ._iter_mutual_ranks import iter_mutual_ranks


def iter_ranks_of_retained_commonality_between(
    first: HereditaryStratigraphicSpecimen,
    second: HereditaryStratigraphicSpecimen,
) -> typing.Iterator[int]:
    """Iterate over ranks with matching strata between columns in ascending
    order."""
    for rank, comp in iter_mutual_ranks(first, second, compare=True):
        if comp:
            yield rank
        else:
            return
