from ._IterRetainedRanks_ import IterRetainedRanksProduction


# must inherit rather than assign due to failure of attribute lookup when
# pickling otherwise
class IterRetainedRanks(IterRetainedRanksProduction):
    pass
