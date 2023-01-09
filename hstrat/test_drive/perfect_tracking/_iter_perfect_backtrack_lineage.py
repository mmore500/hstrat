import typing

from ._PerfectBacktrackHandle import PerfectBacktrackHandle


def iter_perfect_backtrack_lineage(
    handle: PerfectBacktrackHandle,
) -> typing.Iterator[PerfectBacktrackHandle]:
    while True:
        yield handle

        if handle.parent is None:
            break
        else:
            handle = handle.parent
