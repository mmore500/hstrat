from ..._impl import (
    CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank as CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank_,
)


# must inherit rather than assign due to failure of attribute lookup when
# pickling otherwise
class CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank(
    CalcMrcaUncertaintyAbsUpperBoundAtPessimalRank_
):
    pass
