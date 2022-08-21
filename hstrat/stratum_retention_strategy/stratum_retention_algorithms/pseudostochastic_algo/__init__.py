"""Retains strata probabilistically.

It would be a poor choice to use in practice because mismatches between the
particular ranks that each column happens to have strata for will degrade
the effectiveness of comparisons between columns. Rather, it is included in
the library as an edge case for testing purposes. Worst-case MRCA rank estimate uncertainty scales as O(n) with respect to the greater number of strata deposited on either column being compared.

Under the pseudostochastic resolution policy, the worst and average case number
of strata retained (i.e., space complexity) scales as O(n) with respect to
the number of strata deposited.

This policy implementation that the most ancient and most recent strata will
always be retained. For the secondmost recently deposited sratum, a
pseudorandom coin flip is performed. Depending on the outcome of that coin
flip, the stratum is either immediately purged or retained permanently.
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
