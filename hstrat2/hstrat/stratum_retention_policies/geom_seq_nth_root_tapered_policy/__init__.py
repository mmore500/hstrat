"""The exactly space-filling MRCA-recency-proportional resolution policy
imposes an O(1) limit on the number of retained strata and guarantees that
retained strata will be exponentially distributed with respect to ranks elapsed
since their deposit. MRCA rank estimate uncertainty scales in the worst case
scales as O(n) with respect to the greater number of strata deposited on either
column. However, with respect to estimating the rank of the MRCA when lineages
diverged any fixed number of generations ago, uncertainty scales as O(log(n))
(TODO check this).

Under the MRCA-recency-proportional resolution policy, the number of strata
retained (i.e., space complexity) scales as O(1) with respect to the number of
strata deposited.

Suppose k is specified as the policy's target space utilization. All strata
will be retained until an upper a hard upper limit of 4k + 2 is reached. Then,
the number of strata is mainained exactly at this hard upper limit perpetually.
MRCA rank estimate uncertainty is maintained less than or equal to s * (1 - n^(-1/k)) where n is the number of strata deposited and s is the true number of ranks deposited since the MRCA.

See Also
--------
geom_seq_nth_root_policy:
    For a predicate retention policy that achieves the same guarantees for
    resolution and space complexity but fluctuates in size below an upper
    size bound instead of remaining exactly at the size bound. Likely faster
    than tapered_geom_seq_nth_root_policy for most operations.
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
