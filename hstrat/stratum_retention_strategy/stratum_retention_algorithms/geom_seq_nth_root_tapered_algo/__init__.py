"""Maintain constant size complexity with recency-proportional strata spacing.

The exactly space-filling MRCA-recency-proportional resolution policy
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
geom_seq_nth_root_algo:
    For a predicate retention policy that achieves the same guarantees for
    resolution and space complexity but fluctuates in size below an upper
    size bound instead of remaining exactly at the size bound. Likely faster
    than tapered_geom_seq_nth_root_algo for most operations.
"""

from ._Policy import Policy
from ._PolicySpec import PolicySpec
from ._enact._GenDropRanks import GenDropRanks
from ._enact._GenDropRanks_ import impls as _GenDropRanks_impls
from ._invar._CalcMrcaUncertaintyAbsUpperBound import (
    CalcMrcaUncertaintyAbsUpperBound,
)
from ._invar._CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank import (
    CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank,
)
from ._invar._CalcMrcaUncertaintyAbsUpperBoundPessimalRank import (
    CalcMrcaUncertaintyAbsUpperBoundPessimalRank,
)
from ._invar._CalcMrcaUncertaintyRelUpperBound import (
    CalcMrcaUncertaintyRelUpperBound,
)
from ._invar._CalcMrcaUncertaintyRelUpperBoundAtPessimalRank import (
    CalcMrcaUncertaintyRelUpperBoundAtPessimalRank,
)
from ._invar._CalcMrcaUncertaintyRelUpperBoundPessimalRank import (
    CalcMrcaUncertaintyRelUpperBoundPessimalRank,
)
from ._invar._CalcNumStrataRetainedUpperBound import (
    CalcNumStrataRetainedUpperBound,
)
from ._scry._CalcMrcaUncertaintyAbsExact import CalcMrcaUncertaintyAbsExact
from ._scry._CalcMrcaUncertaintyRelExact import CalcMrcaUncertaintyRelExact
from ._scry._CalcNumStrataRetainedExact import CalcNumStrataRetainedExact
from ._scry._CalcRankAtColumnIndex import CalcRankAtColumnIndex
from ._scry._IterRetainedRanks import IterRetainedRanks

__all__ = [
    "CalcMrcaUncertaintyAbsExact",
    "CalcMrcaUncertaintyAbsUpperBound",
    "CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank",
    "CalcMrcaUncertaintyAbsUpperBoundPessimalRank",
    "CalcMrcaUncertaintyRelExact",
    "CalcMrcaUncertaintyRelUpperBound",
    "CalcMrcaUncertaintyRelUpperBoundAtPessimalRank",
    "CalcMrcaUncertaintyRelUpperBoundPessimalRank",
    "CalcNumStrataRetainedExact",
    "CalcNumStrataRetainedUpperBound",
    "CalcRankAtColumnIndex",
    "GenDropRanks",
    "_GenDropRanks_impls",
    "IterRetainedRanks",
    "Policy",
    "PolicySpec",
]

from ...._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
