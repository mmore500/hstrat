"""Classes to specify prior expectation for the distribution of MRCA generation
between hereditary stratigraphic columns, to assist in estimating the
phylogenetic relationship of hereditary stratigraphic columns."""

from ._ArbitraryPrior import ArbitraryPrior
from ._ExponentialPrior import ExponentialPrior
from ._GeometricPrior import GeometricPrior
from ._UniformPrior import UniformPrior

__all__ = [
    "ArbitraryPrior",
    "GeometricPrior",
    "ExponentialPrior",
    "UniformPrior",
]

from ..._auxiliary_lib import launder_impl_modules as _launder

_launder([eval(item) for item in __all__], __name__)
del _launder  # prevent name from leaking
