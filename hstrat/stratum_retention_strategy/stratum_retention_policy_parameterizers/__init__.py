"""Functors to configure policies that satisfy evaluated requirements."""

from ..._auxiliary_lib import lazy_attach_stub

__getattr__, __dir__, __all__ = lazy_attach_stub(
    __name__, __file__, launder=True
)
del lazy_attach_stub
