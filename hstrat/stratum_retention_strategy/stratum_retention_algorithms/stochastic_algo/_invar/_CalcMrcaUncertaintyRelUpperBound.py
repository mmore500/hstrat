from ..._impl import CalcMrcaUncertaintyRelUpperBoundWorstCase


# must inherit rather than assign due to failure of attribute lookup when
# pickling otherwise
class CalcMrcaUncertaintyRelUpperBound(
    CalcMrcaUncertaintyRelUpperBoundWorstCase
):
    pass
