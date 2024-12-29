"""Top-level package for hstrat."""

__author__ = "Matthew Andres Moreno"
__email__ = "m.more500@gmail.com"
__version__ = "1.15.3"


from ._auxiliary_lib import lazy_attach_stub

__getattr__, __dir__, __all__ = lazy_attach_stub(
    __name__,
    __file__,
    should_launder=[].__contains__,
)
del lazy_attach_stub
