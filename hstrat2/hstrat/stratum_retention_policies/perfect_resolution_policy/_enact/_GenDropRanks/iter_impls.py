from .GenDropRanks import GenDropRanks
from .FromPredKeepRank import FromPredKeepRank

def iter_impls():
    yield from (
        GenDropRanks,
        FromPredKeepRank,
    )
