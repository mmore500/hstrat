import typing

from ._PerfectBacktrackHandle import PerfectBacktrackHandle


def iter_perfect_backtrack_lineage(
    handle: PerfectBacktrackHandle,
) -> typing.Iterator[PerfectBacktrackHandle]:
    """Iterate up `PerfectBacktrackHandle` breadcrumbs for line of descent
    ending in `handle`, including `handle`."""
    while True:
        yield handle

        if handle.parent is None:
            break
        else:
            handle = handle.parent
