"""Eagerly utilize fixed stratum storage capacity `size_curb` to minimize
recency-proportional MRCA uncertainty.

The curbed recency-proportional resolution policy ensures that retained stratum
count respects a user-specified size cap. Recency-proportional MRCA resolution
is provided at finest-possible granularity given space constraint with graceful
degradation of granularity occuring as deposition history grows.

This policy works by splicing together successively-sparser
`recency_proportional_resolution_algo` paramaterizations then --- after the
stratum retention count upper bound of the sparsest
`recency_proportional_resolution_algo` exceeds storage capacity --- a
permanently fixed parameterization of the `geometric_seq_nth root` algorithm.

While

    num_depositions < 2 ** (size_curb // 3) // 2,

`recency_proportional_resolution_algo` policies apply with resolution

    size_curb // ceil(log2(num_depisitons)) - 1.

For

    num_depisitons > 2 ** (size_curb // 3) // 2,

a `geometric_sequence_nth_root_algorithm` policy with degree

    (size_curb - 2) // 6

and interspersal 2 applies. To ensure availability of ranks required by the
`geometric_sequence_nth_root_algorithm`, the transition between algorithms
occurs exactly before recency-proportional resolution 1 would apply.

Because strata retained by each policy supersets
strata retained by all subsequent retention policies, uncertainty bounds for
all policies apply within their respective domains. (I.e., all strata expected
by each policy are available when that policy activates.)

Although the geometric sequence nth root algorithm also guarantees constant
space complexity with recency-proportional MRCA uncertainty, the curbed recency-
proportional algorithm makes fuller (i.e., more aggressive) use of available
space during early depositions.

The curbed recency-proportional algorithm also compares favorably to the
tapered geometric sequence nth root algorithm during early depositions.
Although the tapered nth root algorithm makes the fullest (i.e., most
aggressive) use of available space --- upper bound capacity is always perfectly
utilized --- the used space is less effective at minimizing worst-case recency-
proportional resolution than the curbed algorithm. (I.e., the tapered nth root
algorithm provides patchier, less systematic coverage.)

Notes
-----
Only size caps of eight strata and above are guaranteed respected.
(Initialization of smaller size caps will warn.)

See Also
--------
recency_proportional_resolution_algo:
    Provides log space complexity and recency-proportional strata spacing.
geom_seq_nth_root_algo:
    Provides constant space complexity and MRCA rank estimate uncertainty
    bounded under s * (1 - n^(-1/k)) where n is the number of strata deposited
    and s is the true number of ranks deposited since the MRCA.
geom_seq_nth_root_tapered_algo:
    Perfectly space-filling variant of geom_seq_nth_root_algo.
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
