"""Functors to specify property policies should be parameterized for."""

from ._MrcaUncertaintyAbsExactEvaluator import MrcaUncertaintyAbsExactEvaluator
from ._MrcaUncertaintyAbsUpperBoundEvaluator import (
    MrcaUncertaintyAbsUpperBoundEvaluator,
)
from ._MrcaUncertaintyRelExactEvaluator import MrcaUncertaintyRelExactEvaluator
from ._MrcaUncertaintyRelUpperBoundEvaluator import (
    MrcaUncertaintyRelUpperBoundEvaluator,
)
from ._NumStrataRetainedExactEvaluator import NumStrataRetainedExactEvaluator
from ._NumStrataRetainedUpperBoundEvaluator import (
    NumStrataRetainedUpperBoundEvaluator,
)

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "MrcaUncertaintyAbsExactEvaluator",
    "MrcaUncertaintyAbsUpperBoundEvaluator",
    "MrcaUncertaintyRelExactEvaluator",
    "MrcaUncertaintyRelUpperBoundEvaluator",
    "NumStrataRetainedExactEvaluator",
    "NumStrataRetainedUpperBoundEvaluator",
]

from ..._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
