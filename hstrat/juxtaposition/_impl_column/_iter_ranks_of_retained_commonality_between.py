import typing

from ...genome_instrumentation import HereditaryStratigraphicColumn
from ._iter_mutual_ranks import iter_mutual_ranks


def iter_ranks_of_retained_commonality_between(
    first: HereditaryStratigraphicColumn,
    second: HereditaryStratigraphicColumn,
    *,
    first_start_idx: int = 0,
    second_start_idx: int = 0,
) -> typing.Iterator[int]:
    """Iterate over ranks with matching strata between columns in ascending
    order."""
    for rank, comp in iter_mutual_ranks(
        first,
        second,
        compare=True,
        first_start_idx=first_start_idx,
        second_start_idx=second_start_idx,
    ):
        if comp:
            yield rank
        else:
            return
