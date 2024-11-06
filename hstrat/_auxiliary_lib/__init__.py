from ._lazy_attach_stub import lazy_attach_stub

__getattr__, __dir__, __all__ = lazy_attach_stub(__name__, __file__)
del lazy_attach_stub
