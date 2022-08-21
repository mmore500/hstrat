"""Accept linear size complexity to maintain fixed spacing between strata.

The fixed resolution policy ensures estimates of MRCA rank will have
uncertainty bounds less than or equal a fixed, absolute user-specified cap
that is independent of the number of strata deposited on either column.
Thus, MRCA rank estimate uncertainty scales as O(1) with respect to the
greater number of strata deposited on either column.

Under the fixed resolution policy, the number of strata retained (i.e.,
space complexity) scales as O(n) with respect to the number of strata
deposited.
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
