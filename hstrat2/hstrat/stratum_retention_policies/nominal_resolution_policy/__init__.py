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

from .PolicySpec import PolicySpec

from ._enact.GenDropRanks import GenDropRanks
from ._enact import _GenDropRanks

from ._invar.CalcMrcaUncertaintyAbsUpperBound \
    import CalcMrcaUncertaintyAbsUpperBound
from ._invar.CalcNumStrataRetainedUpperBound \
    import CalcNumStrataRetainedUpperBound

from ._scry.CalcMrcaUncertaintyAbsExact import CalcMrcaUncertaintyAbsExact
from ._scry.CalcMrcaUncertaintyRelExact import CalcMrcaUncertaintyRelExact
from ._scry.CalcNumStrataRetainedExact import CalcNumStrataRetainedExact
from ._scry.CalcRankAtColumnIndex import CalcRankAtColumnIndex
from ._scry.IterRetainedRanks import IterRetainedRanks

from .Policy import Policy
