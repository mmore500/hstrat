"""Implementation for `GarbageCollectingPhyloTracker`."""

from ._discern_referenced_rows import _discern_referenced_rows

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "_discern_referenced_rows",
]
