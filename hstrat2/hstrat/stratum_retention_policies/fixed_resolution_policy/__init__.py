"""The fixed resolution policy ensures estimates of MRCA rank will have
uncertainty bounds less than or equal a fixed, absolute user-specified cap
that is independent of the number of strata deposited on either column.
Thus, MRCA rank estimate uncertainty scales as O(1) with respect to the
greater number of strata deposited on either column.

Under the fixed resolution policy, the number of strata retained (i.e.,
space complexity) scales as O(n) with respect to the number of strata
deposited.
"""

from .PolicySpec import PolicySpec

from ._enact.GenDropRanks import GenDropRanks
from ._enact import _GenDropRanks

from ._invar.CalcMrcaUncertaintyAbsUpperBound \
    import CalcMrcaUncertaintyAbsUpperBound
from ._invar.CalcMrcaUncertaintyAbsUpperBoundPessimalRank \
    import CalcMrcaUncertaintyAbsUpperBoundPessimalRank
from ._invar.CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank \
    import CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank
from ._invar.CalcMrcaUncertaintyRelUpperBound \
    import CalcMrcaUncertaintyRelUpperBound
from ._invar.CalcMrcaUncertaintyRelUpperBoundPessimalRank \
    import CalcMrcaUncertaintyRelUpperBoundPessimalRank
from ._invar.CalcNumStrataRetainedUpperBound \
    import CalcNumStrataRetainedUpperBound

from ._scry.CalcMrcaUncertaintyAbsExact import CalcMrcaUncertaintyAbsExact
from ._scry.CalcMrcaUncertaintyRelExact import CalcMrcaUncertaintyRelExact
from ._scry.CalcNumStrataRetainedExact import CalcNumStrataRetainedExact
from ._scry.CalcRankAtColumnIndex import CalcRankAtColumnIndex
from ._scry.IterRetainedRanks import IterRetainedRanks

from .Policy import Policy
