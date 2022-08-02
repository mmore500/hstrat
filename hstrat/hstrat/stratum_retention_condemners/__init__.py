"""Functors that implement stratum retention policies by specifying
the set of strata ranks that should be pruned from a hereditary
stratigraphic column when the nth stratum is deposited."""

from .StratumRetentionCondemnerDepthProportionalResolution \
    import StratumRetentionCondemnerDepthProportionalResolution
from .StratumRetentionCondemnerFixedResolution \
    import StratumRetentionCondemnerFixedResolution
from .StratumRetentionCondemnerFromPredicate \
    import StratumRetentionCondemnerFromPredicate
from .StratumRetentionCondemnerGeomSeqNthRoot \
    import StratumRetentionCondemnerGeomSeqNthRoot
from .StratumRetentionCondemnerPerfectResolution \
    import StratumRetentionCondemnerPerfectResolution
from .StratumRetentionCondemnerNominalResolution \
    import StratumRetentionCondemnerNominalResolution
from .StratumRetentionCondemnerRecencyProportionalResolution \
    import StratumRetentionCondemnerRecencyProportionalResolution
from .StratumRetentionCondemnerTaperedDepthProportionalResolution \
    import StratumRetentionCondemnerTaperedDepthProportionalResolution
from .StratumRetentionCondemnerTaperedGeomSeqNthRoot \
    import StratumRetentionCondemnerTaperedGeomSeqNthRoot

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    'StratumRetentionCondemnerDepthProportionalResolution',
    'StratumRetentionCondemnerFixedResolution',
    'StratumRetentionCondemnerFromPredicate',
    'StratumRetentionCondemnerGeomSeqNthRoot',
    'StratumRetentionCondemnerPerfectResolution',
    'StratumRetentionCondemnerNominalResolution',
    'StratumRetentionCondemnerRecencyProportionalResolution',
    'StratumRetentionCondemnerTaperedDepthProportionalResolution',
    'StratumRetentionCondemnerTaperedGeomSeqNthRoot',
]
