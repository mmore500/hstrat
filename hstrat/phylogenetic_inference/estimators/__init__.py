"""Tools to estimate MRCA generation from shared ranks of commonality and
disparity."""

from ..._auxiliary_lib import lazy_attach_stub

__getattr__, __dir__, __all__ = lazy_attach_stub(
    __name__, __file__, should_launder=lambda _: False
)
del lazy_attach_stub
