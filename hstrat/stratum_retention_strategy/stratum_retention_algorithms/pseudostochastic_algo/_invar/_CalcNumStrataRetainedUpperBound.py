from ..._impl import CalcNumStrataRetainedUpperBoundWorstCase


# must inherit rather than assign due to failure of attribute lookup when
# pickling otherwise
class CalcNumStrataRetainedUpperBound(
    CalcNumStrataRetainedUpperBoundWorstCase
):
    pass
