"""The nominal resolution policy only retains the most ancient (i.e., very
first) and most recent (i.e., last) strata. So, comparisons between two
columns under this policy will only be able to detect whether they share
any common ancestor and whether they are from the same organism (i.e., no
generations have elapsed since the MRCA). Thus, MRCA rank estimate
uncertainty scales as O(n) with respect to the greater number of strata deposited on either column.

Under the nominal resolution policy, the number of strata retained (i.e.,
space complexity) scales as O(1) with respect to the number of strata
deposited.
"""

from .Policy import Policy
from .PolicySpec import PolicySpec
from ._enact.GenDropRanks import GenDropRanks
from ._enact._GenDropRanks import impls as GenDropRanks_impls
from ._invar.CalcMrcaUncertaintyAbsUpperBound import (
    CalcMrcaUncertaintyAbsUpperBound,
)
from ._invar.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank import (
    CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank,
)
from ._invar.CalcMrcaUncertaintyAbsUpperBoundPessimalRank import (
    CalcMrcaUncertaintyAbsUpperBoundPessimalRank,
)
from ._invar.CalcMrcaUncertaintyRelUpperBound import (
    CalcMrcaUncertaintyRelUpperBound,
)
from ._invar.CalcMrcaUncertaintyRelUpperBoundAtPessimalRank import (
    CalcMrcaUncertaintyRelUpperBoundAtPessimalRank,
)
from ._invar.CalcMrcaUncertaintyRelUpperBoundPessimalRank import (
    CalcMrcaUncertaintyRelUpperBoundPessimalRank,
)
from ._invar.CalcNumStrataRetainedUpperBound import (
    CalcNumStrataRetainedUpperBound,
)
from ._scry.CalcMrcaUncertaintyAbsExact import CalcMrcaUncertaintyAbsExact
from ._scry.CalcMrcaUncertaintyRelExact import CalcMrcaUncertaintyRelExact
from ._scry.CalcNumStrataRetainedExact import CalcNumStrataRetainedExact
from ._scry.CalcRankAtColumnIndex import CalcRankAtColumnIndex
from ._scry.IterRetainedRanks import IterRetainedRanks

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
    "GenDropRanks_impls",
    "IterRetainedRanks",
    "Policy",
    "PolicySpec",
]
