from ..._impl import CalcMrcaUncertaintyRelExactFromAbs


# must inherit rather than assign due to failure of attribute lookup when
# pickling otherwise
class CalcMrcaUncertaintyRelExact(CalcMrcaUncertaintyRelExactFromAbs):
    pass
