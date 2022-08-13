"""The tapered depth-proportional resolution policy ensures estimates of MRCA
rank will have uncertainty bounds less than or equal to a user-specified
proportion of the largest number of strata deposited on either column. Thus,
MRCA rank estimate uncertainty scales as O(n) with respect to the greater
number of strata deposited on either column.

Under the tapered depth-proportional resolution policy, the number of strata
retained (i.e., space complexity) scales as O(1) with respect to the number of
strata deposited.

This functor's retention policy implementation guarantees that columns will
retain appropriate strata so that for any two columns with m and n strata
deposited, the rank of the most recent common ancestor can be determined with
uncertainty of at most

    bound = floor(max(m, n) / guaranteed_depth_proportional_resolution)

ranks. Achieving this limit on uncertainty requires retaining sufficient strata
so that no more than bound ranks elapsed between any two strata. This policy
accumulates retained strata at a fixed interval until twice as many as
guaranteed_depth_proportional_resolution are at hand. Then, every other
retained stratum is purged gradually from back to front until the cycle repeats
with a new twice-as-wide interval between retained strata.

See Also
--------
StratumRetentionPredicateDepthProportionalResolution:
    For a predicate retention policy that achieves the same guarantees for
    tapered depth-proportional resolution but purges unnecessary strata more
    aggressively and abruptly.
"""

from .PolicySpec import PolicySpec

from ._enact.GenDropRanks import GenDropRanks
from ._enact import _GenDropRanks

from ._invar.CalcMrcaUncertaintyAbsUpperBound \
    import CalcMrcaUncertaintyAbsUpperBound
from ._invar.CalcMrcaUncertaintyRelUpperBound \
    import CalcMrcaUncertaintyRelUpperBound
from ._invar.CalcNumStrataRetainedUpperBound \
    import CalcNumStrataRetainedUpperBound

from ._scry.CalcMrcaUncertaintyAbsExact import CalcMrcaUncertaintyAbsExact
from ._scry.CalcMrcaUncertaintyRelExact import CalcMrcaUncertaintyRelExact
from ._scry.CalcNumStrataRetainedExact import CalcNumStrataRetainedExact
from ._scry.CalcRankAtColumnIndex import CalcRankAtColumnIndex
from ._scry.IterRetainedRanks import IterRetainedRanks

from .Policy import Policy
