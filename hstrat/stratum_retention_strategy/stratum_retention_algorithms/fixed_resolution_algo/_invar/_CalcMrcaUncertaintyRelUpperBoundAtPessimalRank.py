from ..._impl import (
    CalcMrcaUncertaintyRelUpperBoundAtPessimalRank as CalcMrcaUncertaintyRelUpperBoundAtPessimalRank_,
)


# must inherit rather than assign due to failure of attribute lookup when
# pickling otherwise
class CalcMrcaUncertaintyRelUpperBoundAtPessimalRank(
    CalcMrcaUncertaintyRelUpperBoundAtPessimalRank_
):
    pass
