from ..._impl import CalcMrcaUncertaintyAbsUpperBoundWorstCase


# must inherit rather than assign due to failure of attribute lookup when
# pickling otherwise
class CalcMrcaUncertaintyAbsUpperBound(
    CalcMrcaUncertaintyAbsUpperBoundWorstCase
):
    pass
