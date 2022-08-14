"""The pseudostochastic resolution policy retains strata probabilistically. It
would be a poor choice to use in practice because mismatches between the
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

from .PolicySpec import PolicySpec

from ._enact.GenDropRanks import GenDropRanks
from ._enact import _GenDropRanks

from ._invar.CalcMrcaUncertaintyAbsUpperBound \
    import CalcMrcaUncertaintyAbsUpperBound
from ._invar.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank \
    import CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank
from ._invar.CalcMrcaUncertaintyAbsUpperBoundPessimalRank \
    import CalcMrcaUncertaintyAbsUpperBoundPessimalRank
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
