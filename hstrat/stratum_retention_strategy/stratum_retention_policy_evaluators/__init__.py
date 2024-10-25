"""Functors to specify property policies should be parameterized for."""

from ..._auxiliary_lib import lazy_attach_stub

__getattr__, __dir__, __all__ = lazy_attach_stub(
    __name__, __file__, launder=True
)
del lazy_attach_stub
