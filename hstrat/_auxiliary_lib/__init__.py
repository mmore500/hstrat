from ._AnyTreeAscendingIter import AnyTreeAscendingIter
from ._RecursionLimit import RecursionLimit
from ._ScalarFormatterFixedPrecision import ScalarFormatterFixedPrecision
from ._all_same import all_same
from ._bit_ceil import bit_ceil
from ._bit_floor import bit_floor
from ._caretdown_marker import caretdown_marker
from ._caretup_marker import caretup_marker
from ._div_range import div_range
from ._find_bounds import find_bounds
from ._is_nondecreasing import is_nondecreasing
from ._is_nonincreasing import is_nonincreasing
from ._launder_impl_modules import launder_impl_modules
from ._memoize_generator import memoize_generator
from ._pairwise import pairwise
from ._popcount import popcount
from ._release_cur_mpl_fig import release_cur_mpl_fig
from ._scale_luminosity import scale_luminosity

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    "all_same",
    "AnyTreeAscendingIter",
    "bit_ceil",
    "bit_floor",
    "caretdown_marker",
    "caretup_marker",
    "div_range",
    "find_bounds",
    "is_nondecreasing",
    "is_nonincreasing",
    "launder_impl_modules",
    "memoize_generator",
    "pairwise",
    "popcount",
    "RecursionLimit",
    "release_cur_mpl_fig",
    "scale_luminosity",
    "ScalarFormatterFixedPrecision",
]

for o in __all__:
    try:
        eval(o).__module__ = __name__
    except (AttributeError, TypeError):
        pass
