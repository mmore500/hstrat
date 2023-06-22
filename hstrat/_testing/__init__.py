from ._ftor_shim import ftor_shim
from ._iter_ftor_shims import iter_ftor_shims
from ._iter_no_calcrank_ftor_shims import iter_no_calcrank_ftor_shims

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "ftor_shim",
    "iter_ftor_shims",
    "iter_no_calcrank_ftor_shims",
]

for o in __all__:
    try:
        eval(o).__module__ = __name__
    except AttributeError:
        pass
