"""Containers for use with HereditaryStratigraphicColumn to store deposited
strata."""

from .HereditaryStratumOrderedStoreDict \
    import HereditaryStratumOrderedStoreDict
from .HereditaryStratumOrderedStoreList \
    import HereditaryStratumOrderedStoreList
from .HereditaryStratumOrderedStoreTree \
    import HereditaryStratumOrderedStoreTree

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    'HereditaryStratumOrderedStoreDict',
    'HereditaryStratumOrderedStoreList',
    'HereditaryStratumOrderedStoreTree',
]
